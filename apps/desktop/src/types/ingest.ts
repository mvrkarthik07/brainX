export interface FileError {
  path: string;
  error: string;
}

export interface DocumentRecord {
  id: string;
  user_id: string;
  title?: string | null;
  file_path: string;
  file_type: string;
  checksum?: string | null;
  metadata: Record<string, unknown>;
  ingested_at: string;
  updated_at: string;
  chunk_count?: number | null;
}

export interface ChunkRecord {
  id: string;
  document_id: string;
  text: string;
  position: number;
  file_path: string;
  file_type: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface IngestionSummary {
  documents_added: number;
  chunks_created: number;
  concepts_extracted: number;
  vectors_added: number;
  graph_nodes_upserted: number;
  graph_edges_upserted: number;
  errors: FileError[];
  document?: DocumentRecord | null;
}

export interface DocumentListResponse {
  documents: DocumentRecord[];
}

export interface DocumentDetailResponse {
  document: DocumentRecord;
  chunks: ChunkRecord[];
}

export interface IngestQueueItem {
  id: string;
  kind: "file" | "folder";
  path: string;
  recursive?: boolean;
  status: "queued" | "running" | "done" | "error";
  summary?: IngestionSummary;
  error?: string;
}
