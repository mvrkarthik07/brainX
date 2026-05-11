from typing import Any

from fastapi import APIRouter, HTTPException

from brain.generation.answer_service import get_interaction_trace_payload

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("/{interaction_id}/trace")
def interaction_trace_route(interaction_id: str) -> dict[str, Any]:
    trace = get_interaction_trace_payload(interaction_id)
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Interaction '{interaction_id}' was not found")
    return trace
