import { useQuery } from "@tanstack/react-query";

import { BASE_URL } from "@/api/client";
import { getHealth } from "@/api/system";
import styles from "@/views/SettingsView/SettingsView.module.css";

export function SettingsView() {
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 15_000,
  });

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <div className={styles.eyebrow}>Local configuration</div>
        <div className={styles.title}>Settings</div>
      </div>
      <div className={styles.panel}>
        <div className={styles.row}>
          <div className={styles.label}>API base URL</div>
          <div className={styles.value}>{BASE_URL}</div>
        </div>
        <div className={styles.row}>
          <div className={styles.label}>Health status</div>
          <div className={styles.value}>{healthQuery.data?.status ?? "loading"}</div>
        </div>
        <div className={styles.row}>
          <div className={styles.label}>Graph backend</div>
          <div className={styles.value}>{String(healthQuery.data?.graph.backend ?? "unknown")}</div>
        </div>
        <div className={styles.row}>
          <div className={styles.label}>Installed local models</div>
          <div className={styles.value}>{Object.keys(healthQuery.data?.ollama.models ?? {}).join(", ") || "loading"}</div>
        </div>
      </div>
    </div>
  );
}
