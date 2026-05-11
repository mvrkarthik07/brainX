import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

type ViewKey = "chat" | "graph" | "documents" | "ingest" | "history" | "settings";

interface UIStore {
  sidebarCollapsed: boolean;
  activeView: ViewKey;
  inspectorOpen: boolean;
  toggleSidebar: () => void;
  setActiveView: (view: ViewKey) => void;
  setInspectorOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>()(
  immer((set) => ({
    sidebarCollapsed: false,
    activeView: "chat",
    inspectorOpen: true,
    toggleSidebar: () => {
      set((state) => {
        state.sidebarCollapsed = !state.sidebarCollapsed;
      });
    },
    setActiveView: (view) => {
      set((state) => {
        state.activeView = view;
      });
    },
    setInspectorOpen: (open) => {
      set((state) => {
        state.inspectorOpen = open;
      });
    },
  })),
);
