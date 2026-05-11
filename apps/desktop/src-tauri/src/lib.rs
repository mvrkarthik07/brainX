use std::sync::Mutex;

use tauri::Manager;
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

struct BackendSidecar(Mutex<Option<CommandChild>>);

pub fn run() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(BackendSidecar(Mutex::new(None)))
        .setup(|app| {
            // In packaged mode, we ship a Python sidecar binary and start it automatically.
            // In dev mode, developers can keep using their own backend flow (port 8000/8420).
            if cfg!(debug_assertions) {
                return Ok(());
            }

            let sidecar = app
                .shell()
                .sidecar("brainx-backend")?
                .args(["--host", "127.0.0.1", "--port", "8765"]);

            let (_rx, child) = sidecar.spawn()?;

            let state = app.state::<BackendSidecar>();
            *state.0.lock().expect("sidecar mutex poisoned") = Some(child);

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building brainX desktop");

    app.run(|app_handle, event| {
        if matches!(event, tauri::RunEvent::ExitRequested { .. }) {
            let state = app_handle.state::<BackendSidecar>();
            let mut guard = state.0.lock().expect("sidecar mutex poisoned");
            if let Some(child) = guard.take() {
                let _ = child.kill();
            }
        }
    });
}
