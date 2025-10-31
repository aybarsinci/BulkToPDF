# BulkToPDF

A desktop application to bulk convert documents to PDF format. Built with Python, this tool supports the conversion of Word and Excel files with a user-friendly GUI.

## Download

Pick your platform and grab the latest build from GitHub releases:

[![Download for Windows](https://img.shields.io/badge/download-Windows_%28.zip%29-blue.svg)](https://github.com/aybarsinci/BulkToPDF/releases/download/v.1.0.5/BulkToPDF.zip)
[![Download for macOS](https://img.shields.io/badge/download-macOS_%28.zip%29-green.svg)](https://github.com/aybarsinci/BulkToPDF/releases/download/v1.0.3/BulkToPDF-macOS.zip)

## Features

- **Batch Conversion**: Convert multiple Word documents (.doc, .docx) and Excel spreadsheets (.xls, .xlsx) to PDF in one go.
- **Drag-and-Drop UI**: Drop a folder (or browse to one) and kick off, pause-free conversion instantly.
- **Downloadable Zip**: Converted PDFs are bundled into a single zip file when the process completes.
- **Cross-platform**: A shared codebase drives both Windows (via Microsoft Office automation) and macOS/Linux (via headless LibreOffice).
- **Flexible Output Modes**: Toggle between skipping other file types or copying them into the output archive unchanged.
- **Smart Filtering**: Always skips OS temp files (`.DS_Store`, `Thumbs.db`, `~$...`) to keep output clean in either mode.
- **Robust Error Reporting**: Numbered error log with clear status messaging and aggregated failure counts.
- **Exportable Error Logs**: Save a detailed `BulkToPDF_errors.txt` report after each run with failures.

## Usage

This tool is ideal for individuals and businesses needing to digitize batches of documents, streamline workflow processes, or manage document conversions without relying on online services.

## Run the App (Binaries)

**Windows**
- Download the latest `BulkToPDF.exe`.
- Ensure Microsoft Word and Excel are installed (the converter uses Office automation).
- Double-click the executable. Windows SmartScreen may warn about unknown publishers; click **More info → Run anyway** if you trust the app.

**macOS**
- Download `BulkToPDF-macOS.zip` and unzip it to reveal `BulkToPDF.app`.
- Optional: move the app into `/Applications` for easier access.
- Because the build is unsigned, macOS may block the first launch. Either right-click the app and choose **Open**, or run `xattr -r -d com.apple.quarantine BulkToPDF.app` in Terminal.
- Install LibreOffice (see prerequisites below) and open it once from Applications so the OS finishes verification before running the headless converter.

## Getting Started (from source)

1. Clone the repository and install dependencies into a virtual environment:

   ```bash
   git clone https://github.com/yourusername/BulkToPDF.git
   cd BulkToPDF
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Launch the application:

   ```bash
   python main.py
   ```

## Prerequisites

- **Windows**: Python 3.9+ and the `comtypes` package (`pip install comtypes`). Microsoft Word/Excel must be installed.
- **macOS**: Python 3.9+ and LibreOffice (install via the [official DMG](https://www.libreoffice.org/download/download/) or `brew install --cask libreoffice`). Ensure the `soffice` binary is on your `PATH` (or located at `/Applications/LibreOffice.app/Contents/MacOS/soffice`).
- **Optional (for drag-and-drop on all platforms)**: `pip install tkinterdnd2`. Without it, use the **Browse** button to pick a folder.
- On macOS, launch LibreOffice once from Applications to finish the OS verification prompt before running it headlessly.

## Architecture Overview

The codebase is organised into a small, testable package:

```
bulktopdf/
├── conversion/          # Platform-specific conversion backends
├── services/            # Business logic (directory traversal, zipping)
├── ui/                  # Tkinter view/controller glue
├── config.py            # Shared configuration dataclasses
└── logging_utils.py     # Centralised logging setup
```

- `conversion` hides the platform differences (LibreOffice vs. comtypes).
- `services.ConversionService` orchestrates directory traversal, invokes the converter, collects results, and emits user-facing callbacks.
- `ui` contains a clear MVC boundary: the `PDFConverterController` wires the service to the Tkinter `PDFConverterView` using callbacks.

This separation allows backend logic to be unit-tested without the GUI, keeps platform-specific code in one place, and makes it straightforward to add new interfaces (CLI/API) in the future.

## Error Handling & Logging

- Every conversion error is recorded and displayed with an index in the Errors panel.
- A summary reports how many files failed and whether a zip is ready for download.
- Logs are emitted through the standard `logging` module (`bulktopdf/logging_utils.py`) so they can easily be redirected to files or aggregators.

## Contributing

- Ensure the code passes linting (`ruff`, `black`) and basic static checks (`mypy`) if available in your environment.
- Tests can be added under a future `tests/` directory; the modular design makes it easy to mock conversion backends.

After installing the prerequisites, run `python main.py` to launch the GUI. Drop a folder (or click **Browse**) and press **Convert**. When the process finishes, click **Download Converted Zip** to choose where to save the generated archive.

If any files fail, review them in the **Errors** panel and click **Save Errors** to export a text report (`BulkToPDF_errors.txt`) with the exact failure messages.

## Building a macOS App Bundle

Use the helper script to generate a standalone `.app` bundle with PyInstaller:

```bash
./scripts/build_mac.sh
```

The script will:

- create (or reuse) a `.venv-build` virtual environment in the project root,
- install the runtime requirements together with `pyinstaller`, and
- emit `dist/BulkToPDF.app` and the unpacked `dist/BulkToPDF/` folder with the bundled app icon.

Tips for distributing the build:

- To override the default icon, pass `--icon path/to/custom.icns` (or set `ICON_PATH=...`) when running the script.
- Package the application for GitHub releases with `cd dist && zip -r BulkToPDF-macOS.zip BulkToPDF.app`.
- If you are not code-signing the app, remind users they may need to run `xattr -r -d com.apple.quarantine BulkToPDF.app` after downloading.

## Building a Windows Executable

Use the batch helper to produce a PyInstaller build:

```powershell
scripts\build_windows.bat
```

The script:

- creates (or reuses) `.venv-win` in the project root,
- installs runtime requirements alongside `pyinstaller`,
- bundles the `tkinterdnd2/tkdnd` DLLs so drag-and-drop keeps working, and
- emits `dist\BulkToPDF\BulkToPDF.exe` plus the supporting files under `dist\BulkToPDF\`.

Pass extra PyInstaller flags after the script call (e.g. `scripts\build_windows.bat --clean`). To override the icon, set `ICON_PATH=Path\To\Icon.ico scripts\build_windows.bat`.
