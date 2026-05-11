import sqlite3
from datetime import datetime, timezone

from brain.config.settings import PROJECT_ROOT, SQLITE_DB_PATH, DEFAULT_USER_DIR

DEFAULT_USER_ID = "default"

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    DEFAULT_USER_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_sqlite():
    schema_path = PROJECT_ROOT / "packages" / "brain-core" / "brain" / "storage" / "schema.sql"

    with get_connection() as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    
        conn.execute("""

            INSERT OR IGNORE INTO users (

                id, created_at, total_queries, total_documents, preferences_json

            )

            VALUES (?, ?, 0, 0, '{}')

            """,

            (DEFAULT_USER_ID, utc_now_iso()),

        )
        conn.commit()

def sql_health() -> dict:
    try:
        initialize_sqlite()
        with get_connection() as conn:
            user = conn.execute("""

                SELECT id, created_at, total_queries, total_documents

                FROM users

                WHERE id = ?

                """, (DEFAULT_USER_ID,),).fetchone()
            return {
                "ok": True,
                "db_path": str(SQLITE_DB_PATH),
                "default_user_exists": user is not None,
                "default_user_created_at": user["created_at"] if user else None,
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }
    

