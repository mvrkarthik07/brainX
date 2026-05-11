from typing import Any


def assemble_context(
    *,
    original_query: str,
    rewritten_query: str,
    retrieved_chunks: list[dict[str, Any]],
    graph_edges: list[dict[str, Any]],
    max_context_chars: int = 12000,
) -> str:
    lines: list[str] = [
        "BRAINX LOCAL CONTEXT",
        "",
        "ORIGINAL QUERY:",
        original_query,
        "",
        "REWRITTEN QUERY:",
        rewritten_query,
        "",
        "RETRIEVED CHUNKS:",
    ]

    current_chars = sum(len(line) + 1 for line in lines)
    for chunk in retrieved_chunks:
        chunk_header = (
            f"[chunk_id={chunk['id']} document_id={chunk['document_id']} "
            f"title={chunk.get('document_title') or chunk['document_id']} score={chunk.get('score', 0.0):.4f}]"
        )
        chunk_body = chunk["text"]
        candidate_lines = [chunk_header, chunk_body, ""]
        candidate_chars = sum(len(line) + 1 for line in candidate_lines)
        if current_chars + candidate_chars > max_context_chars:
            break
        lines.extend(candidate_lines)
        current_chars += candidate_chars

    lines.extend(["GRAPH RELATIONSHIPS:"])
    for edge in graph_edges:
        edge_line = (
            f"edge_id={edge['id']} source={edge['source_id']} target={edge['target_id']} "
            f"type={edge['edge_type']} weight={edge['effective_weight']:.4f}"
        )
        if current_chars + len(edge_line) + 1 > max_context_chars:
            break
        lines.append(edge_line)
        current_chars += len(edge_line) + 1

    lines.extend(
        [
            "",
            "INSTRUCTIONS:",
            "Answer only using this local context. If the answer is not supported by this context, say the local knowledge base does not contain enough information.",
        ]
    )

    return "\n".join(lines)
