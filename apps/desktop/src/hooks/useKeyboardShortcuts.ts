import { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";

import { useGraphStore, useUIStore } from "@/store";

export function useKeyboardShortcuts() {
  const navigate = useNavigate();
  const setActiveView = useUIStore((state) => state.setActiveView);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const selectNode = useGraphStore((state) => state.selectNode);
  const focusDepth = useGraphStore((state) => state.focusDepth);
  const setFocusDepth = useGraphStore((state) => state.setFocusDepth);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      const isCommand = event.metaKey || event.ctrlKey;
      if (isCommand && event.key.toLowerCase() === "g") {
        event.preventDefault();
        setActiveView("graph");
        void navigate({ to: "/graph" });
      } else if (isCommand && event.key.toLowerCase() === "i") {
        event.preventDefault();
        setActiveView("ingest");
        void navigate({ to: "/ingest" });
      } else if (isCommand && event.key.toLowerCase() === "h") {
        event.preventDefault();
        setActiveView("history");
        void navigate({ to: "/history" });
      } else if (isCommand && event.key === ",") {
        event.preventDefault();
        setActiveView("settings");
        void navigate({ to: "/settings" });
      } else if (isCommand && event.key.toLowerCase() === "b") {
        event.preventDefault();
        toggleSidebar();
      } else if (event.key === "Escape") {
        selectNode(null);
      } else if (event.key === "]") {
        setFocusDepth(Math.min(focusDepth + 1, 5));
      } else if (event.key === "[") {
        setFocusDepth(Math.max(focusDepth - 1, 1));
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [focusDepth, navigate, selectNode, setActiveView, setFocusDepth, toggleSidebar]);
}
