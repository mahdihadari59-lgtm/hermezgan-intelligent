"""
providers/knowledge_provider.py

Thin async adapter over the REAL KnowledgeBase (core/engine/hybrid/knowledge_base.py):

    class KnowledgeBase:
        def search(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict]
        ...
    def get_knowledge_base() -> KnowledgeBase   # module-level singleton factory

KnowledgeBase is fully synchronous (in-memory list + JSON file persistence),
so every call is pushed to a thread executor to avoid blocking the event
loop.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from . import BaseProvider, ProviderError


class KnowledgeProvider(BaseProvider):
    name = "knowledge"

    def __init__(self, engine: Any = None, timeout: float = 4.0):
        """
        `engine` may be a KnowledgeBase instance you already constructed
        (e.g. via `get_knowledge_base()` at startup and passed in once, so
        every request shares the same in-memory index). If omitted, the
        provider lazily calls `get_knowledge_base()` itself on first use.
        """
        super().__init__(timeout=timeout)
        self._engine = engine

    def _resolve_engine(self):
        if self._engine is not None:
            return self._engine
        try:
            from core.engine.hybrid.knowledge_base import get_knowledge_base  # type: ignore

            self._engine = get_knowledge_base()
            return self._engine
        except ImportError as exc:  # pragma: no cover - environment-specific
            raise ProviderError(f"knowledge: engine not injected and import failed: {exc}") from exc

    async def _execute(self, payload: dict) -> dict:
        engine = self._resolve_engine()

        if payload.get("__health__"):
            return {"ok": True}

        query = payload.get("query", "")
        category = payload.get("category")
        limit = int(payload.get("limit", 8))

        if not query:
            raise ProviderError("knowledge: 'query' is required")

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None, partial(engine.search, query, category=category, limit=limit)
        )
        # KnowledgeBase.search() already returns dicts shaped like
        # {"id", "title", "content", "category", "metadata", "score", "_source": "knowledge"}
        return {"query": query, "results": results}

    async def search(self, query: str, category: str | None = None, limit: int = 8) -> list[dict]:
        result = await self.query({"query": query, "category": category, "limit": limit})
        return result.get("results", [])
