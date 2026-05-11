import hashlib
import heapq
import json
import uuid
from collections import deque
from typing import Any

from brain.config.settings import GRAPH_BACKEND, SQLITE_DB_PATH
from brain.graph.base import GraphEdge, GraphNeighborhood, GraphNode, GraphTraversalResult
from brain.storage.sqlite_store import DEFAULT_USER_ID, get_connection, initialize_sqlite, utc_now_iso


class SQLiteGraphStore:
    def __init__(self) -> None:
        self.backend = GRAPH_BACKEND
        self.db_path = SQLITE_DB_PATH
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        initialize_sqlite()
        with get_connection() as conn:
            self._upsert_node(
                conn=conn,
                node_id=self.build_node_id("user", DEFAULT_USER_ID),
                node_type="User",
                label="Default User",
                properties={"user_id": DEFAULT_USER_ID},
            )
            conn.commit()

        self._initialized = True

    def health(self) -> dict[str, Any]:
        try:
            self.initialize()
            with get_connection() as conn:
                node_count = conn.execute("SELECT COUNT(*) AS count FROM graph_nodes").fetchone()["count"]
                edge_count = conn.execute("SELECT COUNT(*) AS count FROM graph_edges").fetchone()["count"]
                default_user_exists = (
                    conn.execute(
                        "SELECT 1 FROM graph_nodes WHERE id = ?",
                        (self.build_node_id("user", DEFAULT_USER_ID),),
                    ).fetchone()
                    is not None
                )

            return {
                "ok": True,
                "backend": "sqlite",
                "db_path": str(self.db_path),
                "nodes": node_count,
                "edges": edge_count,
                "default_user_exists": default_user_exists,
            }
        except Exception as exc:
            return {
                "ok": False,
                "backend": "sqlite",
                "db_path": str(self.db_path),
                "error": str(exc),
            }

    def build_node_id(self, node_type: str, entity_id: str) -> str:
        normalized_type = node_type.strip().lower()
        if entity_id.startswith(f"{normalized_type}:"):
            return entity_id
        return f"{normalized_type}:{entity_id}"

    def upsert_user(
        self,
        user_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        merged_properties = dict(properties or {})
        merged_properties["user_id"] = user_id
        return self._upsert_node_record(
            node_id=self.build_node_id("user", user_id),
            node_type="User",
            label=label or user_id,
            properties=merged_properties,
        )

    def upsert_document(
        self,
        document_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        merged_properties = dict(properties or {})
        merged_properties["document_id"] = document_id
        return self._upsert_node_record(
            node_id=self.build_node_id("document", document_id),
            node_type="Document",
            label=label or document_id,
            properties=merged_properties,
        )

    def upsert_chunk(
        self,
        chunk_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        merged_properties = dict(properties or {})
        merged_properties["chunk_id"] = chunk_id
        return self._upsert_node_record(
            node_id=self.build_node_id("chunk", chunk_id),
            node_type="Chunk",
            label=label or chunk_id,
            properties=merged_properties,
        )

    def upsert_concept(
        self,
        concept_id: str,
        label: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        merged_properties = dict(properties or {})
        merged_properties["concept_id"] = concept_id
        return self._upsert_node_record(
            node_id=self.build_node_id("concept", concept_id),
            node_type="Concept",
            label=label or concept_id,
            properties=merged_properties,
        )

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
        self.initialize()

        with get_connection() as conn:
            existing = self._get_edge_row(conn, source_id, target_id, edge_type)
            now = utc_now_iso()

            if existing is None:
                stored_base_weight = 1.0 if base_weight is None else float(base_weight)
                stored_feedback_delta = 0.0 if feedback_delta is None else float(feedback_delta)
                stored_flagged = 0 if flagged is None else int(flagged)
                effective_weight = max(0.0, stored_base_weight + stored_feedback_delta)

                conn.execute(
                    """
                    INSERT INTO graph_edges (
                        id,
                        source_id,
                        target_id,
                        edge_type,
                        base_weight,
                        feedback_delta,
                        effective_weight,
                        properties_json,
                        flagged,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self._build_edge_id(source_id, target_id, edge_type),
                        source_id,
                        target_id,
                        edge_type,
                        stored_base_weight,
                        stored_feedback_delta,
                        effective_weight,
                        self._encode_properties(properties or {}),
                        stored_flagged,
                        now,
                        now,
                    ),
                )
            else:
                existing_properties = self._decode_properties(existing["properties_json"])
                stored_base_weight = (
                    float(base_weight) if base_weight is not None else float(existing["base_weight"])
                )
                stored_feedback_delta = (
                    float(feedback_delta)
                    if feedback_delta is not None
                    else float(existing["feedback_delta"])
                )
                stored_flagged = int(flagged) if flagged is not None else int(existing["flagged"])
                updated_properties = properties if properties is not None else existing_properties
                effective_weight = max(0.0, stored_base_weight + stored_feedback_delta)

                conn.execute(
                    """
                    UPDATE graph_edges
                    SET
                        base_weight = ?,
                        feedback_delta = ?,
                        effective_weight = ?,
                        properties_json = ?,
                        flagged = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        stored_base_weight,
                        stored_feedback_delta,
                        effective_weight,
                        self._encode_properties(updated_properties),
                        stored_flagged,
                        now,
                        existing["id"],
                    ),
                )

            conn.commit()
            edge_row = self._get_edge_row(conn, source_id, target_id, edge_type)
            if edge_row is None:
                raise RuntimeError("Failed to upsert graph edge")
            return self._row_to_edge(edge_row)

    def get_node(self, node_id: str) -> GraphNode | None:
        self.initialize()
        with get_connection() as conn:
            row = self._get_node_row(conn, node_id)
            return self._row_to_node(row) if row is not None else None

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        self.initialize()
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM graph_edges
                WHERE source_id = ?
                ORDER BY effective_weight DESC, updated_at DESC
                """,
                (node_id,),
            ).fetchall()
            return [self._row_to_edge(row) for row in rows]

    def get_edges_between(self, source_id: str, target_id: str) -> list[GraphEdge]:
        self.initialize()
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM graph_edges
                WHERE
                    (source_id = ? AND target_id = ?)
                    OR
                    (source_id = ? AND target_id = ?)
                ORDER BY effective_weight DESC, updated_at DESC
                """,
                (source_id, target_id, target_id, source_id),
            ).fetchall()
            return [self._row_to_edge(row) for row in rows]

    def get_neighborhood(
        self,
        node_id: str,
        hops: int = 1,
        limit: int = 100,
    ) -> GraphNeighborhood:
        self.initialize()
        center_node = self.get_node(node_id)
        if center_node is None:
            return {
                "center_node_id": node_id,
                "hops": hops,
                "nodes": [],
                "edges": [],
            }

        nodes_by_id: dict[str, GraphNode] = {center_node["id"]: center_node}
        edges_by_id: dict[str, GraphEdge] = {}
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        visited_depths: dict[str, int] = {node_id: 0}

        with get_connection() as conn:
            while queue and len(nodes_by_id) < limit:
                current_node_id, depth = queue.popleft()
                if depth >= hops:
                    continue

                for edge in self._get_connected_edges(conn, current_node_id):
                    edge_record = self._row_to_edge(edge)
                    edges_by_id[edge_record["id"]] = edge_record

                    neighbor_id = (
                        edge_record["target_id"]
                        if edge_record["source_id"] == current_node_id
                        else edge_record["source_id"]
                    )

                    if neighbor_id not in nodes_by_id and len(nodes_by_id) < limit:
                        neighbor_row = self._get_node_row(conn, neighbor_id)
                        if neighbor_row is not None:
                            nodes_by_id[neighbor_id] = self._row_to_node(neighbor_row)

                    next_depth = depth + 1
                    if next_depth <= hops and visited_depths.get(neighbor_id, hops + 1) > next_depth:
                        visited_depths[neighbor_id] = next_depth
                        queue.append((neighbor_id, next_depth))

        return {
            "center_node_id": node_id,
            "hops": hops,
            "nodes": list(nodes_by_id.values()),
            "edges": list(edges_by_id.values()),
        }

    def traverse(
        self,
        seed_node_ids: list[str],
        max_hops: int,
        edge_threshold: float,
        hop_decay: float,
        max_nodes: int = 80,
        max_edges: int = 80,
    ) -> GraphTraversalResult:
        self.initialize()

        if max_hops < 0:
            raise ValueError("max_hops must be non-negative")
        if not 0.0 <= edge_threshold:
            raise ValueError("edge_threshold must be non-negative")
        if not 0.0 <= hop_decay <= 1.0:
            raise ValueError("hop_decay must be between 0.0 and 1.0")
        if max_nodes <= 0:
            raise ValueError("max_nodes must be positive")
        if max_edges <= 0:
            raise ValueError("max_edges must be positive")

        with get_connection() as conn:
            valid_seed_ids = [
                node_id for node_id in seed_node_ids if self._get_node_row(conn, node_id) is not None
            ]
            best_scores: dict[str, float] = {node_id: 1.0 for node_id in valid_seed_ids}
            visited_nodes = set(valid_seed_ids)
            traversed_edges: dict[str, GraphEdge] = {}
            frontier: list[tuple[float, int, str]] = [(-1.0, 0, node_id) for node_id in valid_seed_ids]
            heapq.heapify(frontier)

            while frontier:
                if len(visited_nodes) >= max_nodes or len(traversed_edges) >= max_edges:
                    break
                negative_score, current_hop, node_id = heapq.heappop(frontier)
                current_score = -negative_score
                if current_hop >= max_hops:
                    continue
                if current_score < best_scores.get(node_id, 0.0):
                    continue

                for edge in self._get_connected_edges(conn, node_id):
                    if len(visited_nodes) >= max_nodes or len(traversed_edges) >= max_edges:
                        break
                    edge_record = self._row_to_edge(edge)
                    if edge_record["effective_weight"] < edge_threshold:
                        continue

                    neighbor_id = (
                        edge_record["target_id"]
                        if edge_record["source_id"] == node_id
                        else edge_record["source_id"]
                    )
                    next_score = current_score * edge_record["effective_weight"] * hop_decay
                    if next_score <= 0.0:
                        continue

                    previous_score = best_scores.get(neighbor_id, 0.0)
                    if next_score > previous_score:
                        best_scores[neighbor_id] = next_score
                        if neighbor_id not in visited_nodes and len(visited_nodes) >= max_nodes:
                            continue
                        visited_nodes.add(neighbor_id)
                        traversed_edges[edge_record["id"]] = edge_record
                        heapq.heappush(frontier, (-next_score, current_hop + 1, neighbor_id))

        ordered_nodes = sorted(best_scores, key=lambda node_id: best_scores[node_id], reverse=True)
        ordered_edges = sorted(
            traversed_edges.values(),
            key=lambda edge_record: (edge_record["effective_weight"], edge_record["updated_at"]),
            reverse=True,
        )

        return {
            "seed_node_ids": valid_seed_ids,
            "visited_nodes": ordered_nodes,
            "traversed_edges": ordered_edges,
            "activation_scores": {node_id: best_scores[node_id] for node_id in ordered_nodes},
        }

    def update_edge_feedback(
        self,
        edge_id: str,
        delta: float,
        interaction_id: str | None = None,
        rating: int | None = None,
        flag: bool = False,
    ) -> dict[str, Any]:
        self.initialize()

        with get_connection() as conn:
            edge_row = conn.execute("SELECT * FROM graph_edges WHERE id = ?", (edge_id,)).fetchone()
            if edge_row is None:
                raise ValueError(f"Graph edge '{edge_id}' was not found")

            previous_feedback_delta = float(edge_row["feedback_delta"])
            previous_effective_weight = float(edge_row["effective_weight"])
            new_feedback_delta = previous_feedback_delta + delta
            new_effective_weight = max(0.0, float(edge_row["base_weight"]) + new_feedback_delta)
            new_flagged = 1 if flag else int(edge_row["flagged"])
            updated_at = utc_now_iso()

            conn.execute(
                """
                UPDATE graph_edges
                SET
                    feedback_delta = ?,
                    effective_weight = ?,
                    flagged = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    new_feedback_delta,
                    new_effective_weight,
                    new_flagged,
                    updated_at,
                    edge_id,
                ),
            )

            if interaction_id is not None and rating is not None:
                conn.execute(
                    """
                    INSERT INTO graph_edge_feedback_events (
                        id,
                        edge_id,
                        interaction_id,
                        rating,
                        delta,
                        previous_feedback_delta,
                        new_feedback_delta,
                        previous_effective_weight,
                        new_effective_weight,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        edge_id,
                        interaction_id,
                        rating,
                        delta,
                        previous_feedback_delta,
                        new_feedback_delta,
                        previous_effective_weight,
                        new_effective_weight,
                        updated_at,
                    ),
                )

            conn.commit()
            return {
                "edge_id": edge_id,
                "delta": delta,
                "flagged": bool(new_flagged),
                "previous_feedback_delta": previous_feedback_delta,
                "new_feedback_delta": new_feedback_delta,
                "previous_effective_weight": previous_effective_weight,
                "new_effective_weight": new_effective_weight,
            }

    def export_graph(self) -> dict[str, Any]:
        self.initialize()
        with get_connection() as conn:
            node_rows = conn.execute("SELECT * FROM graph_nodes ORDER BY created_at ASC").fetchall()
            edge_rows = conn.execute("SELECT * FROM graph_edges ORDER BY created_at ASC").fetchall()

        return {
            "backend": "sqlite",
            "db_path": str(self.db_path),
            "nodes": [self._row_to_node(row) for row in node_rows],
            "edges": [self._row_to_edge(row) for row in edge_rows],
        }

    def _upsert_node_record(
        self,
        node_id: str,
        node_type: str,
        label: str | None,
        properties: dict[str, Any] | None,
    ) -> GraphNode:
        self.initialize()
        with get_connection() as conn:
            node = self._upsert_node(conn, node_id, node_type, label, properties)
            conn.commit()
            return node

    def _upsert_node(
        self,
        conn,
        node_id: str,
        node_type: str,
        label: str | None,
        properties: dict[str, Any] | None,
    ) -> GraphNode:
        existing = self._get_node_row(conn, node_id)
        now = utc_now_iso()

        if existing is None:
            conn.execute(
                """
                INSERT INTO graph_nodes (
                    id,
                    node_type,
                    label,
                    properties_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    node_type = excluded.node_type,
                    label = excluded.label,
                    properties_json = excluded.properties_json,
                    updated_at = excluded.updated_at
                """,
                (
                    node_id,
                    node_type,
                    label,
                    self._encode_properties(properties or {}),
                    now,
                    now,
                ),
            )
        else:
            updated_label = label if label is not None else existing["label"]
            updated_properties = (
                properties
                if properties is not None
                else self._decode_properties(existing["properties_json"])
            )
            conn.execute(
                """
                UPDATE graph_nodes
                SET
                    node_type = ?,
                    label = ?,
                    properties_json = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    node_type,
                    updated_label,
                    self._encode_properties(updated_properties),
                    now,
                    node_id,
                ),
            )

        row = self._get_node_row(conn, node_id)
        if row is None:
            raise RuntimeError("Failed to upsert graph node")
        return self._row_to_node(row)

    def _build_edge_id(self, source_id: str, target_id: str, edge_type: str) -> str:
        digest = hashlib.sha1(f"{source_id}|{edge_type}|{target_id}".encode("utf-8")).hexdigest()
        return f"edge:{digest}"

    def _get_node_row(self, conn, node_id: str):
        return conn.execute("SELECT * FROM graph_nodes WHERE id = ?", (node_id,)).fetchone()

    def _get_edge_row(self, conn, source_id: str, target_id: str, edge_type: str):
        return conn.execute(
            """
            SELECT *
            FROM graph_edges
            WHERE source_id = ? AND target_id = ? AND edge_type = ?
            """,
            (source_id, target_id, edge_type),
        ).fetchone()

    def _get_connected_edges(self, conn, node_id: str):
        return conn.execute(
            """
            SELECT *
            FROM graph_edges
            WHERE source_id = ? OR target_id = ?
            ORDER BY effective_weight DESC, updated_at DESC
            """,
            (node_id, node_id),
        ).fetchall()

    def _row_to_node(self, row) -> GraphNode:
        return {
            "id": row["id"],
            "node_type": row["node_type"],
            "label": row["label"],
            "properties": self._decode_properties(row["properties_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _row_to_edge(self, row) -> GraphEdge:
        return {
            "id": row["id"],
            "source_id": row["source_id"],
            "target_id": row["target_id"],
            "edge_type": row["edge_type"],
            "base_weight": float(row["base_weight"]),
            "feedback_delta": float(row["feedback_delta"]),
            "effective_weight": float(row["effective_weight"]),
            "properties": self._decode_properties(row["properties_json"]),
            "flagged": bool(row["flagged"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _encode_properties(self, properties: dict[str, Any]) -> str:
        return json.dumps(properties, ensure_ascii=True, sort_keys=True)

    def _decode_properties(self, raw_value: str | None) -> dict[str, Any]:
        if not raw_value:
            return {}

        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            return {}

        return decoded if isinstance(decoded, dict) else {}
