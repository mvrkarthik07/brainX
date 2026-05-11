import ast
from dataclasses import dataclass, field
from pathlib import Path

import fitz

try:
    import mistletoe  # noqa: F401
except ImportError:  # pragma: no cover - optional parser path
    mistletoe = None


SUPPORTED_FILE_TYPES = {
    ".txt",
    ".md",
    ".pdf",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
}

CODE_FILE_TYPES = {".py", ".js", ".ts", ".tsx", ".jsx"}


@dataclass(slots=True)
class ParsedDocument:
    title: str
    file_path: str
    file_type: str
    raw_text: str
    metadata: dict = field(default_factory=dict)


def parse_file(path: str | Path) -> ParsedDocument:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {suffix or '<none>'}")

    if suffix == ".txt":
        return _parse_text_file(file_path)
    if suffix == ".md":
        return _parse_markdown_file(file_path)
    if suffix == ".pdf":
        return _parse_pdf_file(file_path)
    if suffix == ".py":
        return _parse_python_file(file_path)

    return _parse_source_file(file_path)


def _parse_text_file(file_path: Path) -> ParsedDocument:
    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    return ParsedDocument(
        title=file_path.stem,
        file_path=str(file_path),
        file_type=file_path.suffix.lower(),
        raw_text=raw_text,
        metadata={"parser": "plain_text"},
    )


def _parse_markdown_file(file_path: Path) -> ParsedDocument:
    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    parser_name = "mistletoe" if mistletoe is not None else "plain_text"
    headings = [
        line.strip().lstrip("#").strip()
        for line in raw_text.splitlines()
        if line.strip().startswith("#")
    ]
    return ParsedDocument(
        title=headings[0] if headings else file_path.stem,
        file_path=str(file_path),
        file_type=file_path.suffix.lower(),
        raw_text=raw_text,
        metadata={
            "parser": parser_name,
            "headings": headings,
        },
    )


def _parse_pdf_file(file_path: Path) -> ParsedDocument:
    with fitz.open(file_path) as document:
        page_texts = [page.get_text("text").strip() for page in document]

    non_empty_pages = [page_text for page_text in page_texts if page_text]
    if not non_empty_pages:
        raise ValueError(
            f"PDF '{file_path}' did not contain extractable text. Scanned/OCR PDFs are not supported yet."
        )

    raw_text = "\n\n".join(non_empty_pages)
    return ParsedDocument(
        title=file_path.stem,
        file_path=str(file_path),
        file_type=file_path.suffix.lower(),
        raw_text=raw_text,
        metadata={
            "parser": "pymupdf",
            "page_count": len(page_texts),
        },
    )


def _parse_python_file(file_path: Path) -> ParsedDocument:
    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    blocks: list[dict] = []

    try:
        parsed = ast.parse(raw_text)
        for node in ast.walk(parsed):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                block_text = ast.get_source_segment(raw_text, node) or ""
                if not block_text.strip():
                    continue
                blocks.append(
                    {
                        "name": getattr(node, "name", "<anonymous>"),
                        "kind": type(node).__name__,
                        "start_line": getattr(node, "lineno", None),
                        "end_line": getattr(node, "end_lineno", None),
                        "text": block_text,
                    }
                )
        parser_name = "python_ast"
    except SyntaxError:
        parser_name = "plain_text_fallback"

    return ParsedDocument(
        title=file_path.stem,
        file_path=str(file_path),
        file_type=file_path.suffix.lower(),
        raw_text=raw_text,
        metadata={
            "parser": parser_name,
            "code_blocks": blocks,
        },
    )


def _parse_source_file(file_path: Path) -> ParsedDocument:
    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    return ParsedDocument(
        title=file_path.stem,
        file_path=str(file_path),
        file_type=file_path.suffix.lower(),
        raw_text=raw_text,
        metadata={"parser": "plain_text_source"},
    )
