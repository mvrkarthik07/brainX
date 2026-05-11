# Release checklist (alpha)

## Version bump

Update version consistently in:

- `apps/desktop/package.json`
- `apps/desktop/src-tauri/tauri.conf.json`
- `apps/desktop/src-tauri/Cargo.toml`
- `apps/api/main.py` (API version string)

## Preflight

- Ensure Ollama is installed and running (local prerequisite)
- Run backend scripts:

```bash
.venv/bin/python scripts/dev/check_health.py
.venv/bin/python scripts/dev/query_sample.py
```

## Build backend sidecar

```bash
bash scripts/build_backend_sidecar.sh
```

This must be built **per platform** (macOS, Windows, Linux).

## Build desktop app

```bash
cd apps/desktop
npm install
npm run tauri:build
```

## Sign updater artifacts

- Generate updater keys (one-time) and keep the private key secret.
- Build with the private key available via environment/CI secrets.
- Upload release artifacts and `latest.json` to your hosting.

## Test update flow

1. Install previous version (e.g. `0.0.1`)
2. Publish new signed release (e.g. `0.0.2`)
3. Confirm the installed `0.0.1` updates to `0.0.2`

Updater testing must be done on an **installed packaged app**, not `tauri dev`.

