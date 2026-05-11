import sys

from brain.feedback.feedback_service import apply_feedback


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: .venv/bin/python scripts/dev/feedback_sample.py <interaction_id> <rating>")

    interaction_id = sys.argv[1]
    rating = int(sys.argv[2])
    print(apply_feedback(interaction_id, rating))


if __name__ == "__main__":
    main()
