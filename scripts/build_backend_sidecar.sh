#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/apps/desktop/src-tauri/binaries"
ENTRYPOINT="${ROOT_DIR}/apps/api/sidecar_main.py"

mkdir -p "${OUT_DIR}"

PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ -x "${PYTHON_BIN}" ]]; then
  :
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "No python found. Install Python 3 and/or create .venv."
  exit 1
fi

if ! "${PYTHON_BIN}" -c "import PyInstaller" >/dev/null 2>&1; then
  echo "PyInstaller is not installed in this environment."
  echo "Install it in your venv:"
  echo "  ${PYTHON_BIN} -m pip install pyinstaller"
  exit 1
fi

# Ensure repo imports work (packages/brain-core is not necessarily installed when packaging locally).
export PYTHONPATH="${ROOT_DIR}:${ROOT_DIR}/packages/brain-core:${PYTHONPATH:-}"

# Default packaged port; override at runtime via BRAINX_PORT.
export BRAINX_PORT="${BRAINX_PORT:-8765}"

echo "Building BrainX backend sidecar..."
echo "  python: ${PYTHON_BIN}"
echo "  entry:  ${ENTRYPOINT}"
echo "  out:    ${OUT_DIR}"

SCHEMA_SQL="${ROOT_DIR}/packages/brain-core/brain/storage/schema.sql"

"${PYTHON_BIN}" -m PyInstaller \
  --noconfirm \
  --clean \
  --name brainx-backend \
  --onefile \
  --distpath "${OUT_DIR}" \
  --add-data "${SCHEMA_SQL}:brain/storage" \
  "${ENTRYPOINT}"

TARGET_TRIPLE="$(rustc --print host-tuple 2>/dev/null || true)"
if [[ -n "${TARGET_TRIPLE}" ]]; then
  mv -f "${OUT_DIR}/brainx-backend" "${OUT_DIR}/brainx-backend-${TARGET_TRIPLE}"
  echo "Done. Sidecar binary: ${OUT_DIR}/brainx-backend-${TARGET_TRIPLE}"
else
  echo "Done. Sidecar binary: ${OUT_DIR}/brainx-backend"
  echo "Note: Tauri bundling expects a target-triple suffix; install Rust or rename accordingly."
fi

