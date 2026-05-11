import { useIngestStore } from "@/store/ingestStore";
import styles from "@/views/IngestView/IngestView.module.css";

export function IngestQueue() {
  const queue = useIngestStore((state) => state.queue);

  if (queue.length === 0) {
    return <div className={styles.emptyState}>No ingestion jobs yet.</div>;
  }

  return (
    <div className={styles.queueList}>
      {queue.map((item) => (
        <div key={item.id} className={styles.queueItem}>
          <div>
            <div className={styles.queueTitle}>{item.path}</div>
            <div className={styles.queueMeta}>
              {item.kind} • {item.status}
            </div>
          </div>
          {item.summary ? (
            <div className={styles.queueMeta}>
              {item.summary.chunks_created} chunks • {item.summary.graph_nodes_upserted} nodes
            </div>
          ) : null}
          {item.error ? <div className={styles.errorText}>{item.error}</div> : null}
        </div>
      ))}
    </div>
  );
}
