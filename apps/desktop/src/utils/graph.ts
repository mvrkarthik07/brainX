import type { GraphEdge, GraphNode, GraphNodeType } from "@/types/graph";

export function toGraphNodeType(value: string): GraphNodeType {
  const normalized = value.toLowerCase();
  if (
    normalized === "document" ||
    normalized === "concept" ||
    normalized === "metanode" ||
    normalized === "user" ||
    normalized === "chunk" ||
    normalized === "interaction"
  ) {
    return normalized;
  }
  return "concept";
}

export function getNodeRadius(node: GraphNode): number {
  const baseMap: Record<GraphNodeType, number> = {
    user: 14,
    metanode: 11,
    document: 8,
    concept: 6,
    interaction: 5,
    chunk: 3,
  };
  const base = baseMap[node.type] ?? 5;
  return base + Math.min(node.weight * 2, 6);
}

export function getNodeColor(type: GraphNodeType): string {
  const colorMap: Record<GraphNodeType, string> = {
    document: "var(--graph-node-document)",
    concept: "var(--graph-node-concept)",
    metanode: "var(--graph-node-metanode)",
    user: "var(--graph-node-user)",
    interaction: "var(--graph-node-interaction)",
    chunk: "var(--graph-node-chunk)",
  };
  return colorMap[type];
}

export function getEdgeColor(weight: number): string {
  if (weight >= 0.7) {
    return "var(--graph-edge-high-weight)";
  }
  if (weight >= 0.4) {
    return "var(--graph-edge-active)";
  }
  return "var(--graph-edge-default)";
}

export function buildGraphData(
  nodes: GraphNode[],
  edges: GraphEdge[],
  selectedNodeId: string | null,
) {
  const nodeIds = new Set(nodes.map((node) => node.id));
  const filteredEdges = edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target));
  const highlightedNodeIds = new Set<string>();
  if (selectedNodeId) {
    highlightedNodeIds.add(selectedNodeId);
    filteredEdges.forEach((edge) => {
      if (edge.source === selectedNodeId || edge.target === selectedNodeId) {
        highlightedNodeIds.add(edge.source);
        highlightedNodeIds.add(edge.target);
      }
    });
  }

  return {
    nodes,
    edges: filteredEdges,
    highlightedNodeIds,
  };
}
