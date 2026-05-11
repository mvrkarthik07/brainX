# Backend sidecar (packaged FastAPI)

BrainX ships a local backend engine (FastAPI) and the desktop app should launch it automatically.

This document describes the **alpha packaging approach**:

- Build a standalone backend executable using **PyInstaller**
- Bundle that executable as a **Tauri sidecar**
- Desktop app launches the sidecar on startup and talks to it via `http://127.0.0.1:<port>`

## Why a sidecar

- Keeps the backend Python stack intact (no rewrite in Rust)
- Enables offline/local-first behavior
- Allows app updates to update only the app code while keeping user data in OS app-data directories

## Dev backend

Run the backend in reload mode:

```bash
bash scripts/run_backend_dev.sh
```

Or directly:

```bash
.venv/bin/uvicorn apps.api.main:app --reload
```

## Sidecar entrypoint

The PyInstaller entrypoint is:

- `apps/api/sidecar_main.py`

Run it directly (no reload):

```bash
.venv/bin/python apps/api/sidecar_main.py --port 8765
curl -i http://127.0.0.1:8765/health
```

Environment:

- `BRAINX_PORT`: override default port (8765)
- `BRAINX_LOG_LEVEL`: uvicorn log level (default: info)
- `BRAINX_DATA_DIR`: override the data directory (see `brain.config.paths`)

## Build sidecar binary

Prereqs:

- Python venv at `.venv`
- `pip install -r requirements.txt`
- Install PyInstaller (do not commit it as a hard prereq for dev):

```bash
.venv/bin/python -m pip install pyinstaller
```

Build:

```bash
bash scripts/build_backend_sidecar.sh
```

Output:

- `apps/desktop/src-tauri/binaries/brainx-backend` (platform-specific executable)

## Notes / pitfalls

- The built binary is **platform-specific**; build on each target OS in CI.
- Do **not** store runtime state inside the app bundle. Backend uses `brain.config.paths` to locate OS app-data directories.

