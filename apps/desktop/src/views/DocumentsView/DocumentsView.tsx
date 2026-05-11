import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { getDocument, listDocuments } from "@/api/ingest";
import styles from "@/views/DocumentsView/DocumentsView.module.css";

export function DocumentsView() {
  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
  });
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

  const documents = documentsQuery.data?.documents ?? [];
  const activeDocumentId = selectedDocumentId ?? documents[0]?.id ?? null;

  const detailQuery = useQuery({
    queryKey: ["document", activeDocumentId],
    queryFn: () => getDocument(activeDocumentId!),
    enabled: Boolean(activeDocumentId),
  });

  const activeDocument = useMemo(() => detailQuery.data?.document ?? null, [detailQuery.data]);

  return (
    <div className={styles.view}>
      <aside className={styles.sidebar}>
        <div className={styles.heading}>Documents</div>
        <div className={styles.list}>
          {documents.map((document) => (
            <button key={document.id} className={styles.item} onClick={() => setSelectedDocumentId(document.id)} type="button">
              <div className={styles.itemTitle}>{document.title ?? document.id}</div>
              <div className={styles.itemMeta}>
                {document.file_type} • {document.chunk_count ?? 0} chunks
              </div>
            </button>
          ))}
        </div>
      </aside>
      <main className={styles.main}>
        {activeDocument ? (
          <>
            <div className={styles.heading}>{activeDocument.title ?? activeDocument.id}</div>
            <div className={styles.itemMeta}>{activeDocument.file_path}</div>
            <div className={styles.chunkList}>
              {detailQuery.data?.chunks.map((chunk) => (
                <div key={chunk.id} className={styles.chunk}>
                  <div className={styles.itemMeta}>
                    chunk {chunk.position} • {chunk.id}
                  </div>
                  <div>{chunk.text}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className={styles.emptyState}>No documents ingested yet.</div>
        )}
      </main>
    </div>
  );
}
