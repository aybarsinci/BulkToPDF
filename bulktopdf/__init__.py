"""BulkToPDF application package."""

from importlib import metadata


def get_version() -> str:
    """Return the installed package version if available."""
    try:
        return metadata.version("bulktopdf")
    except metadata.PackageNotFoundError:
        return "0.0.0-dev"


__all__ = ["get_version"]

