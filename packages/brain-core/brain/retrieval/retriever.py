from dataclasses import asdict
from time import perf_counter
from typing import Any

from brain.embeddings.ollama_embedder import embed_text
from brain.graph.factory import get_graph_store
from brain.retrieval.context_assembler import assemble_context
from brain.retrieval.query_rewriter import rewrite_query
from brain.storage.sqlite_store import (
    get_chunks_by_ids,
    get_concepts_for_chunk,
    get_documents_by_ids,
)
from brain.vector.faiss_store import search

DEFAULT_TOP_K_VECTOR = 5
DEFAULT_MIN_VECTOR_SCORE = 0.45
DEFAULT_MAX_HOPS = 2
DEFAULT_EDGE_THRESHOLD = 0.75
DEFAULT_HOP_DECAY = 0.65
DEFAULT_MAX_CONTEXT_CHUNKS = 4
DEFAULT_MAX_CONTEXT_CHARS = 8000
DEFAULT_MAX_GRAPH_NODES = 80
DEFAULT_MAX_GRAPH_EDGES = 80


def retrieve(
    query: str,
    *,
    top_k_vector: int = DEFAULT_TOP_K_VECTOR,
    min_vector_score: float = DEFAULT_MIN_VECTOR_SCORE,
    max_hops: int = DEFAULT_MAX_HOPS,
    edge_threshold: float = DEFAULT_EDGE_THRESHOLD,
    hop_decay: float = DEFAULT_HOP_DECAY,
    max_context_chunks: int = DEFAULT_MAX_CONTEXT_CHUNKS,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    max_graph_nodes: int = DEFAULT_MAX_GRAPH_NODES,
    max_graph_edges: int = DEFAULT_MAX_GRAPH_EDGES,
) -> dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("retrieve requires a non-empty query")

    timings: dict[str, float] = {}
    total_start = perf_counter()

    rewrite_start = perf_counter()
    rewritten_query = rewrite_query(query.strip())
    timings["rewrite_ms"] = round((perf_counter() - rewrite_start) * 1000, 2)

    embed_start = perf_counter()
    query_vector = embed_text(rewritten_query)
    timings["embed_ms"] = round((perf_counter() - embed_start) * 1000, 2)

    vector_start = perf_counter()
    raw_vector_hits = search(query_vector, top_k=top_k_vector)
    timings["vector_search_ms"] = round((perf_counter() - vector_start) * 1000, 2)

    if not raw_vector_hits:
        result = _empty_result(
            query=query,
            rewritten_query=rewritten_query,
            reason="The local knowledge base does not contain enough information to answer this.",
            timings=timings,
        )
        result["latency_ms"]["total_ms"] = round((perf_counter() - total_start) * 1000, 2)
        return result

    low_confidence = False
    vector_hits = [hit for hit in raw_vector_hits if hit.score >= min_vector_score]
    if not vector_hits and raw_vector_hits:
        vector_hits = raw_vector_hits[:1]
        low_confidence = True

    chunk_fetch_start = perf_counter()
    seed_chunk_ids = _ordered_unique([hit.chunk_id for hit in vector_hits])
    seed_document_ids = _ordered_unique([hit.document_id for hit in vector_hits])
    chunk_records = get_chunks_by_ids(seed_chunk_ids)
    document_records = get_documents_by_ids(seed_document_ids)
    document_map = {document["id"]: document for document in document_records}
    chunk_map = {chunk["id"]: chunk for chunk in chunk_records}
    timings["chunk_fetch_ms"] = round((perf_counter() - chunk_fetch_start) * 1000, 2)

    if not chunk_records:
        result = _empty_result(
            query=query,
            rewritten_query=rewritten_query,
            reason="The local knowledge base does not contain enough information to answer this.",
            vector_hits=vector_hits,
            timings=timings,
        )
        result["latency_ms"]["total_ms"] = round((perf_counter() - total_start) * 1000, 2)
        result["low_confidence"] = low_confidence
        return result

    graph_store = get_graph_store()
    graph_store.initialize()

    seed_node_ids: list[str] = []
    chunk_concepts: dict[str, list[dict[str, Any]]] = {}
    for chunk_id in seed_chunk_ids:
        if chunk_id not in chunk_map:
            continue
        chunk_node_id = graph_store.build_node_id("chunk", chunk_id)
        seed_node_ids.append(chunk_node_id)
        concepts = get_concepts_for_chunk(chunk_id)
        chunk_concepts[chunk_id] = concepts
        for concept in concepts:
            seed_node_ids.append(graph_store.build_node_id("concept", concept["id"]))

    seed_node_ids = _ordered_unique(seed_node_ids)

    traverse_start = perf_counter()
    traversal = graph_store.traverse(
        seed_node_ids=seed_node_ids,
        max_hops=max_hops,
        edge_threshold=edge_threshold,
        hop_decay=hop_decay,
        max_nodes=max_graph_nodes,
        max_edges=max_graph_edges,
    )
    timings["graph_traversal_ms"] = round((perf_counter() - traverse_start) * 1000, 2)

    graph_nodes = []
    for node_id in traversal["visited_nodes"]:
        node = graph_store.get_node(node_id)
        if node is not None:
            graph_nodes.append(node)

    vector_hit_map = {hit.chunk_id: hit for hit in vector_hits}
    retrieved_chunks = _select_context_chunks(
        seed_chunk_ids=seed_chunk_ids,
        chunk_map=chunk_map,
        document_map=document_map,
        vector_hit_map=vector_hit_map,
        min_vector_score=min_vector_score,
        max_context_chunks=max_context_chunks,
        low_confidence=low_confidence,
    )

    context_text = assemble_context(
        original_query=query,
        rewritten_query=rewritten_query,
        retrieved_chunks=retrieved_chunks,
        graph_edges=traversal["traversed_edges"],
        max_context_chars=max_context_chars,
    )

    timings["total_ms"] = round((perf_counter() - total_start) * 1000, 2)

    return {
        "original_query": query,
        "rewritten_query": rewritten_query,
        "vector_hits": [asdict(hit) for hit in vector_hits],
        "seed_chunk_ids": seed_chunk_ids,
        "seed_node_ids": seed_node_ids,
        "retrieved_chunks": retrieved_chunks,
        "graph_nodes": graph_nodes,
        "graph_edges": traversal["traversed_edges"],
        "nodes_traversed": traversal["visited_nodes"],
        "edges_traversed": traversal["traversed_edges"],
        "context_text": context_text,
        "latency_ms": timings,
        "insufficient_context": False,
        "low_confidence": low_confidence,
        "message": None,
    }


