from datetime import datetime, timezone

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from brain.config.settings import MEMGRAPH_PASSWORD, MEMGRAPH_URI, MEMGRAPH_USER

DEFAULT_USER_ID = "default"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    auth = None
    if MEMGRAPH_USER or MEMGRAPH_PASSWORD:
        auth = (MEMGRAPH_USER, MEMGRAPH_PASSWORD)

    return GraphDatabase.driver(MEMGRAPH_URI, auth=auth)


def _safe_schema_setup(session) -> None:
    schema_statements = (
        "CREATE INDEX ON :User(id)",
        "CREATE CONSTRAINT ON (u:User) ASSERT u.id IS UNIQUE",
    )

    for statement in schema_statements:
        try:
            session.run(statement).consume()
        except Neo4jError:
            # Memgraph versions differ in DDL support and duplicate schema handling.
            continue


def _ensure_default_user(session) -> bool:
    result = session.run(
        """
        MERGE (u:User {id: $user_id})
        ON CREATE SET u.created_at = $created_at
        SET
            u.total_queries = coalesce(u.total_queries, 0),
            u.total_documents = coalesce(u.total_documents, 0)
        RETURN u.id = $user_id AS default_user_exists
        """,
        user_id=DEFAULT_USER_ID,
        created_at=utc_now_iso(),
    )
    record = result.single()
    return bool(record and record["default_user_exists"])


def initialize_memgraph() -> bool:
    with get_connection() as driver:
        with driver.session() as session:
            session.run("RETURN 1 AS ok").consume()
            _safe_schema_setup(session)
            return _ensure_default_user(session)


def memgraph_health() -> dict:
    try:
        default_user_exists = initialize_memgraph()
        return {
            "ok": True,
            "uri": MEMGRAPH_URI,
            "default_user_exists": default_user_exists,
        }
    except Exception as exc:
        return {
            "ok": False,
            "uri": MEMGRAPH_URI,
            "error": str(exc),
        }
