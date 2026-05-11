CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    total_queries INTEGER DEFAULT 0,
    total_documents INTEGER DEFAULT 0,
    preferences_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    checksum TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    ingested_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    normalized_label TEXT NOT NULL UNIQUE,
    frequency INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunk_concepts (
    chunk_id TEXT NOT NULL,
    concept_id TEXT NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(chunk_id, concept_id),
    FOREIGN KEY(chunk_id) REFERENCES chunks(id),
    FOREIGN KEY(concept_id) REFERENCES concepts(id)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    status TEXT NOT NULL,
    documents_added INTEGER NOT NULL DEFAULT 0,
    chunks_created INTEGER NOT NULL DEFAULT 0,
    concepts_extracted INTEGER NOT NULL DEFAULT 0,
    vectors_added INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    summary_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(user_id) REFERENCES users(id)
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

CREATE TABLE IF NOT EXISTS interaction_traces (
    interaction_id TEXT PRIMARY KEY,
    nodes_json TEXT NOT NULL DEFAULT '[]',
    edges_json TEXT NOT NULL DEFAULT '[]',
    trace_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(interaction_id) REFERENCES interactions(id)
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

CREATE TABLE IF NOT EXISTS graph_nodes (
    id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT,
    properties_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    base_weight REAL NOT NULL DEFAULT 1.0,
    feedback_delta REAL NOT NULL DEFAULT 0.0,
    effective_weight REAL NOT NULL DEFAULT 1.0,
    properties_json TEXT NOT NULL DEFAULT '{}',
    flagged INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(source_id) REFERENCES graph_nodes(id),
    FOREIGN KEY(target_id) REFERENCES graph_nodes(id),
    UNIQUE(source_id, target_id, edge_type)
);

CREATE TABLE IF NOT EXISTS graph_edge_feedback_events (
    id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL,
    interaction_id TEXT,
    rating INTEGER NOT NULL,
    delta REAL NOT NULL,
    previous_feedback_delta REAL NOT NULL,
    new_feedback_delta REAL NOT NULL,
    previous_effective_weight REAL NOT NULL,
    new_effective_weight REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(edge_id) REFERENCES graph_edges(id),
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

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunk_concepts_concept_id ON chunk_concepts(concept_id);
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interaction_traces_created_at ON interaction_traces(created_at);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_node_type ON graph_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_graph_edges_source_id ON graph_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_target_id ON graph_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_edge_type ON graph_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_graph_edge_feedback_events_edge_id ON graph_edge_feedback_events(edge_id);
CREATE INDEX IF NOT EXISTS idx_vector_mappings_chunk_id ON vector_mappings(chunk_id);
