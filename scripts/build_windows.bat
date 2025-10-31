@echo off
setlocal EnableDelayedExpansion
rem DEBUG: echo commands if needed
if /i "%DEBUG_BUILD%"=="1" echo on

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

if "%ICON_PATH%"=="" (
    set "ICON_PATH=%PROJECT_ROOT%\Resources\BulkToPDF_icon.ico"
)

set "PYINSTALLER=%VENV_PATH%\Scripts\pyinstaller.exe"

echo Running: "%PYINSTALLER%" --noconfirm --windowed --name BulkToPDF --icon "%ICON_PATH%" --hidden-import=tkinterdnd2 --collect-all tkinterdnd2 main.py %*
"%PYINSTALLER%" --noconfirm --windowed --name BulkToPDF --icon "%ICON_PATH%" --hidden-import=tkinterdnd2 --collect-all tkinterdnd2 main.py %*

echo.
echo Windows executable created at dist\BulkToPDF\BulkToPDF.exe

popd
endlocal
