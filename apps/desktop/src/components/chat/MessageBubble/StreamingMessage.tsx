import styles from "@/components/chat/MessageBubble/MessageBubble.module.css";

function ThinkingDots() {
  return (
    <div className={styles.thinkingDots}>
      <span className={styles.thinkingDot} />
      <span className={styles.thinkingDot} />
      <span className={styles.thinkingDot} />
    </div>
  );
}

export function StreamingMessage({ content }: { content: string }) {
  return (
    <div className={styles.streamingMessage}>
      <div className={styles.streamingCard}>
        {content.length === 0 ? <ThinkingDots /> : null}
        <div>
          {content}
          <span className={styles.cursor} aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}
