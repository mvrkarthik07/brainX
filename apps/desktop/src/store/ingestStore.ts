import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

import type { IngestQueueItem } from "@/types/ingest";

interface IngestStore {
  queue: IngestQueueItem[];
  addItem: (item: IngestQueueItem) => void;
  updateItem: (id: string, patch: Partial<IngestQueueItem>) => void;
  clearCompleted: () => void;
}

export const useIngestStore = create<IngestStore>()(
  immer((set) => ({
    queue: [],
    addItem: (item) => {
      set((state) => {
        state.queue.unshift(item);
      });
    },
    updateItem: (id, patch) => {
      set((state) => {
        const target = state.queue.find((item) => item.id === id);
        if (target) {
          Object.assign(target, patch);
        }
      });
    },
    clearCompleted: () => {
      set((state) => {
        state.queue = state.queue.filter((item) => item.status !== "done");
      });
    },
  })),
);
