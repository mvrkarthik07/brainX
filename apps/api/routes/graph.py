from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from brain.graph.factory import get_graph_store

router = APIRouter(prefix="/graph", tags=["graph"])


class GraphNodeResponse(BaseModel):
    id: str
    type: str
    label: str | None
    properties: dict = Field(default_factory=dict)


class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: str
    effective_weight: float


class GraphNeighborhoodResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]


@router.get("/neighborhood", response_model=GraphNeighborhoodResponse)
def get_graph_neighborhood(
    node_id: str = Query(...),
    hops: int = Query(default=1, ge=1, le=5),
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        neighborhood = get_graph_store().get_neighborhood(node_id=node_id, hops=hops, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "nodes": [
            {
                "id": node["id"],
                "type": node["node_type"],
                "label": node["label"],
                "properties": node["properties"],
            }
            for node in neighborhood["nodes"]
        ],
        "edges": [
            {
                "id": edge["id"],
                "source": edge["source_id"],
                "target": edge["target_id"],
                "type": edge["edge_type"],
                "effective_weight": edge["effective_weight"],
            }
            for edge in neighborhood["edges"]
        ],
    }
