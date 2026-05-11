import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { getInteractionTrace } from "@/api/chat";
import { ChatInput } from "@/components/chat/ChatInput/ChatInput";
import { ChatThread } from "@/components/chat/ChatThread";
import { Button } from "@/components/primitives/Button/Button";
import { useChatStore, useGraphStore } from "@/store";
import type { SourceNode } from "@/types/chat";
import { formatDurationMs } from "@/utils/format";
import styles from "@/views/ChatView/ChatView.module.css";

export function ChatView() {
  const messages = useChatStore((state) => state.messages);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const streamingContent = useChatStore((state) => state.streamingContent);
  const clearHistory = useChatStore((state) => state.clearHistory);
  const [selectedInteractionId, setSelectedInteractionId] = useState<string | null>(null);
  const setCenterNodeId = useGraphStore((state) => state.setCenterNodeId);

  const latestAssistant = useMemo(
    () => [...messages].reverse().find((message) => message.role === "assistant"),
    [messages],
  );
  const latestSummary = latestAssistant?.summaryTrace;
  const isEmptySession = messages.length === 0 && !isStreaming;

  const traceQuery = useQuery({
    queryKey: ["interaction-trace", selectedInteractionId],
    queryFn: () => getInteractionTrace(selectedInteractionId!),
    enabled: Boolean(selectedInteractionId),
  });

  function handleSelectSource(node: SourceNode) {
    setCenterNodeId(`chunk:${node.chunk_id.replace(/^chunk:/, "")}`);
  }

  return (
    <div className={`${styles.view} ${isEmptySession ? styles.viewEmpty : ""}`}>
      <div className={styles.main}>
        <div className={styles.topbar}>
          <div className={styles.title}>
            <span className={styles.eyebrow}>Local reasoning surface</span>
            <div className={styles.heading}>Chat</div>
          </div>
          {!isEmptySession ? (
            <Button variant="ghost" onClick={clearHistory}>
              Clear session
            </Button>
          ) : null}
        </div>
        <div className={styles.threadWrap}>
          {isEmptySession ? (
            <div className={styles.emptyComposer}>
              <ChatThread
                messages={messages}
                streamingContent={streamingContent}
                isStreaming={isStreaming}
                onSelectSource={handleSelectSource}
              />
              <ChatInput centered />
            </div>
          ) : (
            <ChatThread
              messages={messages}
              streamingContent={streamingContent}
              isStreaming={isStreaming}
              onSelectSource={handleSelectSource}
            />
          )}
        </div>
        {!isEmptySession ? <ChatInput /> : null}
      </div>

      <aside className={`${styles.inspector} ${isEmptySession ? styles.inspectorHidden : ""}`}>
        <div className={styles.panel}>
          <div className={styles.panelTitle}>Latest response</div>
          {latestAssistant ? (
            <>
              <div className={styles.traceSummary}>
                <div className={styles.traceRow}>
                  <span className={styles.traceLabel}>Rewrite</span>
                  <span className={styles.traceValue}>{latestAssistant.rewrittenQuery ?? "No rewrite captured yet."}</span>
                </div>
                <div className={styles.traceRow}>
                  <span className={styles.traceLabel}>Latency</span>
                  <span className={styles.traceValue}>{formatDurationMs(latestSummary?.latency_ms?.total_ms)}</span>
                </div>
                <div className={styles.traceRow}>
                  <span className={styles.traceLabel}>Vector hits</span>
                  <span className={styles.traceValue}>{latestSummary?.vector_hits ?? 0}</span>
                </div>
                <div className={styles.traceRow}>
                  <span className={styles.traceLabel}>Edges traversed</span>
                  <span className={styles.traceValue}>{latestSummary?.edges_traversed ?? 0}</span>
                </div>
              </div>
              {latestAssistant.queryId ? (
                <div className={styles.actionRow}>
                  <Button variant="ghost" onClick={() => setSelectedInteractionId(latestAssistant.queryId ?? null)}>
                    Load full trace
                  </Button>
                </div>
              ) : null}
            </>
          ) : (
            <div className={styles.emptyState}>Run a query to inspect the retrieval trace.</div>
          )}
        </div>

        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <div className={styles.panelTitle}>Trace</div>
            {selectedInteractionId ? (
              <Button variant="ghost" onClick={() => setSelectedInteractionId(null)}>
                Clear
              </Button>
            ) : null}
          </div>
          {traceQuery.data ? (
            <pre className={styles.traceBlock}>{JSON.stringify(traceQuery.data, null, 2)}</pre>
          ) : (
            <div className={styles.emptyState}>
              {selectedInteractionId ? "Loading trace..." : "Select a completed response to inspect its full trace."}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
