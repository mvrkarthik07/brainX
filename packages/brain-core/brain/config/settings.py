from pathlib import Path

from brain.config.paths import (
    ensure_runtime_dirs,
    get_data_dir,
    get_faiss_index_path,
    get_sqlite_db_path,
    get_user_dir,
)

# brain/config/settings.py -> brain -> brain-core -> packages -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = get_data_dir()
DEFAULT_USER_DIR = get_user_dir("default")
UPLOADED_FILES_DIR = DEFAULT_USER_DIR / "uploads"
ensure_runtime_dirs("default")

SQLITE_DB_PATH = get_sqlite_db_path("default")
FAISS_INDEX_PATH = get_faiss_index_path("default")

GRAPH_BACKEND = "sqlite"

# Optional legacy/dev graph backend settings.
MEMGRAPH_URI = "bolt://localhost:7687"
MEMGRAPH_USER = ""
MEMGRAPH_PASSWORD = ""

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_HEALTH_TIMEOUT_SECONDS = 5
OLLAMA_EMBED_TIMEOUT_SECONDS = 30
OLLAMA_GENERATE_TIMEOUT_SECONDS = 120

EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768

REWRITE_MODEL = "qwen2.5:3b"
GENERATION_MODEL = "qwen2.5:3b"
