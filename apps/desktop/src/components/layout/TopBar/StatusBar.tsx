import { useQuery } from "@tanstack/react-query";

import { getHealth } from "@/api/system";
import { StatusDot } from "@/components/primitives/StatusDot/StatusDot";
import { useChatStore } from "@/store/chatStore";
import { formatDurationMs, formatNumber } from "@/utils/format";
import styles from "@/components/layout/TopBar/TopBar.module.css";

export function StatusBar() {
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 15_000,
  });
  const messages = useChatStore((state) => state.messages);
  const latestAssistantMessage = [...messages].reverse().find((message) => message.role === "assistant");
  const latestLatency = latestAssistantMessage?.summaryTrace?.latency_ms?.total_ms;
  const health = healthQuery.data;

  return (
    <div className={styles.statusBar}>
      <div className={styles.statusList}>
        <div className={styles.statusItem}>
          <StatusDot status={health?.ollama.ok ? "active" : health ? "error" : "loading"} />
          Ollama {health?.ollama.ok ? "ready" : "offline"}
        </div>
        <div className={styles.statusItem}>
          <StatusDot status={health?.faiss.ok ? "active" : health ? "error" : "loading"} />
          FAISS {formatNumber(health?.faiss.vectors as number | undefined)} vectors
        </div>
        <div className={styles.statusItem}>
          <StatusDot status={health?.graph.ok ? "active" : health ? "error" : "loading"} />
          graph {formatNumber(health?.graph.nodes as number | undefined)} nodes
        </div>
      </div>
      <div className={styles.statusList}>
        <div className={styles.statusItem}>
          latency <span className={styles.statusValue}>{formatDurationMs(latestLatency)}</span>
        </div>
        <div className={styles.statusItem}>
          backend <span className={styles.statusValue}>{health?.status ?? "loading"}</span>
        </div>
      </div>
    </div>
  );
}
