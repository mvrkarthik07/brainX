from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from brain.storage.sqlite_store import get_chunks_for_document, get_document, list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    title: str | None
    file_path: str
    file_type: str
    checksum: str | None
    metadata: dict = Field(default_factory=dict)
    ingested_at: str
    updated_at: str
    chunk_count: int | None = None


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    text: str
    position: int
    file_path: str
    file_type: str
    metadata: dict = Field(default_factory=dict)
    created_at: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class DocumentDetailResponse(BaseModel):
    document: DocumentResponse
    chunks: list[ChunkResponse]


@router.get("", response_model=DocumentListResponse)
def list_documents_route():
    return {"documents": list_documents()}


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_route(document_id: str):
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' was not found")

    return {
        "document": document,
        "chunks": get_chunks_for_document(document_id),
    }
