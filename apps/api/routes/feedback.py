from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from brain.feedback.feedback_service import apply_feedback
from brain.storage.sqlite_store import get_interaction

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    interaction_id: str
    rating: int


class FeedbackResponse(BaseModel):
    interaction_id: str
    rating: int
    delta: float
    edges_mutated: int
    edges_skipped: int
    flagged_edges: int


@router.post("", response_model=FeedbackResponse)
def feedback_route(request: FeedbackRequest):
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="rating must be an integer between 1 and 5")

    if get_interaction(request.interaction_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Interaction '{request.interaction_id}' was not found",
        )

    try:
        return apply_feedback(request.interaction_id, request.rating)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
