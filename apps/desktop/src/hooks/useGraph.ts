import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";

import { getGraphNeighborhood } from "@/api/graph";
import { useGraphStore } from "@/store";
import type { GraphEdge, GraphNode } from "@/types/graph";
import { toGraphNodeType } from "@/utils/graph";

export function useGraph(centerNodeId: string, hops: number, limit = 100) {
  const setNodes = useGraphStore((state) => state.setNodes);
  const setEdges = useGraphStore((state) => state.setEdges);
  const setLoading = useGraphStore((state) => state.setLoading);

  const query = useQuery({
    queryKey: ["graph-neighborhood", centerNodeId, hops, limit],
    queryFn: () => getGraphNeighborhood(centerNodeId, hops, limit),
  });

  useEffect(() => {
    setLoading(query.isLoading);
  }, [query.isLoading, setLoading]);

  useEffect(() => {
    if (!query.data) {
      return;
    }

    const nodes: GraphNode[] = query.data.nodes.map((node) => ({
      id: node.id,
      type: toGraphNodeType(node.type),
      label: node.label || node.id,
      properties: node.properties,
      weight: Number(node.properties.weight ?? 1),
    }));

    const edges: GraphEdge[] = query.data.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type,
      weight: edge.effective_weight,
    }));

    setNodes(nodes);
    setEdges(edges);
  }, [query.data, setEdges, setNodes]);

  return query;
}
