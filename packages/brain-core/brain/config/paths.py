from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "BrainX"
ENV_DATA_DIR = "BRAINX_DATA_DIR"


def _project_root() -> Path:
    # packages/brain-core/brain/config/paths.py -> ... -> project root
    return Path(__file__).resolve().parents[4]


def _is_packaged_runtime() -> bool:
    # PyInstaller sets sys.frozen = True. This is our "packaged mode" signal.
    return bool(getattr(sys, "frozen", False))


def _default_os_data_root() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME
        return home / "AppData" / "Roaming" / APP_NAME
    # Linux + everything else.
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / APP_NAME
    return home / ".local" / "share" / APP_NAME


def get_data_dir() -> Path:
    """
    Returns the root directory for all BrainX runtime state.

    Behavior:
    - If BRAINX_DATA_DIR is set, it always wins (dev or packaged).
    - In packaged mode (PyInstaller), defaults to OS app data dir.
    - In dev mode, defaults to <project_root>/data (backwards compatible).
    """
    override = os.environ.get(ENV_DATA_DIR, "").strip()
    if override:
        return Path(override).expanduser().resolve()

    if _is_packaged_runtime():
        return _default_os_data_root()

    return _project_root() / "data"


def get_user_dir(user_id: str = "default") -> Path:
    return get_data_dir() / "users" / user_id


def get_sqlite_db_path(user_id: str = "default") -> Path:
    return get_user_dir(user_id) / "user.db"


def get_faiss_index_path(user_id: str = "default") -> Path:
    return get_user_dir(user_id) / "user.faiss"


def get_snapshots_dir(user_id: str = "default") -> Path:
    return get_user_dir(user_id) / "snapshots"


def get_documents_dir(user_id: str = "default") -> Path:
    return get_user_dir(user_id) / "documents"


def get_config_path(user_id: str = "default") -> Path:
    return get_user_dir(user_id) / "config.json"


def ensure_runtime_dirs(user_id: str = "default") -> None:
    """
    Create runtime directories if missing.
    Safe to call on every start; does not overwrite files.
    """
    base = get_user_dir(user_id)
    base.mkdir(parents=True, exist_ok=True)
    get_snapshots_dir(user_id).mkdir(parents=True, exist_ok=True)
    get_documents_dir(user_id).mkdir(parents=True, exist_ok=True)

