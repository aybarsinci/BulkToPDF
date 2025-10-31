@echo off
setlocal EnableDelayedExpansion

REM Build a Windows executable for BulkToPDF using PyInstaller.

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
pushd "%PROJECT_ROOT%"

if "%VENV_PATH%"=="" (
    set "VENV_PATH=%PROJECT_ROOT%\.venv-win"
)

if not exist "%VENV_PATH%" (
    python -m venv "%VENV_PATH%"
)

call "%VENV_PATH%\Scripts\activate.bat"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

for /f "usebackq delims=" %%I in (`"%VENV_PATH%\Scripts\python.exe" -c "import tkinterdnd2, os; print(os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd'))"`) do (
    set "TKDND_DIR=%%I"
)

if "%ICON_PATH%"=="" (
    set "ICON_PATH=%PROJECT_ROOT%\Resources\BulkToPDF_icon.ico"
)

set "PYINSTALLER=%VENV_PATH%\Scripts\pyinstaller.exe"

if defined TKDND_DIR if exist "%TKDND_DIR%" (
    "%PYINSTALLER%" --noconfirm --windowed --name BulkToPDF --icon "%ICON_PATH%" --hidden-import=tkinterdnd2 --add-data "%TKDND_DIR%;tkinterdnd2/tkdnd" main.py %*
) else (
    "%PYINSTALLER%" --noconfirm --windowed --name BulkToPDF --icon "%ICON_PATH%" --hidden-import=tkinterdnd2 main.py %*
)

echo.
echo Windows executable created at dist\BulkToPDF\BulkToPDF.exe

popd
endlocal
