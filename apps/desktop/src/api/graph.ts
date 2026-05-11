import type { GraphNeighborhoodResponse } from "@/types/graph";
import { request } from "@/api/client";

export function getGraphNeighborhood(nodeId: string, hops = 1, limit = 100) {
  const params = new URLSearchParams({
    node_id: nodeId,
    hops: String(hops),
    limit: String(limit),
  });
  return request<GraphNeighborhoodResponse>(`/graph/neighborhood?${params.toString()}`);
}
