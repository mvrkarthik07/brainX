from brain.embeddings.ollama_health import ollama_health
from brain.graph.factory import get_graph_store
from brain.storage.sqlite_store import sql_health
from brain.vector.faiss_store import faiss_health


def main() -> None:
    print({"sql": sql_health()})
    print({"faiss": faiss_health()})
    print({"graph": get_graph_store().health()})
    print({"ollama": ollama_health()})


if __name__ == "__main__":
    main()
