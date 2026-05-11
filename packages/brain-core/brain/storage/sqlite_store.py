import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from brain.config.settings import DEFAULT_USER_DIR, PROJECT_ROOT, SQLITE_DB_PATH
from brain.storage.migrations import apply_migrations

DEFAULT_USER_ID = "default"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    DEFAULT_USER_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_sqlite() -> None:
    with get_connection() as conn:
        apply_migrations(conn)

        conn.execute(
            """
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
            user = conn.execute(
                """
                SELECT id, created_at, total_queries, total_documents
                FROM users
                WHERE id = ?
                """,
                (DEFAULT_USER_ID,),
            ).fetchone()
            return {
                "ok": True,
                "db_path": str(SQLITE_DB_PATH),
                "default_user_exists": user is not None,
                "default_user_created_at": user["created_at"] if user else None,
            }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }


def create_document(
    title: str,
    file_path: str,
    file_type: str,
    metadata: dict[str, Any] | None = None,
    raw_text: str | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    initialize_sqlite()

    checksum = _compute_checksum(raw_text or "")
    document_id = _stable_id("document", f"{Path(file_path).resolve()}::{checksum}")
    now = utc_now_iso()
    metadata_json = _encode_json(metadata or {})

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT ingested_at FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        ingested_at = existing["ingested_at"] if existing else now

        conn.execute(
            """
            INSERT INTO documents (
                id, user_id, title, file_path, file_type, checksum, metadata_json, ingested_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                file_path = excluded.file_path,
                file_type = excluded.file_type,
                checksum = excluded.checksum,
                metadata_json = excluded.metadata_json,
                updated_at = excluded.updated_at
            """,
            (
                document_id,
                user_id,
                title,
                str(Path(file_path).resolve()),
                file_type,
                checksum,
                metadata_json,
                ingested_at,
                now,
            ),
        )
        _refresh_user_document_count(conn, user_id)
        conn.commit()

    document = get_document(document_id)
    if document is None:
        raise RuntimeError("Failed to create document record")
    return document


def create_chunk(
    document_id: str,
    text: str,
    position: int,
    file_path: str,
    file_type: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    initialize_sqlite()

    chunk_id = _stable_id("chunk", f"{document_id}:{position}:{_compute_checksum(text)}")
    now = utc_now_iso()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chunks (
                id, document_id, text, position, file_path, file_type, metadata_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                text = excluded.text,
                position = excluded.position,
                file_path = excluded.file_path,
                file_type = excluded.file_type,
                metadata_json = excluded.metadata_json
            """,
            (
                chunk_id,
                document_id,
                text,
                position,
                file_path,
                file_type,
                _encode_json(metadata or {}),
                now,
            ),
        )
        conn.commit()

    chunk = get_chunk_by_id(chunk_id)
    if chunk is None:
        raise RuntimeError("Failed to create chunk record")
    return chunk


def create_concept(label: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    initialize_sqlite()

    normalized_label = " ".join(label.lower().split())
    concept_id = _stable_id("concept", normalized_label)
    now = utc_now_iso()

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT frequency FROM concepts WHERE id = ?",
            (concept_id,),
        ).fetchone()
        new_frequency = (existing["frequency"] if existing else 0) + 1

        conn.execute(
            """
            INSERT INTO concepts (
                id, label, normalized_label, frequency, metadata_json, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                label = excluded.label,
                frequency = ?,
                metadata_json = excluded.metadata_json,
                updated_at = excluded.updated_at
            """,
            (
                concept_id,
                label,
                normalized_label,
                new_frequency,
                _encode_json(metadata or {}),
                now,
                now,
                new_frequency,
            ),
        )
        conn.commit()

    return get_concept(concept_id)


def link_chunk_concept(chunk_id: str, concept_id: str, frequency: int = 1) -> None:
    initialize_sqlite()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chunk_concepts (chunk_id, concept_id, frequency)
            VALUES (?, ?, ?)
            ON CONFLICT(chunk_id, concept_id) DO UPDATE SET
                frequency = excluded.frequency
            """,
            (chunk_id, concept_id, frequency),
        )
        conn.commit()


def get_document(document_id: str) -> dict[str, Any] | None:
    initialize_sqlite()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT d.*, COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            WHERE d.id = ?
            GROUP BY d.id
            """,
            (document_id,),
        ).fetchone()
        return _row_to_document(row) if row is not None else None


def list_documents() -> list[dict[str, Any]]:
    initialize_sqlite()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.*, COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.ingested_at DESC
            """
        ).fetchall()
        return [_row_to_document(row) for row in rows]


def get_chunk_by_id(chunk_id: str) -> dict[str, Any] | None:
    initialize_sqlite()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM chunks WHERE id = ?",
            (chunk_id,),
        ).fetchone()
        return _row_to_chunk(row) if row is not None else None


def get_chunks_for_document(document_id: str) -> list[dict[str, Any]]:
    initialize_sqlite()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM chunks
            WHERE document_id = ?
            ORDER BY position ASC
            """,
            (document_id,),
        ).fetchall()
        return [_row_to_chunk(row) for row in rows]


