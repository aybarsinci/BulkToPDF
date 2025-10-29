# BulkToPDF

A desktop application to bulk convert documents to PDF format. Built with Python, this tool supports the conversion of Word and Excel files with a user-friendly GUI.

## Download

To download the latest version of BulkToPDF, click the button below:

[![Download BulkToPDF](https://img.shields.io/badge/download-BulkToPDF.exe-blue.svg)](https://github.com/aybarsinci/BulkToPDF/releases/download/v1.0.2/BulkToPDF.exe)

## Features

- **Batch Conversion**: Convert multiple Word documents (.doc, .docx) and Excel spreadsheets (.xls, .xlsx) to PDF in one go.
- **Drag-and-Drop UI**: Drop a folder (or browse to one) and kick off, pause-free conversion instantly.
- **Downloadable Zip**: Converted PDFs are bundled into a single zip file when the process completes.
- **Cross-platform**: A shared codebase drives both Windows (via Microsoft Office automation) and macOS/Linux (via headless LibreOffice).
- **Safe Concurrency**: A multi-threaded conversion pipeline with backend-specific locks keeps the UI responsive while avoiding LibreOffice/COM conflicts.
- **Flexible Output Modes**: Toggle between skipping unsupported file types or copying them into the output archive unchanged.
- **Smart Filtering**: Always skips OS temp files (`.DS_Store`, `Thumbs.db`, `~$...`) to keep output clean in either mode.
- **Robust Error Reporting**: Numbered error log with clear status messaging and aggregated failure counts.


## Usage

This tool is ideal for individuals and businesses needing to digitize batches of documents, streamline workflow processes, or manage document conversions without relying on online services.

## Getting Started

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
