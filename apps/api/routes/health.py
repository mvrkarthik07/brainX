from fastapi import APIRouter
from brain.graph.memgraph_store import memgraph_health
from brain.storage.sqlite_store import sql_health
from brain.vector.faiss_store import faiss_health

router = APIRouter()

@router.get("/health")
def health_check():
    faiss_status = faiss_health()
    sql_status = sql_health()
    memgraph_status = memgraph_health()
    all_ok = sql_status["ok"] and faiss_status["ok"] and memgraph_status["ok"]

    return {
        "status": "ok" if all_ok else "degraded",
        "message": "BrainX cerebellum works",
        "api": True,
        "sql": sql_status,
        "faiss": faiss_status,
        "memgraph": memgraph_status,
    }