def get_chunks_by_ids(chunk_ids: list[str]) -> list[dict[str, Any]]:
    initialize_sqlite()
    if not chunk_ids:
        return []

    placeholders = ",".join("?" for _ in chunk_ids)
    order_map = {chunk_id: index for index, chunk_id in enumerate(chunk_ids)}
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT *
            FROM chunks
            WHERE id IN ({placeholders})
            """,
            chunk_ids,
        ).fetchall()
    chunks = [_row_to_chunk(row) for row in rows]
    return sorted(chunks, key=lambda chunk: order_map.get(chunk["id"], len(order_map)))


def get_concept(concept_id: str) -> dict[str, Any]:
    initialize_sqlite()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM concepts WHERE id = ?",
            (concept_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Concept '{concept_id}' was not found")
        return _row_to_concept(row)


def get_concepts_for_chunk(chunk_id: str) -> list[dict[str, Any]]:
    initialize_sqlite()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.*
            FROM concepts c
            INNER JOIN chunk_concepts cc ON cc.concept_id = c.id
            WHERE cc.chunk_id = ?
            ORDER BY c.frequency DESC, c.label ASC
            """,
            (chunk_id,),
        ).fetchall()
    return [_row_to_concept(row) for row in rows]


def get_documents_by_ids(document_ids: list[str]) -> list[dict[str, Any]]:
    initialize_sqlite()
    if not document_ids:
        return []

    placeholders = ",".join("?" for _ in document_ids)
    order_map = {document_id: index for index, document_id in enumerate(document_ids)}
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT d.*, COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            WHERE d.id IN ({placeholders})
            GROUP BY d.id
            """,
            document_ids,
        ).fetchall()
    documents = [_row_to_document(row) for row in rows]
    return sorted(documents, key=lambda document: order_map.get(document["id"], len(order_map)))


def map_vector(faiss_id: int, chunk_id: str, document_id: str) -> None:
    initialize_sqlite()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO vector_mappings (faiss_id, chunk_id, document_id, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (faiss_id, chunk_id, document_id, utc_now_iso()),
        )
        conn.commit()


def get_chunk_id_for_faiss_id(faiss_id: int) -> str | None:
    initialize_sqlite()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT chunk_id FROM vector_mappings WHERE faiss_id = ?",
            (faiss_id,),
        ).fetchone()
        return row["chunk_id"] if row is not None else None


def get_vector_mappings(
    faiss_id: int | None = None,
    chunk_id: str | None = None,
    document_id: str | None = None,
) -> list[dict[str, Any]]:
    initialize_sqlite()

    query = "SELECT * FROM vector_mappings"
    clauses: list[str] = []
    params: list[Any] = []

    if faiss_id is not None:
        clauses.append("faiss_id = ?")
        params.append(faiss_id)
    if chunk_id is not None:
        clauses.append("chunk_id = ?")
        params.append(chunk_id)
    if document_id is not None:
        clauses.append("document_id = ?")
        params.append(document_id)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY faiss_id ASC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [_row_to_vector_mapping(row) for row in rows]


def save_interaction(
    query_text: str,
    rewritten_query: str | None,
    response_text: str,
    nodes_traversed: list[Any],
    edges_traversed: list[Any],
    user_id: str = DEFAULT_USER_ID,
    interaction_id: str | None = None,
) -> dict[str, Any]:
    initialize_sqlite()

    stored_interaction_id = interaction_id or str(uuid.uuid4())
    timestamp = utc_now_iso()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO interactions (
                id,
                user_id,
                query_text,
                rewritten_query,
                response_text,
                rating,
                timestamp,
                nodes_traversed_json,
                edges_traversed_json
            )
            VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?)
            """,
            (
                stored_interaction_id,
                user_id,
                query_text,
                rewritten_query,
                response_text,
                timestamp,
                _encode_any_json(nodes_traversed),
                _encode_any_json(edges_traversed),
            ),
        )
        conn.commit()

    interaction = get_interaction(stored_interaction_id)
    if interaction is None:
        raise RuntimeError("Failed to save interaction")
    return interaction


def get_interaction(interaction_id: str) -> dict[str, Any] | None:
    initialize_sqlite()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM interactions WHERE id = ?",
            (interaction_id,),
        ).fetchone()
    return _row_to_interaction(row) if row is not None else None


