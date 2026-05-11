from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from brain.generation.answer_service import answer_query

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    query: str


class SourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str | None = None
    score: float


class QueryResponse(BaseModel):
    interaction_id: str
    query: str
    rewritten_query: str
    answer: str
    sources: list[SourceResponse] = Field(default_factory=list)
    summary_trace: dict = Field(default_factory=dict)


@router.post("", response_model=QueryResponse)
def query_route(request: QueryRequest):
    try:
        return answer_query(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
