import { memo } from "react";

import type { Message } from "@/types/chat";
import { formatRelativeTime } from "@/utils/format";
import styles from "@/components/chat/MessageBubble/MessageBubble.module.css";

function UserMessageImpl({ message }: { message: Message }) {
  return (
    <div className={styles.userMessage}>
      <p className={styles.userContent}>{message.content}</p>
      <span className={styles.timestamp}>{formatRelativeTime(message.timestamp)}</span>
    </div>
  );
}

export const UserMessage = memo(UserMessageImpl);
