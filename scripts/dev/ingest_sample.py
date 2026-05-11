from pathlib import Path

from brain.ingestion.ingest_service import ingest_folder


def main() -> None:
    fixture_path = Path("tests/fixtures/docs")
    result = ingest_folder(fixture_path, recursive=True)
    print(result)


if __name__ == "__main__":
    main()
