#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  echo "Missing venv python at .venv/bin/python. Create it first (python -m venv .venv) and install requirements."
  exit 1
fi

exec "${ROOT_DIR}/.venv/bin/uvicorn" apps.api.main:app --reload

