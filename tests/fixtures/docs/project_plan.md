# Project Plan

BrainX ingestion should land before full retrieval orchestration.
The first vertical slice writes documents, chunks, concepts, vectors, and graph edges locally.
Graph traversal and grounded answer generation come after the memory-writing path is stable.

## Acceptance

The API should ingest a local folder without cloud services.
The graph neighborhood endpoint should return real SQLite-backed nodes and edges.
