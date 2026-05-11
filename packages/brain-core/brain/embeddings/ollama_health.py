import requests

from brain.config.settings import (
    EMBEDDING_MODEL,
    GENERATION_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_HEALTH_TIMEOUT_SECONDS,
    REWRITE_MODEL,
)


def _model_matches(target_model: str, installed_name: str) -> bool:
    target_base = target_model.split(":", maxsplit=1)[0]
    installed_base = installed_name.split(":", maxsplit=1)[0]

    return (
        installed_name == target_model
        or installed_name.startswith(f"{target_model}:")
        or installed_base == target_base
    )


def _has_model(target_model: str, installed_models: list[str]) -> bool:
    return any(_model_matches(target_model, model_name) for model_name in installed_models)


def ollama_health() -> dict:
    tags_url = f"{OLLAMA_BASE_URL}/api/tags"

    try:
        response = requests.get(tags_url, timeout=OLLAMA_HEALTH_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return {
            "ok": False,
            "base_url": OLLAMA_BASE_URL,
            "server_reachable": False,
            "error": f"Failed to reach Ollama tags endpoint: {exc}",
        }
    except ValueError as exc:
        return {
            "ok": False,
            "base_url": OLLAMA_BASE_URL,
            "server_reachable": False,
            "error": f"Invalid Ollama tags response: {exc}",
        }

    installed_models = [model.get("name", "") for model in payload.get("models", []) if model.get("name")]
    embedding_model_exists = _has_model(EMBEDDING_MODEL, installed_models)
    rewrite_model_exists = _has_model(REWRITE_MODEL, installed_models)
    generation_model_exists = _has_model(GENERATION_MODEL, installed_models)

    all_ok = embedding_model_exists and rewrite_model_exists and generation_model_exists

    return {
        "ok": all_ok,
        "base_url": OLLAMA_BASE_URL,
        "server_reachable": True,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_model_exists": embedding_model_exists,
        "rewrite_model": REWRITE_MODEL,
        "rewrite_model_exists": rewrite_model_exists,
        "generation_model": GENERATION_MODEL,
        "generation_model_exists": generation_model_exists,
        "installed_models": installed_models,
    }
