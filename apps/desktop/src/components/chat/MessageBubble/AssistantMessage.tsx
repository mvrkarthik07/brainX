import { memo } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { RatingBar } from "@/components/chat/RatingBar/RatingBar";
import { SourceNodeList } from "@/components/chat/SourceNodes/SourceNodeList";
import type { Message, SourceNode } from "@/types/chat";
import { formatDurationMs } from "@/utils/format";
import styles from "@/components/chat/MessageBubble/MessageBubble.module.css";

function AssistantMessageImpl({
  message,
  onSelectSource,
}: {
  message: Message;
  onSelectSource?: (node: SourceNode) => void;
}) {
  return (
    <motion.div
      className={styles.assistantMessage}
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className={styles.assistantCard}>
        <div className={styles.assistantContent}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
        <SourceNodeList nodes={message.sourceNodes ?? []} onSelect={onSelectSource} />
        <div className={styles.metaRow}>
          <span>retrieved in {formatDurationMs(message.latencyMs)}</span>
          {message.queryId ? <span>{message.queryId}</span> : null}
        </div>
        {message.queryId ? <RatingBar queryId={message.queryId} currentRating={message.rating} /> : null}
      </div>
    </motion.div>
  );
}

export const AssistantMessage = memo(AssistantMessageImpl);
