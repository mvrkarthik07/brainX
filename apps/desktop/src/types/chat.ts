export interface SourceNode {
  chunk_id: string;
  document_id: string;
  document_title?: string | null;
  score: number;
}

export interface QuerySummaryTrace {
  vector_hits: number;
  seed_chunks: number;
  graph_nodes: number;
  graph_edges: number;
  edges_traversed: number;
  latency_ms: Record<string, number>;
}

export interface QueryResponse {
  interaction_id: string;
  query: string;
  rewritten_query: string;
  answer: string;
  sources: SourceNode[];
  summary_trace: QuerySummaryTrace;
}

export interface InteractionTrace {
  original_query: string;
  rewritten_query: string;
  vector_hits: Array<{
    chunk_id: string;
    document_id: string;
    faiss_id: number;
    score: number;
  }>;
  seed_chunk_ids: string[];
  seed_node_ids: string[];
  retrieved_chunks: Array<{
    id: string;
    document_id: string;
    document_title?: string | null;
    text: string;
    score: number;
  }>;
  graph_nodes: Array<{
    id: string;
    node_type: string;
    label?: string | null;
    properties: Record<string, unknown>;
  }>;
  graph_edges: Array<{
    id: string;
    source_id: string;
    target_id: string;
    edge_type: string;
    effective_weight: number;
  }>;
  nodes_traversed: string[];
  edges_traversed: Array<{
    id: string;
    source_id: string;
    target_id: string;
    edge_type: string;
    effective_weight: number;
  }>;
  context_text: string;
  latency_ms: Record<string, number>;
  insufficient_context?: boolean;
  message?: string | null;
  low_confidence?: boolean;
}

export interface FeedbackResponse {
  interaction_id: string;
  rating: number;
  delta: number;
  edges_mutated: number;
  edges_skipped: number;
  flagged_edges: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sourceNodes?: SourceNode[];
  rating?: 1 | 2 | 3 | 4 | 5;
  latencyMs?: number;
  timestamp: number;
  isStreaming?: boolean;
  queryId?: string;
  rewrittenQuery?: string;
  summaryTrace?: QuerySummaryTrace;
}
