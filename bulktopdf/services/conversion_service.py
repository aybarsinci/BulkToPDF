"""Service layer that orchestrates directory conversions."""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
from zipfile import ZipFile, ZIP_DEFLATED

from bulktopdf.config import ConversionSettings
from bulktopdf.conversion import DocumentConverter, ConversionError
from bulktopdf.logging_utils import configure_logging

StatusCallback = Callable[[str], None]
ErrorCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int], None]

logger = configure_logging()


@dataclass(slots=True)
class ConversionSummary:
    processed_files: int
    failed_files: int
    errors: list[str]
    zip_path: Path | None

    @property
    def succeeded_files(self) -> int:
        return self.processed_files - self.failed_files


@dataclass(slots=True)
class ConversionService:
    """Convert directories of documents using the provided converter."""

    converter: DocumentConverter
    settings: ConversionSettings

    def convert_directory(
        self,
        input_dir: Path,
        status_callback: StatusCallback,
        error_callback: ErrorCallback,
        progress_callback: ProgressCallback,
        *,
        copy_unsupported: bool = False,
    ) -> ConversionSummary:
        input_dir = input_dir.resolve()
        if not input_dir.exists() or not input_dir.is_dir():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        temp_dir = Path(tempfile.mkdtemp(prefix=self.settings.temporary_file_prefix))
        errors: list[str] = []
        failed = 0
        processed = 0

        try:
            entries = list(self._iter_files(input_dir, include_unsupported=copy_unsupported))
            total = len(entries)
            if not total:
                raise ValueError("No convertible files were found in the selected folder.")

            for source, relative_path, is_supported in entries:
                status_callback(f"Converting: {relative_path}")
                logger.debug("Processing %s", source)
                try:
                    self.converter.convert(
                        source,
                        temp_dir,
                        relative_path,
                        copy_unsupported=copy_unsupported,
                    )
                except (ConversionError, RuntimeError, OSError) as exc:
                    failed += 1
                    rel_str = str(relative_path)
                    errors.append(rel_str)
                    error_callback(rel_str)
                    logger.warning("Failed to convert %s: %s", source, exc)
                finally:
                    processed += 1
                    progress_callback(processed, total)

            zip_path = self._create_zip_from_temp(temp_dir, input_dir) if (processed - failed) else None
            return ConversionSummary(processed_files=processed, failed_files=failed, errors=errors, zip_path=zip_path)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _iter_files(
        self,
        input_dir: Path,
        *,
        include_unsupported: bool = False,
    ) -> Iterable[tuple[Path, Path, bool]]:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file in self.settings.excluded_filenames:
                    continue
                if file.startswith(self.settings.excluded_prefixes):
                    continue
                extension = Path(file).suffix.lower()
                is_supported = extension in self.settings.supported_extensions
                if not is_supported and not include_unsupported:
                    continue
                absolute = Path(root, file)
                relative = absolute.relative_to(input_dir)
                yield absolute, relative, is_supported

    @staticmethod
    def _create_zip_from_temp(temp_dir: Path, input_dir: Path) -> Path:
        fd, zip_filepath = tempfile.mkstemp(prefix=f"{input_dir.name}_", suffix=".zip")
        os.close(fd)
        zip_path = Path(zip_filepath)
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zip_file:
            for file in temp_dir.rglob("*"):
                if file.is_file():
                    arcname = file.relative_to(temp_dir)
                    zip_file.write(file, arcname)
        logger.info("Created archive %s", zip_path)
        return zip_path
