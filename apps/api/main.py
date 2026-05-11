from fastapi import FastAPI
from apps.api.routes.documents import router as documents_router
from apps.api.routes.health import router as health_router
from apps.api.routes.graph import router as graph_router
from apps.api.routes.ingest import router as ingest_router

app = FastAPI(
    title="BrainX API",
    description="API for BrainX cerebellum",
    version="0.1.0"
)

@app.get("/")

def root():

    return {

        "status": "ok",

        "message": "BrainX API root. Use /health or /docs."

    }

app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(documents_router)
app.include_router(graph_router)
