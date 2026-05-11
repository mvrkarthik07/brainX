from dataclasses import asdict, dataclass

import faiss
import numpy as np

from brain.config.settings import DEFAULT_USER_DIR, EMBEDDING_DIM, FAISS_INDEX_PATH
from brain.storage.sqlite_store import get_vector_mappings, map_vector


@dataclass(slots=True)
class VectorHit:
    faiss_id: int
    chunk_id: str
    document_id: str
    score: float


def create_empty_index() -> faiss.Index:
    return faiss.IndexFlatIP(EMBEDDING_DIM)


def save_index(index: faiss.Index) -> None:
    DEFAULT_USER_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))


def load_or_create_index() -> faiss.Index:
    DEFAULT_USER_DIR.mkdir(parents=True, exist_ok=True)
    if FAISS_INDEX_PATH.exists():
        return faiss.read_index(str(FAISS_INDEX_PATH))

    index = create_empty_index()
    save_index(index)
    return index


def normalize_vector(vector: list[float] | np.ndarray) -> np.ndarray:
    array = np.asarray(vector, dtype=np.float32)
    if array.shape != (EMBEDDING_DIM,):
        raise ValueError(f"Vector dimension mismatch: expected {EMBEDDING_DIM}, got {array.shape[0]}")

    norm = np.linalg.norm(array)
    if norm == 0:
        raise ValueError("Cannot normalize a zero-length vector")
    return array / norm


def add_embedding(chunk_id: str, document_id: str, vector: list[float]) -> int:
    existing_mappings = get_vector_mappings(chunk_id=chunk_id, document_id=document_id)
    if existing_mappings:
        return int(existing_mappings[0]["faiss_id"])

    index = load_or_create_index()
    normalized = normalize_vector(vector).reshape(1, EMBEDDING_DIM)
    faiss_id = int(index.ntotal)
    index.add(normalized)
    save_index(index)
    map_vector(faiss_id=faiss_id, chunk_id=chunk_id, document_id=document_id)
    return faiss_id


def search(vector: list[float], top_k: int = 8) -> list[VectorHit]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    index = load_or_create_index()
    if index.ntotal == 0:
        return []

    normalized = normalize_vector(vector).reshape(1, EMBEDDING_DIM)
    scores, ids = index.search(normalized, min(top_k, index.ntotal))
    hits: list[VectorHit] = []

    for faiss_id, score in zip(ids[0], scores[0], strict=False):
        if int(faiss_id) < 0:
            continue
        mappings = get_vector_mappings(faiss_id=int(faiss_id))
        if not mappings:
            continue
        mapping = mappings[0]
        hits.append(
            VectorHit(
                faiss_id=int(faiss_id),
                chunk_id=mapping["chunk_id"],
                document_id=mapping["document_id"],
                score=float(score),
            )
        )

    return hits


def faiss_health() -> dict:
    try:
        index = load_or_create_index()
        return {
            "ok": True,
            "index_path": str(FAISS_INDEX_PATH),
            "dimension": index.d,
            "vectors": index.ntotal,
            "index_type": type(index).__name__,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }


def vector_hits_to_dicts(hits: list[VectorHit]) -> list[dict]:
    return [asdict(hit) for hit in hits]
