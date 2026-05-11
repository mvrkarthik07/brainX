from brain.config.settings import REWRITE_MODEL
from brain.generation.ollama_llm import generate_text


def rewrite_query(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("rewrite_query requires a non-empty query")

    prompt = (
        "You rewrite user queries into concise semantic search terms for a local knowledge base. "
        "Preserve the user's topic. Do not broaden scope. Do not add technologies, projects, or concepts "
        "that are not already implied by the query. Keep it under 12 words. "
        "Return only the rewritten search query. No explanation.\n\n"
        f"User query: {query.strip()}"
    )

    try:
        rewritten = generate_text(prompt=prompt, model=REWRITE_MODEL, timeout=45)
    except Exception:
        return query.strip()

    rewritten = rewritten.strip().splitlines()[0].strip() if rewritten.strip() else ""
    if not rewritten:
        return query.strip()
    if len(rewritten.split()) > 12:
        return query.strip()
    return rewritten
