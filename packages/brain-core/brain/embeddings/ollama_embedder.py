import numpy as np
import requests

from brain.config.settings import (
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_TIMEOUT_SECONDS,
)


def _normalize_embedding(vector: list[float]) -> list[float]:
    array = np.asarray(vector, dtype=np.float32)

    if array.shape != (EMBEDDING_DIM,):
        raise ValueError(
            f"Ollama embedding dimension mismatch: expected {EMBEDDING_DIM}, got {array.shape[0]}"
        )

    norm = np.linalg.norm(array)
    if norm == 0:
        raise ValueError("Ollama returned a zero-length embedding vector")

    return (array / norm).tolist()


def _request_embeddings(text_input: str | list[str]) -> list[list[float]]:
    embed_url = f"{OLLAMA_BASE_URL}/api/embed"

    try:
        response = requests.post(
            embed_url,
            json={"model": EMBEDDING_MODEL, "input": text_input},
            timeout=OLLAMA_EMBED_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to request Ollama embeddings from {embed_url}: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Invalid Ollama embeddings response: {exc}") from exc

    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list) or not embeddings:
        raise RuntimeError("Ollama embeddings response did not include any embeddings")

    normalized_embeddings = []
    for index, embedding in enumerate(embeddings):
        if not isinstance(embedding, list):
            raise RuntimeError(f"Ollama embedding at index {index} was not a vector list")
        normalized_embeddings.append(_normalize_embedding(embedding))

    return normalized_embeddings


def embed_text(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("embed_text requires non-empty text")

    return _request_embeddings(text)[0]


def embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        raise ValueError("embed_batch requires at least one text")

    cleaned_texts = []
    for index, text in enumerate(texts):
        if not text or not text.strip():
            raise ValueError(f"embed_batch received empty text at index {index}")
        cleaned_texts.append(text)

    embeddings = _request_embeddings(cleaned_texts)
    if len(embeddings) != len(cleaned_texts):
        raise RuntimeError(
            f"Ollama embedding count mismatch: expected {len(cleaned_texts)}, got {len(embeddings)}"
        )

    return embeddings
