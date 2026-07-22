from typing import List, Dict, Any, Optional, Set
import logging
import json
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class GraphStore:
    """
    ذخیره‌سازی گرافی برای روابط بین موجودیت‌ها
    """

    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
        self._index_path = Path("data/graph_store.json")

        self._load()

        logger.info(f"✅ Graph Store initialized with {len(self.nodes)} nodes")

    def add_node(self, node: Dict[str, Any]) -> bool:
        try:
            node_id = node.get("id")
            if not node_id:
                logger.warning("⚠️ Node has no id")
                return False

            self.nodes[node_id] = {
                "id": node_id,
                "type": node.get("type", "unknown"),
                "properties": node.get("properties", {}),
                "created_at": node.get("created_at")
            }

            self._save()
            return True

        except Exception as e:
            logger.error(f"❌ Error adding node to graph store: {e}")
            return False

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        properties: Optional[Dict] = None
    ) -> bool:
        try:
            if source_id not in self.nodes or target_id not in self.nodes:
                logger.warning(f"⚠️ Source or target node not found: {source_id} -> {target_id}")
                return False

            edge = {
                "source": source_id,
                "target": target_id,
                "relation": relation,
                "properties": properties or {}
            }

            self.edges[source_id].append(edge)

            self._save()
            return True

        except Exception as e:
            logger.error(f"❌ Error adding edge to graph store: {e}")
            return False

    def search(
        self,
        query: str,
        limit: int = 20,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()

        for node_id, node in self.nodes.items():
            score = self._calculate_node_score(node, query_lower)
            if score > 0:
                results.append({
                    "id": node_id,
                    "type": node["type"],
                    "properties": node["properties"],
                    "score": score,
                    "_source": "graph"
                })

        for source_id, edges in self.edges.items():
            for edge in edges:
                if query_lower in edge.get("relation", "").lower():
                    target_node = self.nodes.get(edge["target"])
                    if target_node:
                        results.append({
                            "id": edge["target"],
                            "type": target_node["type"],
                            "properties": target_node["properties"],
                            "score": 0.7,
                            "_source": "graph",
                            "relation": edge["relation"],
                            "source": source_id
                        })

        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return results[:limit]

    def _calculate_node_score(self, node: Dict[str, Any], query: str) -> float:
        score = 0
        properties = node.get("properties", {})

        for key, value in properties.items():
            if isinstance(value, str):
                if query in value.lower():
                    score += 0.3

                if any(query in word for word in value.lower().split()):
                    score += 0.2

        node_type = node.get("type", "")
        if node_type and query in node_type:
            score += 0.5

        return min(score, 1.0)

    def get_node(self, node_id: str) -> Optional[Dict]:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[Dict]:
        neighbors = []

        for edge in self.edges.get(node_id, []):
            target = self.nodes.get(edge["target"])
            if target:
                neighbors.append({
                    "node": target,
                    "relation": edge["relation"]
                })

        for source_id, edges in self.edges.items():
            for edge in edges:
                if edge["target"] == node_id:
                    source = self.nodes.get(source_id)
                    if source:
                        neighbors.append({
                            "node": source,
                            "relation": f"inverse_{edge['relation']}"
                        })

        return neighbors

    def _save(self):
        try:
            data = {
                "nodes": self.nodes,
                "edges": dict(self.edges)
            }

            self._index_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"❌ Error saving graph store: {e}")

    def _load(self):
        try:
            if not self._index_path.exists():
                return

            with open(self._index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.nodes = data.get("nodes", {})
            self.edges = defaultdict(list, data.get("edges", {}))

        except Exception as e:
            logger.error(f"❌ Error loading graph store: {e}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": sum(len(edges) for edges in self.edges.values()),
            "node_types": list(set(node["type"] for node in self.nodes.values()))
        }


_graph_store = None


def get_graph_store() -> GraphStore:
    global _graph_store
    if _graph_store is None:
        _graph_store = GraphStore()
    return _graph_store
