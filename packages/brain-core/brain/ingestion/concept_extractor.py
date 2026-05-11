import re
from collections import Counter

try:
    import yake
except ImportError:  # pragma: no cover - dependency fallback
    yake = None


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "have",
    "will",
    "function",
    "class",
    "return",
    "const",
    "let",
    "var",
}


def extract_concepts(text: str, max_concepts: int = 12) -> list[str]:
    normalized_text = text.strip()
    if not normalized_text:
        return []

    concepts = _extract_with_yake(normalized_text, max_concepts)
    if not concepts:
        concepts = _extract_with_fallback(normalized_text, max_concepts)

    cleaned: list[str] = []
    seen: set[str] = set()
    for concept in concepts:
        normalized_concept = _normalize_concept(concept)
        if not normalized_concept or normalized_concept in seen:
            continue
        seen.add(normalized_concept)
        cleaned.append(normalized_concept)
        if len(cleaned) >= max_concepts:
            break

    return cleaned


def _extract_with_yake(text: str, max_concepts: int) -> list[str]:
    if yake is None:
        return []

    extractor = yake.KeywordExtractor(
        lan="en",
        n=3,
        top=max_concepts * 3,
        dedupLim=0.9,
    )
    try:
        keywords = extractor.extract_keywords(text)
    except Exception:
        return []

    return [keyword for keyword, _score in keywords]


def _extract_with_fallback(text: str, max_concepts: int) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}", text.lower())
    filtered_tokens = [token for token in tokens if token not in STOPWORDS]
    if not filtered_tokens:
        return []

    phrases: Counter[str] = Counter(filtered_tokens)
    for size in (2, 3):
        for index in range(len(filtered_tokens) - size + 1):
            phrase = " ".join(filtered_tokens[index : index + size])
            if any(token in STOPWORDS for token in phrase.split()):
                continue
            phrases[phrase] += 1

    ranked = sorted(phrases.items(), key=lambda item: (-item[1], len(item[0])))
    return [phrase for phrase, _count in ranked[: max_concepts * 3]]


def _normalize_concept(concept: str) -> str | None:
    normalized = " ".join(concept.lower().strip().split())
    if len(normalized) < 2 or len(normalized) > 80:
        return None
    if re.fullmatch(r"[\W\d_]+", normalized):
        return None
    if len(normalized.split()) > 5:
        return None
    return normalized
