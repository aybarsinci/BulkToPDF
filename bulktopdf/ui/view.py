"""Tkinter view for the BulkToPDF desktop application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from bulktopdf.config import CONFIG

try:  # Optional dependency for drag-and-drop.
    from tkinterdnd2 import DND_FILES  # type: ignore
except ImportError:  # pragma: no cover - used only when optional package installed.
    DND_FILES = None


class ControllerProtocol:
    """Protocol used only for static typing of the view."""

    def browse_input(self) -> None: ...

    def start_conversion(self) -> None: ...

    def download_converted(self) -> None: ...

    def set_input_directory(self, directory: str) -> None: ...


class PDFConverterView(tk.Frame):
    """Tkinter view responsible for rendering the BulkToPDF UI."""

    def __init__(self, master: tk.Widget, controller: ControllerProtocol):
        super().__init__(master)
        self.controller = controller
        self.dnd_supported = DND_FILES is not None and hasattr(master, "drop_target_register")
        self.selected_path = tk.StringVar(value="Drop a folder here or click Browse")
        self.copy_mode = tk.BooleanVar(value=CONFIG.conversion.copy_unsupported_by_default)
        self.config(padx=20, pady=20)
        self.columnconfigure(0, weight=1)
        self._build_widgets()

    # --------------------------------------------------------------------- UI construction
    def _build_widgets(self) -> None:
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11), padding=5)
        style.configure("DropFrame.TFrame", borderwidth=2, relief="ridge")

        ttk.Label(self, text="Input Folder").grid(row=0, column=0, sticky="w")

        self.drop_frame = ttk.Frame(self, style="DropFrame.TFrame", padding=20)
        self.drop_frame.grid(row=1, column=0, sticky="ew", pady=(10, 5))
        self.drop_frame.columnconfigure(0, weight=1)

        drop_label = ttk.Label(
            self.drop_frame,
            textvariable=self.selected_path,
            anchor="center",
            justify="center",
            wraplength=520,
        )
        drop_label.grid(row=0, column=0, sticky="ew")

        if self.dnd_supported:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind("<<Drop>>", self._on_drop)

        button_row = ttk.Frame(self)
        button_row.grid(row=2, column=0, sticky="ew", pady=(5, 15))
        for column in range(3):
            button_row.columnconfigure(column, weight=0)
        button_row.columnconfigure(3, weight=1)

        browse_button = ttk.Button(button_row, text="Browse...", command=self.controller.browse_input)
        browse_button.grid(row=0, column=0, padx=(0, 10))

        self.convert_button = ttk.Button(
            button_row,
            text="Convert",
            command=self.controller.start_conversion,
            state=tk.DISABLED,
        )
        self.convert_button.grid(row=0, column=1, padx=(0, 10))

        self.download_button = ttk.Button(
            button_row,
            text="Download Zip",
            command=self.controller.download_converted,
            state=tk.DISABLED,
        )
        self.download_button.grid(row=0, column=2)

        copy_checkbox = ttk.Checkbutton(
            button_row,
            text="Copy other files",
            variable=self.copy_mode,
        )
        copy_checkbox.grid(row=1, column=0, sticky="w", pady=(8, 0))

        info_label = ttk.Label(button_row, text="ⓘ", cursor="hand2", padding=(4, 0))
        info_label.grid(row=1, column=1, sticky="w", pady=(8, 0))
        self._attach_tooltip(
            info_label,
            "When enabled, files that are not Word/Excel/PDF will be copied into the output archive.",
        )

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.grid(row=3, column=0, sticky="ew", pady=(10, 5))
        self.progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(self.progress_frame, mode="determinate")
        self.progress.grid(row=0, column=0, sticky="ew")

        self.progress_label = ttk.Label(self.progress_frame, text="0% • 0/0 files")
        self.progress_label.grid(row=1, column=0, sticky="e", pady=(4, 0))

        self.status_box = ttk.LabelFrame(self, text="Status")
        self.status_box.grid(row=4, column=0, sticky="ew", pady=(5, 5))
        self.status_box.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(self.status_box, text="Ready.", font=("Arial", 11))
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=6)

        self.error_frame = ttk.LabelFrame(self, text="Errors", padding=(10, 10, 10, 10))
        self.error_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 20))
        self.rowconfigure(5, weight=1, minsize=200)
        self.error_frame.columnconfigure(0, weight=1)
        self.error_frame.rowconfigure(0, weight=1)

        self.error_text = tk.Text(
            self.error_frame,
            height=8,
            wrap="word",
            state=tk.DISABLED,
            font=("Arial", 10),
            relief="flat",
            bg=self.cget("background"),
        )
        self.error_text.grid(row=0, column=0, sticky="nsew")

        status_scrollbar = ttk.Scrollbar(self.error_frame, orient="vertical", command=self.error_text.yview)
        status_scrollbar.grid(row=0, column=1, sticky="ns")
        self.error_text.configure(yscrollcommand=status_scrollbar.set)

        self.download_button.grid_remove()
        self.error_count = 0
        self._update_error_header()
        self._tooltip_window: tk.Toplevel | None = None

    # --------------------------------------------------------------------- Controller API
    def set_input_display(self, path: str) -> None:
        display_text = path if path else "Drop a folder here or click Browse"
        self.selected_path.set(display_text)
        self.convert_button.config(state=tk.NORMAL if path else tk.DISABLED)

    def display_info(self, message: str) -> None:
        self._set_status(message, is_error=False)

    def display_error(self, message: str) -> None:
        self._set_status(message, is_error=True)

    def display_progress(self, message: str) -> None:
        self._set_status(message, is_error=False)

    def update_progress(self, current: int, total: int) -> None:
        total = max(total, 1)
        current = min(current, total)
        self.progress.configure(maximum=total, value=current)
        percent = int((current / total) * 100)
        self.progress_label.config(text=f"{percent}% • {current}/{total} files")

    def reset_progress(self) -> None:
        self.progress.configure(value=0)
        self.progress_label.config(text="0% • 0/0 files")

    def show_download_ready(self, zip_available: bool) -> None:
        if zip_available:
            self.download_button.grid()
            self.download_button.config(state=tk.NORMAL)
        else:
            self.download_button.config(state=tk.DISABLED)
            self.download_button.grid_remove()

    def reset_after_download(self) -> None:
        self.download_button.config(state=tk.DISABLED)
        self.display_info("Zip saved successfully.")
        self.download_button.grid_remove()

    def should_copy_unsupported(self) -> bool:
        return bool(self.copy_mode.get())

    def clear_errors(self) -> None:
        self.error_text.configure(state=tk.NORMAL)
        self.error_text.delete("1.0", tk.END)
        self.error_text.configure(state=tk.DISABLED)
        self.error_count = 0
        self._update_error_header()

    def record_conversion_error(self, message: str) -> None:
        self._set_status(message, is_error=True)
        self._append_error(message)

    # --------------------------------------------------------------------- Internal helpers
    def _set_status(self, message: str, is_error: bool) -> None:
        foreground = "#FF6B6B" if is_error else "#FFFFFF"
        self.status_label.config(text=message, foreground=foreground)

    def _append_error(self, message: str) -> None:
        self.error_text.configure(state=tk.NORMAL)
        if self.error_text.index("end-1c") != "1.0":
            self.error_text.insert(tk.END, "\n")
        self.error_count += 1
        self._update_error_header()
        self.error_text.insert(tk.END, f"[{self.error_count}] {message}")
        self.error_text.see(tk.END)
        self.error_text.configure(state=tk.DISABLED)

    def _update_error_header(self) -> None:
        if self.error_count:
            self.error_frame.config(text=f"Errors ({self.error_count})")
        else:
            self.error_frame.config(text="Errors")

    # --------------------------------------------------------------------- Drag-and-drop
    def _on_drop(self, event: tk.Event) -> None:  # type: ignore[override]
        paths = self._split_dnd_event(event.data)
        if paths:
            self.controller.set_input_directory(paths[0])

    @staticmethod
    def _split_dnd_event(data: str | None) -> list[str]:
        if not data:
            return []
        result: list[str] = []
        current = ""
        in_braces = False
        for char in data:
            if char == "{":
                in_braces = True
                current = ""
            elif char == "}":
                in_braces = False
                result.append(current)
                current = ""
            elif char == " " and not in_braces:
                if current:
                    result.append(current)
                    current = ""
            else:
                current += char
        if current:
            result.append(current)
        return result

    # --------------------------------------------------------------------- Tooltip helper
    def _attach_tooltip(self, widget: ttk.Widget, text: str) -> None:
        def on_enter(event):  # noqa: ANN001
            if self._tooltip_window is not None:
                return
            self._tooltip_window = tk.Toplevel(self)
            self._tooltip_window.wm_overrideredirect(True)
            self._tooltip_window.attributes("-topmost", True)
            label = ttk.Label(
                self._tooltip_window,
                text=text,
                background="#FFFFE0",
                relief="solid",
                borderwidth=1,
                padding=5,
                wraplength=260,
            )
            label.pack()
            x = event.x_root + 10
            y = event.y_root + 10
            self._tooltip_window.wm_geometry(f"+{x}+{y}")

        def on_leave(_event):  # noqa: ANN001
            if self._tooltip_window is not None:
                self._tooltip_window.destroy()
                self._tooltip_window = None

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
