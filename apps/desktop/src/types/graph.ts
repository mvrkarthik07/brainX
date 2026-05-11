export type GraphNodeType =
  | "document"
  | "concept"
  | "metanode"
  | "user"
  | "chunk"
  | "interaction";

export interface GraphNode {
  id: string;
  type: GraphNodeType;
  label: string;
  properties: Record<string, unknown>;
  x?: number;
  y?: number;
  weight: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface GraphNeighborhoodResponse {
  nodes: Array<{
    id: string;
    type: string;
    label?: string | null;
    properties: Record<string, unknown>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    effective_weight: number;
  }>;
}
