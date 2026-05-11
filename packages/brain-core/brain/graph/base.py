from typing import Any, Protocol, TypedDict, runtime_checkable


class GraphNode(TypedDict):
    id: str
    node_type: str
    label: str | None
    properties: dict[str, Any]
    created_at: str
    updated_at: str


class GraphEdge(TypedDict):
    id: str
    source_id: str
    target_id: str
    edge_type: str
    base_weight: float
    feedback_delta: float
    effective_weight: float
    properties: dict[str, Any]
    flagged: bool
    created_at: str
    updated_at: str


class GraphNeighborhood(TypedDict):
    center_node_id: str
    hops: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class GraphTraversalResult(TypedDict):
    seed_node_ids: list[str]
    visited_nodes: list[str]
    traversed_edges: list[GraphEdge]
    activation_scores: dict[str, float]


@runtime_checkable
class GraphStore(Protocol):
    def initialize(self) -> None:
        ...

    def health(self) -> dict[str, Any]:
        ...

    def build_node_id(self, node_type: str, entity_id: str) -> str:
        ...

    def upsert_user(
        self,
        user_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        ...

    def upsert_document(
        self,
        document_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        ...

    def upsert_chunk(
        self,
        chunk_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        ...

    def upsert_concept(
        self,
        concept_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        ...

    def upsert_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        base_weight: float | None = None,
        properties: dict[str, Any] | None = None,
        feedback_delta: float | None = None,
        flagged: bool | None = None,
    ) -> GraphEdge:
        ...

    def get_node(self, node_id: str) -> GraphNode | None:
        ...

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        ...

    def get_edges_between(self, source_id: str, target_id: str) -> list[GraphEdge]:
        ...

    def get_neighborhood(
        self,
        node_id: str,
        hops: int = 1,
        limit: int = 100,
    ) -> GraphNeighborhood:
        ...

    def traverse(
        self,
        seed_node_ids: list[str],
        max_hops: int,
        edge_threshold: float,
        hop_decay: float,
        max_nodes: int = 80,
        max_edges: int = 80,
    ) -> GraphTraversalResult:
        ...

    def update_edge_feedback(
        self,
        edge_id: str,
        delta: float,
        interaction_id: str | None = None,
        rating: int | None = None,
        flag: bool = False,
    ) -> dict[str, Any]:
        ...

    def export_graph(self) -> dict[str, Any]:
        ...
