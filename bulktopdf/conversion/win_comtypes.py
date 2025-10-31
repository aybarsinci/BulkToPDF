"""Windows COM-based conversion backend."""

from __future__ import annotations

import threading
from pathlib import Path

try:
    import comtypes  # type: ignore
    import comtypes.client  # type: ignore
except ImportError:  # pragma: no cover - handled at runtime
    comtypes = None  # type: ignore[assignment]
    comtypes_client = None  # type: ignore[assignment]
else:
    comtypes_client = comtypes.client  # type: ignore

_COM_LOCK = threading.Lock()


def convert_with_comtypes(source: Path, destination: Path) -> None:
    if comtypes is None or comtypes_client is None:
        raise RuntimeError("comtypes is not installed; Word/Excel automation unavailable.")

    file_type = source.suffix.lower()
    with _COM_LOCK:
        initialized = False
        app = None
        try:
            comtypes.CoInitialize()  # Initialize COM on this thread.
            initialized = True
            if file_type in {".doc", ".docx"}:
                app = comtypes_client.CreateObject("Word.Application")
                app.DisplayAlerts = False
                doc = app.Documents.Open(str(source))
                doc.SaveAs(str(destination), FileFormat=17)
                doc.Close()
            else:
                app = comtypes_client.CreateObject("Excel.Application")
                app.DisplayAlerts = False
                workbook = app.Workbooks.Open(str(source))
                workbook.ExportAsFixedFormat(0, str(destination))
                workbook.Close()
        finally:
            if app is not None:
                app.Quit()
            if initialized:
                comtypes.CoUninitialize()
