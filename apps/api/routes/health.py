from fastapi import APIRouter
from brain.config.settings import GRAPH_BACKEND
from brain.embeddings.ollama_health import ollama_health
from brain.graph.factory import get_graph_store
from brain.storage.sqlite_store import sql_health
from brain.vector.faiss_store import faiss_health

router = APIRouter()

@router.get("/health")
def health_check():
    faiss_status = faiss_health()
    sql_status = sql_health()
    try:
        graph_status = get_graph_store().health()
    except Exception as exc:
        graph_status = {
            "ok": False,
            "backend": GRAPH_BACKEND,
            "error": str(exc),
        }
    ollama_status = ollama_health()
    all_ok = (
        sql_status["ok"]
        and faiss_status["ok"]
        and graph_status["ok"]
        and ollama_status["ok"]
    )

    return {
        "status": "ok" if all_ok else "degraded",
        "message": "BrainX cerebellum works",
        "api": True,
        "sql": sql_status,
        "faiss": faiss_status,
        "graph": graph_status,
        "ollama": ollama_status,
    }
