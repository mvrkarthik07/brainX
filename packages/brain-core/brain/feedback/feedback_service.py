import json

from brain.graph.factory import get_graph_store
from brain.storage.sqlite_store import get_connection, initialize_sqlite

RATING_DELTAS = {
    1: -0.3,
    2: -0.1,
    3: 0.0,
    4: 0.1,
    5: 0.3,
}


def apply_feedback(interaction_id: str, rating: int) -> dict:
    if rating not in RATING_DELTAS:
        raise ValueError("rating must be an integer between 1 and 5")

    initialize_sqlite()
    edge_ids = _load_traversed_edge_ids(interaction_id)
    delta = RATING_DELTAS[rating]
    should_flag = rating == 1
    graph_store = get_graph_store()

    edges_mutated = 0
    flagged_edges = 0

    for edge_id in edge_ids:
        update_result = graph_store.update_edge_feedback(
            edge_id=edge_id,
            delta=delta,
            interaction_id=interaction_id,
            rating=rating,
            flag=should_flag,
        )
        edges_mutated += 1
        if update_result["flagged"]:
            flagged_edges += 1

    with get_connection() as conn:
        updated_rows = conn.execute(
            "UPDATE interactions SET rating = ? WHERE id = ?",
            (rating, interaction_id),
        ).rowcount
        conn.commit()

    if updated_rows == 0:
        raise ValueError(f"Interaction '{interaction_id}' was not found")

    return {
        "interaction_id": interaction_id,
        "rating": rating,
        "delta": delta,
        "edges_mutated": edges_mutated,
        "flagged_edges": flagged_edges,
    }


def _load_traversed_edge_ids(interaction_id: str) -> list[str]:
    with get_connection() as conn:
        interaction_row = conn.execute(
            "SELECT edges_traversed_json FROM interactions WHERE id = ?",
            (interaction_id,),
        ).fetchone()
        if interaction_row is None:
            raise ValueError(f"Interaction '{interaction_id}' was not found")

        trace_row = conn.execute(
            "SELECT edges_json FROM interaction_traces WHERE interaction_id = ?",
            (interaction_id,),
        ).fetchone()

    if trace_row is not None:
        return _extract_edge_ids(trace_row["edges_json"])

    return _extract_edge_ids(interaction_row["edges_traversed_json"])


def _extract_edge_ids(raw_json: str) -> list[str]:
    try:
        payload = json.loads(raw_json or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid stored interaction trace JSON: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError("Stored interaction trace edges must be a JSON list")

    edge_ids: list[str] = []
    seen_edge_ids: set[str] = set()

    for item in payload:
        edge_id = None
        if isinstance(item, str):
            edge_id = item
        elif isinstance(item, dict):
            candidate = item.get("id")
            if isinstance(candidate, str):
                edge_id = candidate

        if edge_id and edge_id not in seen_edge_ids:
            seen_edge_ids.add(edge_id)
            edge_ids.append(edge_id)

    return edge_ids