def _empty_result(
    *,
    query: str,
    rewritten_query: str,
    reason: str,
    vector_hits: list[Any] | None = None,
    timings: dict[str, float] | None = None,
) -> dict[str, Any]:
    return {
        "original_query": query,
        "rewritten_query": rewritten_query,
        "vector_hits": [asdict(hit) for hit in vector_hits] if vector_hits else [],
        "seed_chunk_ids": [],
        "seed_node_ids": [],
        "retrieved_chunks": [],
        "graph_nodes": [],
        "graph_edges": [],
        "nodes_traversed": [],
        "edges_traversed": [],
        "context_text": "",
        "latency_ms": dict(timings or {}),
        "insufficient_context": True,
        "low_confidence": False,
        "message": reason,
    }


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _select_context_chunks(
    *,
    seed_chunk_ids: list[str],
    chunk_map: dict[str, dict[str, Any]],
    document_map: dict[str, dict[str, Any]],
    vector_hit_map: dict[str, Any],
    min_vector_score: float,
    max_context_chunks: int,
    low_confidence: bool,
) -> list[dict[str, Any]]:
    if not seed_chunk_ids or max_context_chunks <= 0:
        return []

    top_vector_score = max(
        (vector_hit_map[chunk_id].score for chunk_id in seed_chunk_ids if chunk_id in vector_hit_map),
        default=0.0,
    )
    # Keep the answer context focused on chunks that are competitively relevant,
    # not every hit that merely cleared the absolute floor.
    context_score_floor = max(min_vector_score, top_vector_score * 0.85)

    document_scores: dict[str, float] = {}
    for chunk_id in seed_chunk_ids:
        hit = vector_hit_map.get(chunk_id)
        chunk = chunk_map.get(chunk_id)
        if hit is None or chunk is None:
            continue
        document_id = chunk["document_id"]
        document_scores[document_id] = document_scores.get(document_id, 0.0) + hit.score

    candidates: list[dict[str, Any]] = []
    for order_index, chunk_id in enumerate(seed_chunk_ids):
        chunk = chunk_map.get(chunk_id)
        hit = vector_hit_map.get(chunk_id)
        if chunk is None or hit is None:
            continue
        if hit.score < context_score_floor and not low_confidence:
            continue
        document = document_map.get(chunk["document_id"])
        candidates.append(
            {
                **chunk,
                "score": hit.score,
                "document_title": document["title"] if document is not None else None,
                "_document_score": document_scores.get(chunk["document_id"], 0.0),
                "_order_index": order_index,
            }
        )

    candidates.sort(
        key=lambda chunk: (
            -chunk["_document_score"],
            -chunk["score"],
            chunk["position"],
            chunk["_order_index"],
        )
    )

    trimmed = candidates[:max_context_chunks]
    for chunk in trimmed:
        chunk.pop("_document_score", None)
        chunk.pop("_order_index", None)
    return trimmed
