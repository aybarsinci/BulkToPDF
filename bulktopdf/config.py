"""Static configuration for the BulkToPDF application."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ConversionSettings:
    """Settings that control the conversion pipeline."""

    supported_office_extensions: tuple[str, ...] = (".doc", ".docx", ".xls", ".xlsx")
    passthrough_extensions: tuple[str, ...] = (".pdf",)
    temporary_file_prefix: str = "bulktopdf_converted_"
    libreoffice_timeout_seconds: int = 150  # 2.5 minutes
    max_workers: int = 3  # Upper bound for concurrent conversions
    copy_unsupported_by_default: bool = False
    excluded_filenames: tuple[str, ...] = (".DS_Store", "Thumbs.db", "desktop.ini")
    excluded_prefixes: tuple[str, ...] = ("~$", "._")

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return self.supported_office_extensions + self.passthrough_extensions


@dataclass(frozen=True, slots=True)
class UISettings:
    """Settings that control basic UI behaviour."""

    window_width: int = 600
    window_height: int = 480
    title: str = "PDF Converter"


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Aggregate application configuration."""

    conversion: ConversionSettings = ConversionSettings()
    ui: UISettings = UISettings()
    logs_dir: Path = Path("logs")


CONFIG = AppConfig()
