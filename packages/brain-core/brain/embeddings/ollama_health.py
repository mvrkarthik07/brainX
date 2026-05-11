import requests

from brain.config.settings import (
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_HEALTH_TIMEOUT_SECONDS,
    GENERATION_MODEL,
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
    required_models = {
        EMBEDDING_MODEL: False,
        GENERATION_MODEL: False,
    }

    try:
        response = requests.get(tags_url, timeout=OLLAMA_HEALTH_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return {
            "ok": False,
            "base_url": OLLAMA_BASE_URL,
            "error": f"Failed to reach Ollama tags endpoint: {exc}",
            "models": required_models,
            "installed": [],
        }
    except ValueError as exc:
        return {
            "ok": False,
            "base_url": OLLAMA_BASE_URL,
            "error": f"Invalid Ollama tags response: {exc}",
            "models": required_models,
            "installed": [],
        }

    installed_models = [model.get("name", "") for model in payload.get("models", []) if model.get("name")]
    for model_name in required_models:
        required_models[model_name] = _has_model(model_name, installed_models)

    return {
        "ok": all(required_models.values()),
        "base_url": OLLAMA_BASE_URL,
        "models": required_models,
        "installed": installed_models,
    }
