import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

import type { GraphEdge, GraphNode } from "@/types/graph";

interface GraphStore {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  highlightedNodes: Set<string>;
  focusDepth: number;
  isLoading: boolean;
  centerNodeId: string;
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  selectNode: (id: string | null) => void;
  highlightTraversal: (nodeIds: string[]) => void;
  setFocusDepth: (depth: number) => void;
  setLoading: (isLoading: boolean) => void;
  setCenterNodeId: (nodeId: string) => void;
}

export const useGraphStore = create<GraphStore>()(
  immer((set) => ({
    nodes: [],
    edges: [],
    selectedNodeId: null,
    highlightedNodes: new Set<string>(),
    focusDepth: 1,
    isLoading: false,
    centerNodeId: "user:default",
    setNodes: (nodes) => {
      set((state) => {
        state.nodes = nodes;
      });
    },
    setEdges: (edges) => {
      set((state) => {
        state.edges = edges;
      });
    },
    selectNode: (id) => {
      set((state) => {
        state.selectedNodeId = id;
      });
    },
    highlightTraversal: (nodeIds) => {
      set((state) => {
        state.highlightedNodes = new Set(nodeIds);
      });
    },
    setFocusDepth: (depth) => {
      set((state) => {
        state.focusDepth = depth;
      });
    },
    setLoading: (isLoading) => {
      set((state) => {
        state.isLoading = isLoading;
      });
    },
    setCenterNodeId: (nodeId) => {
      set((state) => {
        state.centerNodeId = nodeId;
      });
    },
  })),
);
