## `src-tauri/binaries/`

This folder contains **Tauri sidecar binaries** bundled into the desktop app.

Tauri expects binaries to be named with the target triple suffix, e.g.:

- `brainx-backend-aarch64-apple-darwin`
- `brainx-backend-x86_64-unknown-linux-gnu`
- `brainx-backend-x86_64-pc-windows-msvc.exe`

For local development, this repo may include a small placeholder binary for the current platform so
`cargo check` / `tauri build` can validate the config. Replace it by running:

```bash
bash scripts/build_backend_sidecar.sh
```

