import { Paperclip, LoaderCircle, SendHorizonal } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/primitives/Button/Button";
import { useChat } from "@/hooks/useChat";
import { useIngest } from "@/hooks/useIngest";
import { cn } from "@/utils/cn";
import styles from "@/components/chat/ChatInput/ChatInput.module.css";

export function ChatInput({ centered = false }: { centered?: boolean }) {
  const [value, setValue] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const { isStreaming, submitQuery } = useChat();
  const { ingestFiles } = useIngest();

  useEffect(() => {
    const element = textareaRef.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, 120)}px`;
  }, [value]);

  async function handleSubmit() {
    if (!value.trim() || isStreaming) {
      return;
    }
    const pending = value;
    setValue("");
    await submitQuery(pending);
  }

  async function handleAttachmentSelection(files: FileList | null) {
    const selectedFiles = Array.from(files ?? []);
    if (selectedFiles.length === 0) {
      return;
    }

    setIsUploading(true);
    try {
      await ingestFiles(selectedFiles);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["documents"] }),
        queryClient.invalidateQueries({ queryKey: ["health"] }),
        queryClient.invalidateQueries({ queryKey: ["graph-neighborhood"] }),
      ]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  return (
    <div className={cn(styles.inputPanel, centered && styles.inputPanelCentered)}>
      <input
        ref={fileInputRef}
        className={styles.hiddenInput}
        type="file"
        multiple
        accept=".txt,.md,.pdf,.py,.js,.ts,.tsx,.jsx"
        onChange={(event) => void handleAttachmentSelection(event.target.files)}
      />
      <div
        className={cn(styles.inputWrapper, centered && styles.inputWrapperCentered)}
        data-streaming={isStreaming || isUploading ? "true" : "false"}
      >
        <textarea
          ref={textareaRef}
          className={cn(styles.textarea, centered && styles.textareaCentered)}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void handleSubmit();
            }
          }}
          placeholder="Ask your brain"
          rows={1}
          disabled={isStreaming}
        />
        <div className={styles.actions}>
          <Button
            variant="icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={isStreaming || isUploading}
            title="Attach files to ingest into BrainX"
            aria-label="Attach files"
          >
            {isUploading ? <LoaderCircle size={14} className="animate-breathe" /> : <Paperclip size={14} />}
          </Button>
          <Button variant="primary" onClick={() => void handleSubmit()} disabled={!value.trim() || isStreaming || isUploading}>
            {isStreaming ? <LoaderCircle size={14} className="animate-breathe" /> : <SendHorizonal size={14} />}
            {isStreaming ? "Thinking" : "Send"}
          </Button>
        </div>
      </div>
    </div>
  );
}
