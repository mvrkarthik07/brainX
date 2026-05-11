from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import sqlite3


@dataclass(frozen=True)
class Migration:
    id: str
    description: str
    sql: str


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def get_applied_migrations(conn: sqlite3.Connection) -> set[str]:
    _ensure_migrations_table(conn)
    rows = conn.execute("SELECT id FROM schema_migrations ORDER BY id ASC").fetchall()
    return {row[0] for row in rows}


def _utc_now_iso(conn: sqlite3.Connection) -> str:
    # Use SQLite time to avoid needing datetime deps and keep deterministic format.
    row = conn.execute("SELECT strftime('%Y-%m-%dT%H:%M:%fZ','now')").fetchone()
    return row[0] if row and row[0] else "1970-01-01T00:00:00.000Z"


def _baseline_sql_path() -> Path:
    # packages/brain-core/brain/storage/migrations.py -> storage/
    return Path(__file__).resolve().parent / "schema.sql"


def _load_migrations() -> list[Migration]:
    # 0001 is a baseline: create tables/indexes if missing.
    baseline_sql = _baseline_sql_path().read_text(encoding="utf-8")
    return [
        Migration(
            id="0001_initial_schema",
            description="Baseline schema (create tables/indexes if missing).",
            sql=baseline_sql,
        )
    ]


def apply_migrations(conn: sqlite3.Connection, migrations: Iterable[Migration] | None = None) -> list[str]:
    """
    Applies pending migrations in order and records them in schema_migrations.

    Safety properties:
    - Baseline migration uses CREATE TABLE IF NOT EXISTS and CREATE INDEX IF NOT EXISTS.
    - Future migrations should be additive by default (no DROP TABLE).
    """
    _ensure_migrations_table(conn)
    applied = get_applied_migrations(conn)
    ran: list[str] = []

    for migration in (list(migrations) if migrations is not None else _load_migrations()):
        if migration.id in applied:
            continue

        conn.executescript(migration.sql)
        conn.execute(
            "INSERT INTO schema_migrations (id, description, applied_at) VALUES (?, ?, ?)",
            (migration.id, migration.description, _utc_now_iso(conn)),
        )
        ran.append(migration.id)

    return ran

