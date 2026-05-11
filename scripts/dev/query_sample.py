from brain.generation.answer_service import answer_query


def main() -> None:
    result = answer_query("what did I write about rust performance?")
    print(result["interaction_id"])
    print(result["answer"])
    print(result["sources"])
    print(result["summary_trace"])



if __name__ == "__main__":
    main()
