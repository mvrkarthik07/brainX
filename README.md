# BrainX

BrainX is a local-first personal intelligence system where the persistent local state is the intelligence layer and the LLM is the language interface.

## Current Architecture

- FastAPI local backend
- SQLite for users, documents, chunks, concepts, graph state, interactions, and feedback traces
- FAISS for local vector search
- Ollama for local embeddings and local generation
- SQLite graph backend as the production default
- No Docker requirement

## Local Requirements

- Python virtual environment at `.venv`
- Ollama running locally
- Models pulled locally:
  - `nomic-embed-text`
  - `qwen2.5:3b`

## Run Backend

```bash
.venv/bin/uvicorn apps.api.main:app --reload
```

## Check Health

```bash
.venv/bin/python scripts/dev/check_health.py
curl -i http://127.0.0.1:8000/health
```

## Ingest Sample Docs

```bash
.venv/bin/python scripts/dev/ingest_sample.py
curl -X POST http://127.0.0.1:8000/ingest/folder \
  -H "Content-Type: application/json" \
  -d '{"path":"tests/fixtures/docs","recursive":true}'
```

## Query Sample

```bash
.venv/bin/python scripts/dev/query_sample.py
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"what did I write about rust performance?"}'
```

## Feedback Sample

```bash
.venv/bin/python scripts/dev/feedback_sample.py <interaction_id> 5
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"interaction_id":"<interaction_id>","rating":5}'
```

## Frontend Plan

- Final UI target is a local Tauri desktop app
- Frontend architecture notes live in [docs/frontend_architecture.md](/Users/karthik/brainX/docs/frontend_architecture.md)
- Graph Explorer will consume the real `/graph/neighborhood` endpoint

## Notes

- No cloud APIs
- No external LLM APIs
- No Docker or default Memgraph dependency
- All state remains on the user’s device
