import { nanoid } from "nanoid";
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

import type { Message, QueryResponse, SourceNode } from "@/types/chat";

interface ChatStore {
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  currentQueryId: string | null;
  selectedMessageId: string | null;
  addMessage: (msg: Omit<Message, "id" | "timestamp">) => string;
  updateStreamingContent: (chunk: string) => void;
  finalizeStreamingMessage: (response: QueryResponse, latencyMs: number) => void;
  setStreaming: (isStreaming: boolean, queryId: string | null) => void;
  setSelectedMessageId: (messageId: string | null) => void;
  rateMessage: (queryId: string, rating: 1 | 2 | 3 | 4 | 5) => void;
  updateMessageSources: (queryId: string, sourceNodes: SourceNode[]) => void;
  clearHistory: () => void;
}

export const useChatStore = create<ChatStore>()(
  immer((set) => ({
    messages: [],
    isStreaming: false,
    streamingContent: "",
    currentQueryId: null,
    selectedMessageId: null,
    addMessage: (msg) => {
      const id = nanoid();
      set((state) => {
        state.messages.push({
          ...msg,
          id,
          timestamp: Date.now(),
        });
      });
      return id;
    },
    updateStreamingContent: (chunk) => {
      set((state) => {
        state.streamingContent = chunk;
      });
    },
    finalizeStreamingMessage: (response, latencyMs) => {
      set((state) => {
        state.messages.push({
          id: nanoid(),
          role: "assistant",
          content: response.answer,
          sourceNodes: response.sources,
          latencyMs,
          timestamp: Date.now(),
          queryId: response.interaction_id,
          rewrittenQuery: response.rewritten_query,
          summaryTrace: response.summary_trace,
        });
        state.isStreaming = false;
        state.streamingContent = "";
        state.currentQueryId = null;
      });
    },
    setStreaming: (isStreaming, queryId) => {
      set((state) => {
        state.isStreaming = isStreaming;
        state.currentQueryId = queryId;
        if (!isStreaming) {
          state.streamingContent = "";
        }
      });
    },
    setSelectedMessageId: (messageId) => {
      set((state) => {
        state.selectedMessageId = messageId;
      });
    },
    rateMessage: (queryId, rating) => {
      set((state) => {
        const target = state.messages.find((message) => message.queryId === queryId);
        if (target) {
          target.rating = rating;
        }
      });
    },
    updateMessageSources: (queryId, sourceNodes) => {
      set((state) => {
        const target = state.messages.find((message) => message.queryId === queryId);
        if (target) {
          target.sourceNodes = sourceNodes;
        }
      });
    },
    clearHistory: () => {
      set((state) => {
        state.messages = [];
        state.isStreaming = false;
        state.streamingContent = "";
        state.currentQueryId = null;
        state.selectedMessageId = null;
      });
    },
  })),
);
