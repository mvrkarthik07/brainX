from typing import Any

from brain.generation.ollama_llm import generate_text
from brain.retrieval.retriever import retrieve
from brain.storage.sqlite_store import get_full_saved_trace, save_interaction, save_interaction_trace

INSUFFICIENT_CONTEXT_ANSWER = (
    "The local knowledge base does not contain enough information to answer this."
)


def answer_query(query: str) -> dict[str, Any]:
    retrieval_result = retrieve(query)
    if retrieval_result["insufficient_context"]:
        answer_text = INSUFFICIENT_CONTEXT_ANSWER
    else:
        prompt = (
            "You are BrainX, a local-first personal intelligence system. "
            "Answer only using the provided local context. Do not use external knowledge. "
            "If the context is insufficient, say: "
            "'The local knowledge base does not contain enough information to answer this.' "
            "Include source chunk IDs when relevant.\n\n"
            f"{retrieval_result['context_text']}\n\n"
            f"USER QUESTION:\n{query.strip()}"
        )
        answer_text = generate_text(prompt=prompt, timeout=120)

    interaction = save_interaction(
        query_text=query.strip(),
        rewritten_query=retrieval_result["rewritten_query"],
        response_text=answer_text,
        nodes_traversed=retrieval_result["nodes_traversed"],
        edges_traversed=retrieval_result["edges_traversed"],
    )

    save_interaction_trace(
        interaction_id=interaction["id"],
        nodes=retrieval_result["graph_nodes"],
        edges=retrieval_result["edges_traversed"],
        trace={
            "original_query": retrieval_result["original_query"],
            "rewritten_query": retrieval_result["rewritten_query"],
            "vector_hits": retrieval_result["vector_hits"],
            "seed_chunk_ids": retrieval_result["seed_chunk_ids"],
            "seed_node_ids": retrieval_result["seed_node_ids"],
            "retrieved_chunks": retrieval_result["retrieved_chunks"],
            "graph_nodes": retrieval_result["graph_nodes"],
            "graph_edges": retrieval_result["graph_edges"],
            "nodes_traversed": retrieval_result["nodes_traversed"],
            "edges_traversed": retrieval_result["edges_traversed"],
            "context_text": retrieval_result["context_text"],
            "latency_ms": retrieval_result["latency_ms"],
            "final_context_chunk_ids": [chunk["id"] for chunk in retrieval_result["retrieved_chunks"]],
            "insufficient_context": retrieval_result["insufficient_context"],
            "message": retrieval_result["message"],
            "low_confidence": retrieval_result["low_confidence"],
        },
    )

    sources = [
        {
            "chunk_id": chunk["id"],
            "document_id": chunk["document_id"],
            "document_title": chunk.get("document_title"),
            "score": chunk.get("score", 0.0),
        }
        for chunk in retrieval_result["retrieved_chunks"]
    ]

    return {
        "interaction_id": interaction["id"],
        "query": query.strip(),
        "rewritten_query": retrieval_result["rewritten_query"],
        "answer": answer_text,
        "sources": sources,
        "summary_trace": {
            "vector_hits": len(retrieval_result["vector_hits"]),
            "seed_chunks": len(retrieval_result["seed_chunk_ids"]),
            "graph_nodes": len(retrieval_result["graph_nodes"]),
            "graph_edges": len(retrieval_result["graph_edges"]),
            "edges_traversed": len(retrieval_result["edges_traversed"]),
            "latency_ms": retrieval_result["latency_ms"],
        },
    }


def get_interaction_trace_payload(interaction_id: str) -> dict[str, Any] | None:
    return get_full_saved_trace(interaction_id)
