import requests

from brain.config.settings import (
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_TIMEOUT_SECONDS,
)


def _validate_embedding(vector: object) -> list[float]:
    if not isinstance(vector, list):
        raise RuntimeError("Ollama embedding response was not a vector list")
    if len(vector) != EMBEDDING_DIM:
        raise ValueError(
            f"Ollama embedding dimension mismatch: expected {EMBEDDING_DIM}, got {len(vector)}"
        )

    validated: list[float] = []
    for index, value in enumerate(vector):
        if not isinstance(value, (int, float)):
            raise RuntimeError(f"Ollama embedding value at index {index} was not numeric")
        validated.append(float(value))

    return validated


def _request_embedding(text: str) -> list[float]:
    embed_url = f"{OLLAMA_BASE_URL}/api/embed"

    try:
        response = requests.post(
            embed_url,
            json={"model": EMBEDDING_MODEL, "input": text},
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
    if len(embeddings) != 1:
        raise RuntimeError(f"Expected exactly one embedding, got {len(embeddings)}")

    return _validate_embedding(embeddings[0])


def embed_text(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("embed_text requires non-empty text")

    return _request_embedding(text.strip())


def embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        raise ValueError("embed_batch requires at least one text")

    embeddings: list[list[float]] = []
    for index, text in enumerate(texts):
        if not text or not text.strip():
            raise ValueError(f"embed_batch received empty text at index {index}")
        embeddings.append(_request_embedding(text.strip()))

    return embeddings
