"""LibreOffice-based conversion backend."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from bulktopdf.logging_utils import configure_logging

logger = configure_logging()
_LIBREOFFICE_LOCK = threading.Lock()


def convert_with_libreoffice(source: Path, destination: Path, timeout_seconds: int) -> None:
    with _LIBREOFFICE_LOCK:
        soffice_path = _get_soffice_path()
        if not soffice_path:
            raise RuntimeError(
                "LibreOffice `soffice` binary not found. Install LibreOffice and ensure it is "
                "available via PATH or located at /Applications/LibreOffice.app/Contents/MacOS/soffice."
            )

        profile_dir = Path(tempfile.mkdtemp(prefix="bulktopdf_lo_profile_"))
        user_profile_arg = f"-env:UserInstallation={profile_dir.as_uri()}"

        filter_arg = _resolve_filter_argument(source.suffix.lower())

        command = [
            soffice_path,
            "--headless",
            "--nologo",
            "--nodefault",
            "--norestore",
            "--nofirststartwizard",
            "--invisible",
            user_profile_arg,
            "--convert-to",
            filter_arg,
            "--outdir",
            str(destination.parent),
            str(source),
        ]

        logger.debug("Running LibreOffice command: %s", " ".join(command))

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:  # noqa: BLE001
            raise RuntimeError(
                f"LibreOffice conversion timed out for {source}. Launch LibreOffice GUI once to "
                "complete first-run setup, or increase the timeout."
            ) from exc
        finally:
            shutil.rmtree(profile_dir, ignore_errors=True)
            _ensure_libreoffice_quits()

        if result.returncode != 0:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            raise RuntimeError(stderr or stdout or "LibreOffice returned a non-zero exit code.")

        expected_pdf = destination.parent / f"{source.stem}.pdf"
        if expected_pdf != destination and expected_pdf.exists():
            shutil.move(expected_pdf, destination)


def _resolve_filter_argument(extension: str) -> str:
    if extension in {".doc", ".docx"}:
        return "pdf:writer_pdf_Export"
    return "pdf:calc_pdf_Export"


def _get_soffice_path() -> str | None:
    candidates = [
        shutil.which("soffice"),
        shutil.which("libreoffice"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def _ensure_libreoffice_quits() -> None:
    """Ensure lingering GUI instances are closed after headless conversion."""
    if not Path("/Applications/LibreOffice.app").exists():
        return

    attempts = [
        ["osascript", "-e", 'tell application "LibreOffice" to quit'],
        ["pkill", "-f", "LibreOffice.app/Contents/MacOS/soffice"],
        ["pkill", "-f", "soffice.bin"],
    ]

    for command in attempts:
        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
            )
        except FileNotFoundError:
            continue
        except Exception:  # noqa: BLE001
            continue
