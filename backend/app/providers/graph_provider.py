"""
providers/graph_provider.py

Thin async adapter over the REAL GraphStore (core/engine/hybrid/graph_store.py):

    class GraphStore:
        def search(self, query: str, limit: int = 20, max_depth: int = 2) -> List[Dict]
        def get_neighbors(self, node_id: str) -> List[Dict]
        ...
    def get_graph_store() -> GraphStore   # module-level singleton factory

Note: there is no `traverse()` method on the real class — `search()` already
does keyword matching over nodes AND edge relations. `get_neighbors()` is
exposed separately for 1-hop expansion when you already have a node id
(e.g. after a knowledge/vector hit resolves to a graph node).

GraphStore is fully synchronous (in-memory dict + JSON file persistence),
so calls are pushed to a thread executor.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from . import BaseProvider, ProviderError


class GraphProvider(BaseProvider):
    name = "graph"

    def __init__(self, engine: Any = None, timeout: float = 4.0):
        super().__init__(timeout=timeout)
        self._engine = engine

    def _resolve_engine(self):
        if self._engine is not None:
            return self._engine
        try:
            from core.engine.hybrid.graph_store import get_graph_store  # type: ignore

            self._engine = get_graph_store()
            return self._engine
        except ImportError as exc:  # pragma: no cover
            raise ProviderError(f"graph: engine not injected and import failed: {exc}") from exc

    async def _execute(self, payload: dict) -> dict:
        engine = self._resolve_engine()
        loop = asyncio.get_running_loop()

        if payload.get("__health__"):
            return {"ok": True}

        node_id = payload.get("node_id")
        if node_id:
            neighbors = await loop.run_in_executor(None, engine.get_neighbors, node_id)
            return {"node_id": node_id, "neighbors": neighbors}

        query = payload.get("query")
        if not query:
            raise ProviderError("graph: 'query' or 'node_id' is required")

        limit = int(payload.get("limit", 20))
        max_depth = int(payload.get("max_depth", 2))

        results = await loop.run_in_executor(
            None, partial(engine.search, query, limit=limit, max_depth=max_depth)
        )
        # Shaped like {"id", "type", "properties", "score", "_source": "graph", ...}
        return {"query": query, "results": results}

    async def search(self, query: str, limit: int = 20, max_depth: int = 2) -> list[dict]:
        result = await self.query({"query": query, "limit": limit, "max_depth": max_depth})
        return result.get("results", [])

    async def neighbors(self, node_id: str) -> list[dict]:
        result = await self.query({"node_id": node_id})
        return result.get("neighbors", [])
