CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    total_queries INTEGER DEFAULT 0,
    total_documents INTEGER DEFAULT 0,
    preferences_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS interactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    rewritten_query TEXT,
    response_text TEXT,
    rating INTEGER,
    timestamp TEXT NOT NULL,
    nodes_traversed_json TEXT NOT NULL DEFAULT '[]',
    edges_traversed_json TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS edge_feedback_deltas (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    edge_key TEXT NOT NULL,
    delta REAL NOT NULL,
    reason TEXT NOT NULL,
    interaction_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(interaction_id) REFERENCES interactions(id)
);

CREATE TABLE IF NOT EXISTS query_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    rewritten_query TEXT,
    latency_ms INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS vector_mappings (
    faiss_id INTEGER PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);