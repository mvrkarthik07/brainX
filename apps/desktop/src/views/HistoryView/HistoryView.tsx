import { useChatStore } from "@/store/chatStore";
import styles from "@/views/HistoryView/HistoryView.module.css";

export function HistoryView() {
  const messages = useChatStore((state) => state.messages);

  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <div className={styles.eyebrow}>Session memory</div>
        <div className={styles.title}>History</div>
      </div>
      {messages.length === 0 ? (
        <div className={styles.emptyState}>
          Backend interaction listing is not exposed yet, so this view currently shows the live local session only.
        </div>
      ) : (
        <div className={styles.list}>
          {messages.map((message) => (
            <div key={message.id} className={styles.card}>
              <div className={styles.meta}>{message.role}</div>
              <div className={styles.content}>{message.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
