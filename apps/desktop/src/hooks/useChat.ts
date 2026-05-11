import { useCallback } from "react";

import { submitQuery, submitRating } from "@/api/chat";
import { useChatStore } from "@/store/chatStore";
import type { QueryResponse } from "@/types/chat";

export function useChat() {
  const addMessage = useChatStore((state) => state.addMessage);
  const finalizeStreamingMessage = useChatStore((state) => state.finalizeStreamingMessage);
  const rateMessage = useChatStore((state) => state.rateMessage);
  const setStreaming = useChatStore((state) => state.setStreaming);
  const isStreaming = useChatStore((state) => state.isStreaming);

  const submit = useCallback(
    async (query: string) => {
      const trimmed = query.trim();
      if (!trimmed || isStreaming) {
        return;
      }

      const startTime = performance.now();
      addMessage({ role: "user", content: trimmed });
      setStreaming(true, "pending");

      try {
        const response = await submitQuery(trimmed);
        finalizeStreamingMessage(response, performance.now() - startTime);
        return response;
      } catch (error) {
        const fallback: QueryResponse = {
          interaction_id: "local-error",
          query: trimmed,
          rewritten_query: trimmed,
          answer: error instanceof Error ? error.message : "Query failed",
          sources: [],
          summary_trace: {
            vector_hits: 0,
            seed_chunks: 0,
            graph_nodes: 0,
            graph_edges: 0,
            edges_traversed: 0,
            latency_ms: {},
          },
        };
        finalizeStreamingMessage(fallback, performance.now() - startTime);
        throw error;
      }
    },
    [addMessage, finalizeStreamingMessage, isStreaming, setStreaming],
  );

  const rate = useCallback(
    async (interactionId: string, rating: 1 | 2 | 3 | 4 | 5) => {
      const response = await submitRating(interactionId, rating);
      rateMessage(interactionId, rating);
      return response;
    },
    [rateMessage],
  );

  return {
    submitQuery: submit,
    rateMessage: rate,
    isStreaming,
  };
}
