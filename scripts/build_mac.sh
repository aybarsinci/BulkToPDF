#!/usr/bin/env bash

# Build a macOS app bundle for BulkToPDF using PyInstaller.
# Creates (or reuses) a virtualenv under .venv-build by default.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

VENV_PATH="${VENV_PATH:-${PROJECT_ROOT}/.venv-build}"
ICON_PATH="${ICON_PATH:-${PROJECT_ROOT}/Resources/BulkToPDF_icon.icns}"

if [[ ! -d "${VENV_PATH}" ]]; then
    python3 -m venv "${VENV_PATH}"
fi

# shellcheck disable=SC1091
source "${VENV_PATH}/bin/activate"

pip install --upgrade pip
pip install -r requirements.txt pyinstaller

PYINSTALLER_ARGS=(
    --noconfirm
    --windowed
    --name BulkToPDF
    --hidden-import=tkinterdnd2
)

if [[ -f "${ICON_PATH}" ]]; then
    PYINSTALLER_ARGS+=(--icon "${ICON_PATH}")
fi

pyinstaller "${PYINSTALLER_ARGS[@]}" main.py "$@"

echo "macOS app bundle created at dist/BulkToPDF.app"
