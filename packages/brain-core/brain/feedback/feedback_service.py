import json

from brain.graph.factory import get_graph_store
from brain.storage.sqlite_store import (
    get_interaction,
    get_full_saved_trace,
    get_interaction_trace,
    initialize_sqlite,
    update_interaction_rating,
)

RATING_DELTAS = {
    1: -0.3,
    2: -0.1,
    3: 0.0,
    4: 0.1,
    5: 0.3,
}

ALLOWED_FEEDBACK_EDGE_TYPES = {
    "HAS_CONCEPT",
    "CO_OCCURS",
    "SEMANTICALLY_SIMILAR",
    "QUERIED_BY",
    "RATED_HIGH",
    "USER_RELEVANCE",
}


def apply_feedback(interaction_id: str, rating: int) -> dict:
    if rating not in RATING_DELTAS:
        raise ValueError("rating must be an integer between 1 and 5")

    initialize_sqlite()
    interaction = get_interaction(interaction_id)
    if interaction is None:
        raise ValueError(f"Interaction '{interaction_id}' was not found")

    traversed_edges = _load_traversed_edges(interaction_id)
    delta = RATING_DELTAS[rating]
    should_flag = rating == 1
    graph_store = get_graph_store()

    edges_mutated = 0
    edges_skipped = 0
    flagged_edges = 0

    seen_edge_ids: set[str] = set()
    for edge in traversed_edges:
        edge_id = edge.get("id")
        edge_type = edge.get("edge_type")
        if not isinstance(edge_id, str) or edge_id in seen_edge_ids:
            continue
        seen_edge_ids.add(edge_id)

        if edge_type not in ALLOWED_FEEDBACK_EDGE_TYPES:
            edges_skipped += 1
            continue

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

    if not update_interaction_rating(interaction_id, rating):
        raise ValueError(f"Interaction '{interaction_id}' was not found")

    return {
        "interaction_id": interaction_id,
        "rating": rating,
        "delta": delta,
        "edges_mutated": edges_mutated,
        "edges_skipped": edges_skipped,
        "flagged_edges": flagged_edges,
    }


def _load_traversed_edges(interaction_id: str) -> list[dict]:
    full_trace = get_full_saved_trace(interaction_id)
    if full_trace is not None:
        edges = full_trace.get("edges_traversed", [])
        if isinstance(edges, list):
            return [edge for edge in edges if isinstance(edge, dict)]

    trace = get_interaction_trace(interaction_id)
    if trace is not None and isinstance(trace.get("edges"), list):
        return [edge for edge in trace["edges"] if isinstance(edge, dict)]

    interaction = get_interaction(interaction_id)
    if interaction is None:
        raise ValueError(f"Interaction '{interaction_id}' was not found")

    edges = interaction.get("edges_traversed", [])
    if isinstance(edges, list):
        return [edge for edge in edges if isinstance(edge, dict)]
    return []
