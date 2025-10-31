"""High-level document converter that chooses appropriate backend per platform."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from bulktopdf.config import ConversionSettings
from bulktopdf.logging_utils import configure_logging

from .libreoffice import convert_with_libreoffice
from .win_comtypes import convert_with_comtypes

logger = configure_logging()


class ConversionError(RuntimeError):
    """Raised when a document cannot be converted."""


@dataclass(slots=True)
class DocumentConverter:
    """Convert documents to PDF using platform-specific backends."""

    settings: ConversionSettings

    def convert(
        self,
        source: Path,
        destination_root: Path,
        relative_path: Path,
        copy_unsupported: bool = False,
    ) -> None:
        """Convert ``source`` to a PDF stored under ``destination_root``."""
        normalized_source = Path(unquote(str(source))).resolve()
        extension = normalized_source.suffix.lower()

        if normalized_source.name in self.settings.excluded_filenames:
            logger.debug("Skipping excluded filename %s", normalized_source)
            return

        if normalized_source.name.startswith(self.settings.excluded_prefixes):
            logger.debug("Skipping temporary system file %s", normalized_source)
            return

        is_supported = extension in self.settings.supported_extensions

        if not is_supported and not copy_unsupported:
            logger.debug("Skipping unsupported file %s", normalized_source)
            return

        destination_suffix = ".pdf" if extension in self.settings.supported_extensions else extension
        destination = destination_root / relative_path.with_suffix(destination_suffix)
        destination.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Converting %s", normalized_source)

        if extension in self.settings.passthrough_extensions or (copy_unsupported and not is_supported):
            try:
                shutil.copy2(normalized_source, destination)
            except OSError as exc:  # noqa: BLE001
                raise ConversionError(f"Failed to copy PDF {normalized_source}: {exc}") from exc
            return

        try:
            if sys.platform.startswith("win"):
                convert_with_comtypes(normalized_source, destination)
            else:
                convert_with_libreoffice(
                    normalized_source,
                    destination,
                    self.settings.libreoffice_timeout_seconds,
                )
        except Exception as exc:  # noqa: BLE001
            raise ConversionError(f"Conversion failed for {normalized_source}: {exc}") from exc

        if is_supported and not destination.exists():
            raise ConversionError(f"Expected output file missing: {destination}")
