from pathlib import Path

# brain/config/settings.py -> brain -> brain-core -> packages -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_USER_DIR = DATA_DIR / "users" / "default"

SQLITE_DB_PATH = DEFAULT_USER_DIR / "user.db"
FAISS_INDEX_PATH = DEFAULT_USER_DIR / "user.faiss"

MEMGRAPH_URI = "bolt://localhost:7687"
MEMGRAPH_USER = ""
MEMGRAPH_PASSWORD = ""

OLLAMA_BASE_URL = "http://localhost:11434"

EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768

REWRITE_MODEL = "qwen2.5:3b"
GENERATION_MODEL = "qwen2.5:7b"
