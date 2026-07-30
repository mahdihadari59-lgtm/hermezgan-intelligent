"""
pipelines/search_pipeline.py

Fans a query out to KnowledgeProvider (BM25/FTS5), GraphProvider (BFS
traversal) and VectorProvider (semantic nearest-neighbor) in parallel,
then merges + re-ranks into a single ordered result list.

This does NOT talk to Bandari or an LLM — it is pure retrieval. RAGPipeline
composes this with generation.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from app.providers import ProviderError
from app.providers.graph_provider import GraphProvider
from app.providers.knowledge_provider import KnowledgeProvider
from app.providers.vector_provider import VectorProvider

logger = logging.getLogger("hdp.pipelines.search")


@dataclass
class RankedResult:
    source: str  # "knowledge" | "graph" | "vector"
    title: str
    content: str
    score: float
    raw: dict = field(default_factory=dict)


class SearchPipeline:
    # Source weights for the fused score. Knowledge (FTS/BM25) is the most
    # reliable signal for HDP's curated content; graph and vector add recall.
    WEIGHTS = {"knowledge": 1.0, "graph": 0.7, "vector": 0.8}

    def __init__(
        self,
        knowledge: KnowledgeProvider,
        graph: GraphProvider,
        vector: VectorProvider,
    ):
        self.knowledge = knowledge
        self.graph = graph
        self.vector = vector

    async def run(self, query: str, category: str | None = None, top_k: int = 8) -> list[RankedResult]:
        tasks = [
            self._safe(self.knowledge.search(query, category=category, limit=top_k), "knowledge"),
            self._safe(self.vector.nearest(query, top_k=top_k), "vector"),
            self._safe(self.graph.search(query, max_depth=2), "graph"),
        ]
        knowledge_res, vector_res, graph_res = await asyncio.gather(*tasks)

        merged: list[RankedResult] = []
        merged += self._to_ranked(knowledge_res, "knowledge")
        merged += self._to_ranked(vector_res, "vector")
        merged += self._to_ranked(graph_res, "graph")

        deduped = self._dedupe(merged)
        deduped.sort(key=lambda r: r.score, reverse=True)
        return deduped[:top_k]

    async def _safe(self, coro, label: str) -> list[dict]:
        try:
            return await coro
        except ProviderError as exc:
            logger.warning("search_pipeline: %s source unavailable: %s", label, exc)
            return []

    def _to_ranked(self, items: list[dict], source: str) -> list[RankedResult]:
        weight = self.WEIGHTS.get(source, 0.5)
        extractor = {
            "knowledge": self._extract_knowledge,
            "vector": self._extract_vector,
            "graph": self._extract_graph,
        }[source]

        ranked = []
        for item in items:
            title, content = extractor(item)
            base_score = float(item.get("score", 1.0))
            ranked.append(
                RankedResult(source=source, title=title, content=content, score=base_score * weight, raw=item)
            )
        return ranked

    @staticmethod
    def _extract_knowledge(item: dict) -> tuple[str, str]:
        # KnowledgeBase.search() -> {"id","title","content","category","metadata","score"}
        return item.get("title", ""), item.get("content", "")

    @staticmethod
    def _extract_vector(item: dict) -> tuple[str, str]:
        # VectorStore.search() -> {"id","text","metadata","created_at","score"}
        metadata = item.get("metadata") or {}
        title = metadata.get("title", "") if isinstance(metadata, dict) else ""
        return title, item.get("text", "")

    @staticmethod
    def _extract_graph(item: dict) -> tuple[str, str]:
        # GraphStore.search() -> {"id","type","properties","score", optional "relation"/"source"}
        properties = item.get("properties") or {}
        title = properties.get("title") or properties.get("name") or item.get("id", "")
        # Build a compact readable summary from properties since there's no free-text "content".
        parts = [f"{k}: {v}" for k, v in properties.items() if isinstance(v, (str, int, float))]
        content = "؛ ".join(parts) if parts else item.get("type", "")
        if item.get("relation"):
            content = f"[{item['relation']}] {content}"
        return title, content

    def _dedupe(self, results: list[RankedResult]) -> list[RankedResult]:
        """Collapse near-duplicate titles across sources, keeping the highest score."""
        best: dict[str, RankedResult] = {}
        for r in results:
            key = (r.title or r.content[:60]).strip()
            if key not in best or r.score > best[key].score:
                best[key] = r
        return list(best.values())
