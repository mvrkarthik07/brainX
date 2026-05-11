import requests

from brain.config.settings import GENERATION_MODEL, OLLAMA_BASE_URL, OLLAMA_GENERATE_TIMEOUT_SECONDS


def generate_text(prompt: str, model: str | None = None, timeout: int = 120) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("generate_text requires a non-empty prompt")

    selected_model = model or GENERATION_MODEL
    generate_url = f"{OLLAMA_BASE_URL}/api/generate"
    request_timeout = timeout if timeout > 0 else OLLAMA_GENERATE_TIMEOUT_SECONDS

    try:
        response = requests.post(
            generate_url,
            json={
                "model": selected_model,
                "prompt": prompt.strip(),
                "stream": False,
            },
            timeout=request_timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to generate text from Ollama model '{selected_model}' via {generate_url}: {exc}"
        ) from exc
    except ValueError as exc:
        raise RuntimeError(f"Invalid Ollama generation response: {exc}") from exc

    generated_text = payload.get("response")
    if not isinstance(generated_text, str) or not generated_text.strip():
        raise RuntimeError(f"Ollama model '{selected_model}' returned an empty response")

    return generated_text.strip()
