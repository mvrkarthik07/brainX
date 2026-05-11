import { motion } from "framer-motion";

import type { SourceNode } from "@/types/chat";
import { SourceNodeChip } from "@/components/chat/SourceNodes/SourceNodeChip";
import styles from "@/components/chat/SourceNodes/SourceNodes.module.css";

export function SourceNodeList({
  nodes,
  onSelect,
}: {
  nodes: SourceNode[];
  onSelect?: (node: SourceNode) => void;
}) {
  if (nodes.length === 0) {
    return null;
  }

  return (
    <motion.div
      className={styles.sourceList}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition: { staggerChildren: 0.05, delayChildren: 0.15 },
        },
      }}
    >
      <span className={styles.sourceLabel}>Sources</span>
      {nodes.map((node) => (
        <motion.div
          key={node.chunk_id}
          variants={{
            hidden: { opacity: 0, scale: 0.85, y: 4 },
            visible: { opacity: 1, scale: 1, y: 0 },
          }}
          transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <SourceNodeChip node={node} onClick={onSelect} />
        </motion.div>
      ))}
    </motion.div>
  );
}