def save_interaction_trace(
    interaction_id: str,
    nodes: list[Any],
    edges: list[Any],
    trace: dict[str, Any],
) -> dict[str, Any]:
    initialize_sqlite()
    created_at = utc_now_iso()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO interaction_traces (
                interaction_id,
                nodes_json,
                edges_json,
                trace_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(interaction_id) DO UPDATE SET
                nodes_json = excluded.nodes_json,
                edges_json = excluded.edges_json,
                trace_json = excluded.trace_json,
                created_at = excluded.created_at
            """,
            (
                interaction_id,
                _encode_any_json(nodes),
                _encode_any_json(edges),
                _encode_any_json(trace),
                created_at,
            ),
        )
        conn.commit()

    trace_row = get_interaction_trace(interaction_id)
    if trace_row is None:
        raise RuntimeError("Failed to save interaction trace")
    return trace_row


def get_interaction_trace(interaction_id: str) -> dict[str, Any] | None:
    initialize_sqlite()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM interaction_traces WHERE interaction_id = ?",
            (interaction_id,),
        ).fetchone()
    return _row_to_interaction_trace(row) if row is not None else None


def get_full_saved_trace(interaction_id: str) -> dict[str, Any] | None:
    interaction = get_interaction(interaction_id)
    if interaction is None:
        return None

    trace_row = get_interaction_trace(interaction_id)
    if trace_row is None:
        return {
            "original_query": interaction["query_text"],
            "rewritten_query": interaction["rewritten_query"],
            "vector_hits": [],
            "seed_chunk_ids": [],
            "seed_node_ids": [],
            "retrieved_chunks": [],
            "graph_nodes": [],
            "graph_edges": interaction["edges_traversed"],
            "nodes_traversed": interaction["nodes_traversed"],
            "edges_traversed": interaction["edges_traversed"],
            "context_text": "",
            "latency_ms": {},
        }

    trace_payload = dict(trace_row["trace"])
    trace_payload.setdefault("original_query", interaction["query_text"])
    trace_payload.setdefault("rewritten_query", interaction["rewritten_query"])
    trace_payload.setdefault("graph_nodes", trace_row["nodes"])
    trace_payload.setdefault("graph_edges", trace_row["edges"])
    trace_payload.setdefault("nodes_traversed", interaction["nodes_traversed"])
    trace_payload.setdefault("edges_traversed", interaction["edges_traversed"])
    trace_payload.setdefault("vector_hits", [])
    trace_payload.setdefault("seed_chunk_ids", [])
    trace_payload.setdefault("seed_node_ids", [])
    trace_payload.setdefault("retrieved_chunks", [])
    trace_payload.setdefault("context_text", "")
    trace_payload.setdefault("latency_ms", {})
    return trace_payload


def update_interaction_rating(interaction_id: str, rating: int) -> bool:
    initialize_sqlite()
    with get_connection() as conn:
        updated_rows = conn.execute(
            "UPDATE interactions SET rating = ? WHERE id = ?",
            (rating, interaction_id),
        ).rowcount
        conn.commit()
    return updated_rows > 0


def _refresh_user_document_count(conn, user_id: str) -> None:
    document_count = conn.execute(
        "SELECT COUNT(*) AS count FROM documents WHERE user_id = ?",
        (user_id,),
    ).fetchone()["count"]
    conn.execute(
        "UPDATE users SET total_documents = ? WHERE id = ?",
        (document_count, user_id),
    )


def _stable_id(prefix: str, payload: str) -> str:
    return f"{prefix}:{hashlib.sha1(payload.encode('utf-8')).hexdigest()}"


def _compute_checksum(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def _encode_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _encode_any_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _decode_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _row_to_document(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "file_path": row["file_path"],
        "file_type": row["file_type"],
        "checksum": row["checksum"],
        "metadata": _decode_json(row["metadata_json"]),
        "ingested_at": row["ingested_at"],
        "updated_at": row["updated_at"],
        "chunk_count": row["chunk_count"] if "chunk_count" in row.keys() else None,
    }


def _row_to_chunk(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "document_id": row["document_id"],
        "text": row["text"],
        "position": row["position"],
        "file_path": row["file_path"],
        "file_type": row["file_type"],
        "metadata": _decode_json(row["metadata_json"]),
        "created_at": row["created_at"],
    }


def _row_to_concept(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "label": row["label"],
        "normalized_label": row["normalized_label"],
        "frequency": row["frequency"],
        "metadata": _decode_json(row["metadata_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_vector_mapping(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "faiss_id": row["faiss_id"],
        "chunk_id": row["chunk_id"],
        "document_id": row["document_id"],
        "created_at": row["created_at"],
    }


def _row_to_interaction(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "query_text": row["query_text"],
        "rewritten_query": row["rewritten_query"],
        "response_text": row["response_text"],
        "rating": row["rating"],
        "timestamp": row["timestamp"],
        "nodes_traversed": _decode_any_json(row["nodes_traversed_json"], default=[]),
        "edges_traversed": _decode_any_json(row["edges_traversed_json"], default=[]),
    }


def _row_to_interaction_trace(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "interaction_id": row["interaction_id"],
        "nodes": _decode_any_json(row["nodes_json"], default=[]),
        "edges": _decode_any_json(row["edges_json"], default=[]),
        "trace": _decode_any_json(row["trace_json"], default={}),
        "created_at": row["created_at"],
    }


def _decode_any_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
