from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.providers.knowledge_provider import KnowledgeProvider
from app.providers.graph_provider import GraphProvider
from app.providers.vector_provider import VectorProvider


class SearchPipeline:
    def __init__(
        self,
        knowledge: KnowledgeProvider,
        graph: GraphProvider,
        vector: VectorProvider,
    ):
        self.knowledge = knowledge
        self.graph = graph
        self.vector = vector

    async def search(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        text_hits = await self.knowledge.search(query, limit=limit * 2, category=category, intent=intent)

        if not text_hits and (category is not None or intent is not None):
            text_hits = await self.knowledge.search(query, limit=limit * 2, category=None, intent=None)

        results: List[Dict[str, Any]] = []
        for item in text_hits:
            result = dict(item)
            result["source"] = "knowledge"
            results.append(result)

        return results[:limit]

    async def answer(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Dict[str, Any]:
        hits = await self.search(query, limit=limit, category=category, intent=intent)

        if not hits:
            return {"answer": "در دانش اصلی پاسخی پیدا نشد.", "results": []}

        top = hits[0]
        answer_parts = [
            top.get("answer"),
            top.get("content"),
            top.get("snippet"),
            top.get("title"),
        ]
        answer = next(
            (part for part in answer_parts if isinstance(part, str) and part.strip()),
            "نتیجه پیدا شد اما متن پاسخ خالی است.",
        )

        return {"answer": answer, "results": hits}
