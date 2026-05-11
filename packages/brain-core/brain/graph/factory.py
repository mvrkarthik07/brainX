from brain.config.settings import GRAPH_BACKEND
from brain.graph.base import GraphStore
from brain.graph.sqlite_graph_store import SQLiteGraphStore


def get_graph_store() -> GraphStore:
    backend = GRAPH_BACKEND.strip().lower()

    if backend == "sqlite":
        return SQLiteGraphStore()

    if backend == "memgraph":
        from brain.graph.memgraph_store import MemgraphGraphStore

        return MemgraphGraphStore()

    raise ValueError(f"Unsupported GRAPH_BACKEND '{GRAPH_BACKEND}'")
