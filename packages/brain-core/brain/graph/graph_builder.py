from typing import Any

from brain.graph.factory import get_graph_store
from brain.storage.sqlite_store import DEFAULT_USER_ID


def build_graph_for_document(document: dict, chunks: list[dict], concepts_by_chunk: dict[str, list[str]]) -> dict:
    graph_store = get_graph_store()
    graph_store.initialize()

    touched_nodes: set[str] = set()
    touched_edges: set[str] = set()

    user_node = graph_store.upsert_user(DEFAULT_USER_ID, label="Default User")
    touched_nodes.add(user_node["id"])

    document_node = graph_store.upsert_document(
        document["id"],
        label=document.get("title") or document["id"],
        properties={
            "document_id": document["id"],
            "file_path": document["file_path"],
            "file_type": document["file_type"],
        },
    )
    touched_nodes.add(document_node["id"])

    ingested_edge = graph_store.upsert_edge(
        user_node["id"],
        document_node["id"],
        "INGESTED",
        base_weight=1.0,
        properties={"document_id": document["id"]},
    )
    touched_edges.add(ingested_edge["id"])

    for chunk in chunks:
        chunk_node = graph_store.upsert_chunk(
            chunk["id"],
            label=f"chunk-{chunk['position']}",
            properties={
                "chunk_id": chunk["id"],
                "document_id": chunk["document_id"],
                "position": chunk["position"],
                "file_type": chunk["file_type"],
            },
        )
        touched_nodes.add(chunk_node["id"])

        document_chunk_edge = graph_store.upsert_edge(
            document_node["id"],
            chunk_node["id"],
            "HAS_CHUNK",
            base_weight=1.0,
            properties={"document_id": document["id"], "chunk_id": chunk["id"]},
        )
        touched_edges.add(document_chunk_edge["id"])

        concepts = concepts_by_chunk.get(chunk["id"], [])
        concept_node_ids: list[str] = []
        for concept_label in concepts:
            concept_node = graph_store.upsert_concept(
                concept_label,
                label=concept_label,
                properties={"label": concept_label},
            )
            touched_nodes.add(concept_node["id"])
            concept_node_ids.append(concept_node["id"])

            chunk_concept_edge = graph_store.upsert_edge(
                chunk_node["id"],
                concept_node["id"],
                "HAS_CONCEPT",
                base_weight=0.75,
                properties={"chunk_id": chunk["id"], "concept_label": concept_label},
            )
            touched_edges.add(chunk_concept_edge["id"])

        for index, source_concept_id in enumerate(concept_node_ids):
            for target_concept_id in concept_node_ids[index + 1 :]:
                co_occurs_edge = graph_store.upsert_edge(
                    source_concept_id,
                    target_concept_id,
                    "CO_OCCURS",
                    base_weight=0.55,
                    properties={"document_id": document["id"], "chunk_id": chunk["id"]},
                )
                touched_edges.add(co_occurs_edge["id"])

    return {
        "nodes_upserted": len(touched_nodes),
        "edges_upserted": len(touched_edges),
    }
