import sys

from brain.generation.answer_service import get_interaction_trace_payload


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: .venv/bin/python scripts/dev/trace_sample.py <interaction_id>")

    interaction_id = sys.argv[1]
    trace = get_interaction_trace_payload(interaction_id)
    if trace is None:
        raise SystemExit(f"Interaction '{interaction_id}' was not found")
    print(trace)


if __name__ == "__main__":
    main()
