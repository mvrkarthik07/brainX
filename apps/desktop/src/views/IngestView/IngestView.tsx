import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { IngestQueue } from "@/components/ingest/IngestQueue";
import { Button } from "@/components/primitives/Button/Button";
import { useIngest } from "@/hooks/useIngest";
import styles from "@/views/IngestView/IngestView.module.css";

type UploadableFile = File & {
  webkitRelativePath?: string;
};

export function IngestView() {
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [folderNames, setFolderNames] = useState<string[]>([]);
  const [isUploadingFiles, setIsUploadingFiles] = useState(false);
  const [isUploadingFolder, setIsUploadingFolder] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const folderInputRef = useRef<HTMLInputElement | null>(null);
  const { ingestFiles, ingestFolderFiles } = useIngest();
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!folderInputRef.current) {
      return;
    }

    folderInputRef.current.setAttribute("webkitdirectory", "");
    folderInputRef.current.setAttribute("directory", "");
  }, []);

  async function refreshIngestQueries() {
    await queryClient.invalidateQueries({ queryKey: ["documents"] });
    await queryClient.invalidateQueries({ queryKey: ["health"] });
  }

  async function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const selectedFiles = Array.from(event.target.files ?? []);
    if (selectedFiles.length === 0) {
      return;
    }

    setFileNames(selectedFiles.map((file) => file.name));
    setIsUploadingFiles(true);
    try {
      await ingestFiles(selectedFiles);
      await refreshIngestQueries();
    } finally {
      setIsUploadingFiles(false);
      event.target.value = "";
    }
  }

  async function handleFolderSelection(event: ChangeEvent<HTMLInputElement>) {
    const selectedFiles = Array.from(event.target.files ?? []) as UploadableFile[];
    if (selectedFiles.length === 0) {
      return;
    }

    const relativePaths = selectedFiles.map((file) => file.webkitRelativePath || file.name);
    setFolderNames(relativePaths);
    setIsUploadingFolder(true);
    try {
      await ingestFolderFiles(selectedFiles, relativePaths);
      await refreshIngestQueries();
    } finally {
      setIsUploadingFolder(false);
      event.target.value = "";
    }
  }

  return (
    <div className={styles.view}>
      <div className={styles.hero}>
        <div className={styles.title}>Knowledge Ingestion</div>
        <div className={styles.subtitle}>Upload local files or a whole folder directly into BrainX. No manual path entry required.</div>
      </div>

      <div className={styles.grid}>
        <div className={styles.card}>
          <div className={styles.dropZone}>
            <strong>Upload files</strong>
            <span>Select one or more supported files from your machine.</span>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              hidden
              onChange={(event) => void handleFileSelection(event)}
              accept=".txt,.md,.pdf,.py,.js,.ts,.tsx,.jsx"
            />
            <div className={styles.actions}>
              <Button variant="primary" onClick={() => fileInputRef.current?.click()} disabled={isUploadingFiles}>
                {isUploadingFiles ? "Uploading..." : "Choose files"}
              </Button>
            </div>
            {fileNames.length > 0 ? <div className={styles.selectionList}>{fileNames.join(", ")}</div> : null}
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.dropZone}>
            <strong>Upload folder</strong>
            <span>Select a local folder and BrainX will ingest supported files inside it.</span>
            <input
              ref={folderInputRef}
              type="file"
              multiple
              hidden
              onChange={(event) => void handleFolderSelection(event)}
              accept=".txt,.md,.pdf,.py,.js,.ts,.tsx,.jsx"
            />
            <div className={styles.actions}>
              <Button variant="primary" onClick={() => folderInputRef.current?.click()} disabled={isUploadingFolder}>
                {isUploadingFolder ? "Uploading..." : "Choose folder"}
              </Button>
            </div>
            {folderNames.length > 0 ? (
              <div className={styles.selectionList}>
                {folderNames.slice(0, 6).join(", ")}
                {folderNames.length > 6 ? ` +${folderNames.length - 6} more` : ""}
              </div>
            ) : null}
          </div>
        </div>
      </div>

      <div className={styles.card}>
        <strong>Ingest queue</strong>
        <IngestQueue />
      </div>
    </div>
  );
}
