import { useCallback } from "react";
import { nanoid } from "nanoid";

import { ingestUploadedFiles } from "@/api/ingest";
import { useIngestStore } from "@/store/ingestStore";

export function useIngest() {
  const addItem = useIngestStore((state) => state.addItem);
  const updateItem = useIngestStore((state) => state.updateItem);

  const ingestUploads = useCallback(
    async (
      files: File[],
      kind: "file" | "folder",
      relativePaths: string[] = [],
    ) => {
      if (files.length === 0) {
        throw new Error("No files selected for ingestion");
      }

      const id = nanoid();
      addItem({
        id,
        kind,
        path:
          kind === "folder"
            ? relativePaths[0]?.split("/")[0] || `${files.length} uploaded files`
            : files.map((file) => file.name).join(", "),
        status: "running",
      });

      try {
        const summary = await ingestUploadedFiles(files, relativePaths);
        updateItem(id, { status: "done", summary });
        return summary;
      } catch (error) {
        updateItem(id, {
          status: "error",
          error: error instanceof Error ? error.message : "Ingestion failed",
        });
        throw error;
      }
    },
    [addItem, updateItem],
  );

  return {
    ingestFiles: (files: File[]) => ingestUploads(files, "file"),
    ingestFolderFiles: (files: File[], relativePaths: string[]) =>
      ingestUploads(files, "folder", relativePaths),
  };
}
