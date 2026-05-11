export interface HealthStatus {
  ok: boolean;
  [key: string]: unknown;
}

export interface BrainXHealthResponse {
  status: "ok" | "degraded";
  message: string;
  api: boolean;
  sql: HealthStatus;
  faiss: HealthStatus & {
    dimension?: number;
    vectors?: number;
    index_type?: string;
  };
  graph: HealthStatus & {
    backend?: string;
    nodes?: number;
    edges?: number;
    default_user_exists?: boolean;
  };
  ollama: HealthStatus & {
    base_url?: string;
    installed?: string[];
    models?: Record<string, boolean>;
  };
}

export interface APIErrorPayload {
  detail?: string;
}
