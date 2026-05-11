import type { PropsWithChildren } from "react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

import { Sidebar } from "@/components/layout/Sidebar/Sidebar";
import { StatusBar } from "@/components/layout/TopBar/StatusBar";
import { TitleBar } from "@/components/layout/TopBar/TitleBar";
import { useUIStore } from "@/store/uiStore";
import styles from "@/components/layout/AppShell.module.css";

export function AppShell({ children }: PropsWithChildren) {
  const sidebarCollapsed = useUIStore((state) => state.sidebarCollapsed);
  const [compactViewport, setCompactViewport] = useState(false);

  useEffect(() => {
    function handleResize() {
      setCompactViewport(window.innerWidth <= 1120);
    }

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const effectiveCollapsed = sidebarCollapsed || compactViewport;

  return (
    <div className={styles.shell}>
      <TitleBar />
      <div className={styles.body}>
        <motion.aside
          className={styles.sidebar}
          animate={{ width: effectiveCollapsed ? 56 : 220 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
        >
          <Sidebar />
        </motion.aside>
        <main className={styles.main}>{children}</main>
      </div>
      <StatusBar />
    </div>
  );
}
