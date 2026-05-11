import type {
  DocumentDetailResponse,
  DocumentListResponse,
  IngestionSummary,
} from "@/types/ingest";
import { request } from "@/api/client";

export function ingestUploadedFiles(
  files: File[],
  relativePaths: string[] = [],
) {
  const formData = new FormData();
  files.forEach((file, index) => {
    formData.append("files", file, file.name);
    formData.append("relative_paths", relativePaths[index] ?? "");
  });

  return request<IngestionSummary>("/ingest/upload", {
    method: "POST",
    body: formData,
  });
}

export function listDocuments() {
  return request<DocumentListResponse>("/documents");
}

export function getDocument(documentId: string) {
  return request<DocumentDetailResponse>(`/documents/${documentId}`);
}
