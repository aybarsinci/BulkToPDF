"""Application-wide logging configuration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def configure_logging(log_path: Optional[Path] = None) -> logging.Logger:
    """Configure and return the shared application logger."""
    logger = logging.getLogger("bulktopdf")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


__all__ = ["configure_logging"]

