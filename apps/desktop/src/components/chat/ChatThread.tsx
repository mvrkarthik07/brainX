import type { Message, SourceNode } from "@/types/chat";
import { AssistantMessage } from "@/components/chat/MessageBubble/AssistantMessage";
import { StreamingMessage } from "@/components/chat/MessageBubble/StreamingMessage";
import { UserMessage } from "@/components/chat/MessageBubble/UserMessage";
import styles from "@/views/ChatView/ChatView.module.css";

export function ChatThread({
  messages,
  streamingContent,
  isStreaming,
  onSelectSource,
}: {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  onSelectSource?: (node: SourceNode) => void;
}) {
  const isEmpty = messages.length === 0 && !isStreaming;

  return (
    <div className={`${styles.thread} ${isEmpty ? styles.threadEmpty : ""}`}>
      {isEmpty ? (
        <div className={styles.emptyThreadState}>
          <div className={styles.emptyThreadCard}>
            <div className={styles.emptyThreadEyebrow}>Local-first reasoning</div>
            <div className={styles.emptyThreadTitle}>Ask your knowledge graph</div>
            <div className={styles.emptyThreadCopy}>
              BrainX answers from local context only. Ingest documents, then query for ideas, decisions, code notes, and recurring concepts.
            </div>
            <div className={styles.exampleList}>
              <div className={styles.examplePrompt}>
                <strong>Summaries</strong>
                What did I write about rust performance?
              </div>
              <div className={styles.examplePrompt}>
                <strong>Connections</strong>
                Show me how my auth notes relate to the current project plan.
              </div>
              <div className={styles.examplePrompt}>
                <strong>Recall</strong>
                Which documents mention retrieval traces or feedback mutation?
              </div>
            </div>
          </div>
        </div>
      ) : null}
      {messages.map((message) =>
        message.role === "user" ? (
          <UserMessage key={message.id} message={message} />
        ) : (
          <AssistantMessage key={message.id} message={message} onSelectSource={onSelectSource} />
        ),
      )}
      {isStreaming ? <StreamingMessage content={streamingContent} /> : null}
    </div>
  );
}
