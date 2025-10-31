"""Tkinter controller that bridges the view with the conversion service."""

from __future__ import annotations

import shutil
import threading
from pathlib import Path
from tkinter import filedialog

from bulktopdf.config import CONFIG
from bulktopdf.conversion import DocumentConverter
from bulktopdf.logging_utils import configure_logging
from bulktopdf.services import ConversionService

from .view import PDFConverterView

logger = configure_logging()


class PDFConverterController:
    """Handle UI events and delegate work to the conversion service."""

    def __init__(self, view: PDFConverterView | None) -> None:
        self.view = view
        self.input_dir: Path | None = None
        self._conversion_thread: threading.Thread | None = None
        converter = DocumentConverter(CONFIG.conversion)
        self.service = ConversionService(converter=converter, settings=CONFIG.conversion)
        self._last_summary = None
        self._copy_unsupported = CONFIG.conversion.copy_unsupported_by_default

    # ------------------------------------------------------------------ UI callbacks
    def browse_input(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.set_input_directory(path)

    def set_input_directory(self, directory: str) -> None:
        path = Path(directory).expanduser()
        if not path.exists() or not path.is_dir():
            self.view.display_error(f"Please choose a valid folder: {path}")
            return
        self.input_dir = path
        self.view.set_input_display(str(path))
        self.view.display_info("")
        self.view.show_download_ready(False)

    def start_conversion(self) -> None:
        if self.input_dir is None:
            self.view.display_error("Select a folder before converting.")
            return

        if self._conversion_thread and self._conversion_thread.is_alive():
            self.view.display_error("A conversion is already in progress.")
            return

        self.view.clear_errors()
        self.view.display_info("Converting...")
        self.view.reset_progress()
        self.view.convert_button.config(state="disabled")
        self.view.show_download_ready(False)
        self._copy_unsupported = self.view.should_copy_unsupported()

        self._conversion_thread = threading.Thread(
            target=self._run_conversion,
            args=(self.input_dir,),
            daemon=True,
        )
        self._conversion_thread.start()

    def download_converted(self) -> None:
        if not self._last_summary or not self._last_summary.zip_path:
            self.view.display_error("No converted archive available to download.")
            return

        destination = filedialog.asksaveasfilename(
            title="Save Converted Archive",
            initialfile=self._last_summary.zip_path.name,
            defaultextension=".zip",
            filetypes=[("Zip Archive", "*.zip")],
        )
        if not destination:
            return

        try:
            shutil.copy2(self._last_summary.zip_path, destination)
            self.view.reset_after_download()
        except OSError as exc:
            logger.exception("Unable to save zip file: %s", exc)
            self.view.display_error(f"Unable to save zip file: {exc}")

    # ------------------------------------------------------------------ Conversion orchestration
    def _run_conversion(self, input_dir: Path) -> None:
        try:
            summary = self.service.convert_directory(
                input_dir=input_dir,
                status_callback=self._dispatch_to_view(self.view.display_progress),
                error_callback=self._dispatch_to_view(self.view.record_conversion_error),
                progress_callback=self._dispatch_to_view(self.view.update_progress),
                copy_unsupported=self._copy_unsupported,
            )
            self._last_summary = summary
            self._dispatch_to_view(self._handle_summary)(summary)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error during conversion: ", exc_info=exc)
            self._dispatch_to_view(self.view.display_error)(f"Unexpected error: {exc}")
        finally:
            self._dispatch_to_view(self._finalize_ui)()

    def _handle_summary(self, summary) -> None:
        if summary.failed_files:
            message = f"Completed with errors. {summary.failed_files} file"
            if summary.failed_files != 1:
                message += "s"
            message += " failed."
            self.view.display_error(message)
        else:
            self.view.display_info("Conversion completed successfully.")
        self.view.show_download_ready(summary.succeeded_files > 0 and summary.zip_path is not None)

    def _finalize_ui(self) -> None:
        self.view.convert_button.config(state="normal")
        if self._last_summary:
            self.view.update_progress(self._last_summary.processed_files, self._last_summary.processed_files)

    def _dispatch_to_view(self, callback):
        def wrapper(*args, **kwargs):
            self.view.after(0, lambda: callback(*args, **kwargs))

        return wrapper
