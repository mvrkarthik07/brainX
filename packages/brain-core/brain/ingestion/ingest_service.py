from pathlib import Path

from brain.embeddings.ollama_embedder import embed_text
from brain.graph.graph_builder import build_graph_for_document
from brain.ingestion.chunker import chunk_document
from brain.ingestion.concept_extractor import extract_concepts
from brain.ingestion.parser import SUPPORTED_FILE_TYPES, parse_file
from brain.storage.sqlite_store import (
    create_chunk,
    create_concept,
    create_document,
    get_document,
    get_vector_mappings,
    link_chunk_concept,
)
from brain.vector.faiss_store import add_embedding


def ingest_file(path: str | Path) -> dict:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Path not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    parsed_document = parse_file(file_path)
    document = create_document(
        title=parsed_document.title,
        file_path=parsed_document.file_path,
        file_type=parsed_document.file_type,
        metadata=parsed_document.metadata,
        raw_text=parsed_document.raw_text,
    )

    chunk_inputs = chunk_document(parsed_document)
    stored_chunks: list[dict] = []
    concepts_by_chunk: dict[str, list[str]] = {}
    concepts_extracted = 0
    vectors_added = 0

    for chunk_input in chunk_inputs:
        chunk_record = create_chunk(
            document_id=document["id"],
            text=chunk_input.text,
            position=chunk_input.position,
            file_path=document["file_path"],
            file_type=document["file_type"],
            metadata=chunk_input.metadata,
        )
        stored_chunks.append(chunk_record)

        extracted_concepts = extract_concepts(chunk_input.text)
        concepts_by_chunk[chunk_record["id"]] = extracted_concepts
        concepts_extracted += len(extracted_concepts)

        for concept_label in extracted_concepts:
            concept_record = create_concept(concept_label)
            link_chunk_concept(chunk_record["id"], concept_record["id"])

        vector = embed_text(chunk_input.text)
        existing_vector_mappings = get_vector_mappings(
            chunk_id=chunk_record["id"],
            document_id=document["id"],
        )
        add_embedding(
            chunk_id=chunk_record["id"],
            document_id=document["id"],
            vector=vector,
        )
        if not existing_vector_mappings:
            vectors_added += 1

    graph_summary = build_graph_for_document(
        document=document,
        chunks=stored_chunks,
        concepts_by_chunk=concepts_by_chunk,
    )

    return {
        "documents_added": 1,
        "chunks_created": len(stored_chunks),
        "concepts_extracted": concepts_extracted,
        "vectors_added": vectors_added,
        "graph_nodes_upserted": graph_summary["nodes_upserted"],
        "graph_edges_upserted": graph_summary["edges_upserted"],
        "errors": [],
        "document": get_document(document["id"]),
    }


def ingest_folder(path: str | Path, recursive: bool = True) -> dict:
    folder_path = Path(path).expanduser().resolve()
    if not folder_path.exists():
        raise FileNotFoundError(f"Path not found: {folder_path}")
    if not folder_path.is_dir():
        raise ValueError(f"Path is not a folder: {folder_path}")

    iterator = folder_path.rglob("*") if recursive else folder_path.glob("*")
    summary = {
        "documents_added": 0,
        "chunks_created": 0,
        "concepts_extracted": 0,
        "vectors_added": 0,
        "graph_nodes_upserted": 0,
        "graph_edges_upserted": 0,
        "errors": [],
    }

    for candidate in iterator:
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in SUPPORTED_FILE_TYPES:
            continue

        try:
            result = ingest_file(candidate)
        except Exception as exc:
            summary["errors"].append({"path": str(candidate), "error": str(exc)})
            continue

        for key in (
            "documents_added",
            "chunks_created",
            "concepts_extracted",
            "vectors_added",
            "graph_nodes_upserted",
            "graph_edges_upserted",
        ):
            summary[key] += result[key]

    return summary
