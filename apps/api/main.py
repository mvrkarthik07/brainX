from fastapi import FastAPI
from apps.api.routes.health import router as health_router

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

