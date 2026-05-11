import { memo } from "react";
import { FileText, Hash } from "lucide-react";

import type { SourceNode } from "@/types/chat";
import { cn } from "@/utils/cn";
import styles from "@/components/chat/SourceNodes/SourceNodes.module.css";

function SourceNodeChipImpl({
  node,
  onClick,
}: {
  node: SourceNode;
  onClick?: (node: SourceNode) => void;
}) {
  const isClickable = Boolean(onClick);

  return (
    <button
      className={cn(styles.sourceChip, !isClickable && styles.sourceChipDisabled)}
      onClick={() => onClick?.(node)}
      type="button"
      disabled={!isClickable}
    >
      {node.document_title ? <FileText size={12} className={styles.sourceChipIcon} /> : <Hash size={12} className={styles.sourceChipIcon} />}
      <span>{node.document_title ?? node.chunk_id}</span>
    </button>
  );
}

export const SourceNodeChip = memo(SourceNodeChipImpl);
