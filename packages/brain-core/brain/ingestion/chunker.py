import re
from dataclasses import dataclass, field

from brain.ingestion.parser import CODE_FILE_TYPES, ParsedDocument

MIN_CHUNK_CHARS = 20
MAX_CHUNK_CHARS = 2400
CODE_LINE_WINDOW = 40
CODE_LINE_OVERLAP = 8


@dataclass(slots=True)
class ChunkInput:
    document_id: str | None
    text: str
    position: int
    metadata: dict = field(default_factory=dict)


def chunk_document(parsed_doc: ParsedDocument) -> list[ChunkInput]:
    if parsed_doc.file_type in CODE_FILE_TYPES:
        return _chunk_code_document(parsed_doc)
    return _chunk_prose_document(parsed_doc)


def _chunk_prose_document(parsed_doc: ParsedDocument) -> list[ChunkInput]:
    sentences = _split_sentences(parsed_doc.raw_text)
    if not sentences:
        return []

    chunks: list[ChunkInput] = []
    window_size = 3
    overlap = 1
    step = max(1, window_size - overlap)

    for start in range(0, len(sentences), step):
        window = sentences[start : start + window_size]
        if not window:
            continue
        chunk_text = " ".join(window).strip()
        if len(chunk_text) < MIN_CHUNK_CHARS:
            continue
        chunk_text = _cap_chunk_text(chunk_text)
        chunks.append(
            ChunkInput(
                document_id=None,
                text=chunk_text,
                position=len(chunks),
                metadata={
                    "source_kind": "prose_window",
                    "sentence_start": start,
                    "sentence_end": start + len(window) - 1,
                },
            )
        )
        if start + window_size >= len(sentences):
            break

    return chunks


def _chunk_code_document(parsed_doc: ParsedDocument) -> list[ChunkInput]:
    code_blocks = parsed_doc.metadata.get("code_blocks") or []
    chunks: list[ChunkInput] = []

    if code_blocks:
        for block in code_blocks:
            chunk_text = _cap_chunk_text((block.get("text") or "").strip())
            if len(chunk_text) < MIN_CHUNK_CHARS:
                continue
            chunks.append(
                ChunkInput(
                    document_id=None,
                    text=chunk_text,
                    position=len(chunks),
                    metadata={
                        "source_kind": "code_block",
                        "block_name": block.get("name"),
                        "block_kind": block.get("kind"),
                        "start_line": block.get("start_line"),
                        "end_line": block.get("end_line"),
                    },
                )
            )

    if chunks:
        return chunks

    lines = parsed_doc.raw_text.splitlines()
    if not lines:
        return []

    step = max(1, CODE_LINE_WINDOW - CODE_LINE_OVERLAP)
    for start in range(0, len(lines), step):
        window = lines[start : start + CODE_LINE_WINDOW]
        chunk_text = "\n".join(window).strip()
        if len(chunk_text) < MIN_CHUNK_CHARS:
            continue
        chunks.append(
            ChunkInput(
                document_id=None,
                text=_cap_chunk_text(chunk_text),
                position=len(chunks),
                metadata={
                    "source_kind": "code_window",
                    "start_line": start + 1,
                    "end_line": start + len(window),
                },
            )
        )
        if start + CODE_LINE_WINDOW >= len(lines):
            break

    return chunks


def _split_sentences(text: str) -> list[str]:
    cleaned_text = re.sub(r"\s+", " ", text).strip()
    if not cleaned_text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", cleaned_text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _cap_chunk_text(text: str) -> str:
    if len(text) <= MAX_CHUNK_CHARS:
        return text
    return text[:MAX_CHUNK_CHARS].rstrip()
