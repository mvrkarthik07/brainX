import {
  BrainCircuit,
  Files,
  GitGraph,
  History,
  Inbox,
  PanelLeftOpen,
  PanelLeftClose,
  Settings,
} from "lucide-react";
import { useEffect, useState } from "react";
import { SidebarNavItem } from "@/components/layout/Sidebar/SidebarNav";
import { Button } from "@/components/primitives/Button/Button";
import { useUIStore } from "@/store/uiStore";
import styles from "@/components/layout/Sidebar/Sidebar.module.css";

export function Sidebar() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
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
    <div className={`${styles.sidebar} ${effectiveCollapsed ? styles.collapsedSidebar : ""}`}>
      <div className={styles.identity}>
        <span className={styles.logo}>{effectiveCollapsed ? "bX" : "brainX"}</span>
      </div>

      <div className={styles.section}>
        <div className={`${styles.sectionTitle} ${effectiveCollapsed ? styles.sectionTitleHidden : ""}`}>Primary</div>
        <nav className={styles.nav}>
          <SidebarNavItem to="/" icon={BrainCircuit} label="Chat" collapsed={effectiveCollapsed} />
          <SidebarNavItem to="/graph" icon={GitGraph} label="Graph" collapsed={effectiveCollapsed} />
          <SidebarNavItem to="/documents" icon={Files} label="Documents" collapsed={effectiveCollapsed} />
          <SidebarNavItem to="/ingest" icon={Inbox} label="Ingest" collapsed={effectiveCollapsed} />
          <SidebarNavItem to="/history" icon={History} label="History" collapsed={effectiveCollapsed} />
        </nav>
      </div>

      <div className={styles.middle}>
        <div className={styles.sectionSpacer} />

        <div className={styles.section}>
          <div className={`${styles.sectionTitle} ${effectiveCollapsed ? styles.sectionTitleHidden : ""}`}>Secondary</div>
          <nav className={styles.nav}>
            <SidebarNavItem to="/settings" icon={Settings} label="Settings" collapsed={effectiveCollapsed} />
          </nav>
          <Button
            variant="icon"
            onClick={toggleSidebar}
            className={`${styles.collapseButton} ${effectiveCollapsed ? styles.collapseButtonCollapsed : ""}`}
            title={effectiveCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label={effectiveCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            disabled={compactViewport}
          >
            {effectiveCollapsed ? <PanelLeftOpen size={14} /> : <PanelLeftClose size={14} />}
          </Button>
        </div>
      </div>
    </div>
  );
}
