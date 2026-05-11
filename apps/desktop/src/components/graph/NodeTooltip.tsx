import type { GraphNode } from "@/types/graph";
import styles from "@/components/graph/NodeTooltip.module.css";

export function NodeTooltip({ node }: { node: GraphNode | null }) {
  if (!node) {
    return <div className={styles.emptyState}>Select a node to inspect its local properties.</div>;
  }

  return (
    <div className={styles.tooltip}>
      <div className={styles.section}>
        <div className={styles.label}>Node</div>
        <div className={styles.value}>{node.label}</div>
      </div>
      <div className={styles.section}>
        <div className={styles.label}>Type</div>
        <div className={styles.value}>{node.type}</div>
      </div>
      <div className={styles.section}>
        <div className={styles.label}>ID</div>
        <div className={styles.monoValue}>{node.id}</div>
      </div>
      <pre className={styles.properties}>
        {JSON.stringify(node.properties, null, 2)}
      </pre>
    </div>
  );
}
