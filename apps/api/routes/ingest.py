from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from brain.ingestion.ingest_service import UploadedIngestFile, ingest_file, ingest_folder, ingest_uploaded_files

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestFileRequest(BaseModel):
    path: str


class IngestFolderRequest(BaseModel):
    path: str
    recursive: bool = True


class DocumentRef(BaseModel):
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


class FileError(BaseModel):
    path: str
    error: str


class IngestionSummaryResponse(BaseModel):
    documents_added: int
    chunks_created: int
    concepts_extracted: int
    vectors_added: int
    graph_nodes_upserted: int
    graph_edges_upserted: int
    errors: list[FileError] = Field(default_factory=list)
    document: DocumentRef | None = None


@router.post("/upload", response_model=IngestionSummaryResponse)
async def ingest_upload_route(
    files: list[UploadFile] = File(...),
    relative_paths: list[str] = Form(default=[]),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one uploaded file is required")

    uploaded_files: list[UploadedIngestFile] = []
    for index, upload in enumerate(files):
        try:
            content = await upload.read()
        finally:
            await upload.close()

        uploaded_files.append(
            UploadedIngestFile(
                filename=upload.filename or f"upload-{index}",
                content=content,
                relative_path=relative_paths[index] if index < len(relative_paths) else None,
            )
        )

    try:
        return ingest_uploaded_files(uploaded_files)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/file", response_model=IngestionSummaryResponse)
def ingest_file_route(request: IngestFileRequest):
    try:
        return ingest_file(request.path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/folder", response_model=IngestionSummaryResponse)
def ingest_folder_route(request: IngestFolderRequest):
    try:
        return ingest_folder(request.path, recursive=request.recursive)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
