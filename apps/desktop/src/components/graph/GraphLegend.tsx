import { Badge } from "@/components/primitives/Badge/Badge";
import styles from "@/components/graph/GraphLegend.module.css";

export function GraphLegend() {
  return (
    <div className={styles.legend}>
      <Badge>Document</Badge>
      <Badge>Concept</Badge>
      <Badge>User</Badge>
      <Badge>Chunk</Badge>
      <Badge>Interaction</Badge>
    </div>
  );
}
