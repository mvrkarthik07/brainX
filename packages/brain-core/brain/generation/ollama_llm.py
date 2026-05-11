import requests

from brain.config.settings import (
    GENERATION_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_GENERATE_TIMEOUT_SECONDS,
    REWRITE_MODEL,
)


def generate_text(prompt: str, model: str | None = None) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("generate_text requires a non-empty prompt")

    selected_model = model or GENERATION_MODEL
    generate_url = f"{OLLAMA_BASE_URL}/api/generate"

    try:
        response = requests.post(
            generate_url,
            json={
                "model": selected_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=OLLAMA_GENERATE_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to generate text from Ollama model '{selected_model}': {exc}"
        ) from exc
    except ValueError as exc:
        raise RuntimeError(f"Invalid Ollama generation response: {exc}") from exc

    generated_text = payload.get("response")
    if not isinstance(generated_text, str) or not generated_text.strip():
        raise RuntimeError(
            f"Ollama model '{selected_model}' returned an empty generation response"
        )

    return generated_text.strip()


def rewrite_query(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("rewrite_query requires a non-empty query")

    prompt = (
        "Rewrite the user's query for retrieval.\n"
        "Preserve the original meaning.\n"
        "Return a single concise search query only.\n\n"
        f"User query: {query.strip()}"
    )

    return generate_text(prompt=prompt, model=REWRITE_MODEL)
