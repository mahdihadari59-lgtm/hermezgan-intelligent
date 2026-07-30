"""
providers/vector_provider.py

Thin async adapter over the REAL VectorStore (core/engine/hybrid/vector_store.py):

    class VectorStore:
        def search(self, query: str, top_k: int = 10, threshold: float = 0.5) -> List[Dict]
        ...
    def get_vector_store() -> VectorStore   # module-level singleton factory

Important: VectorStore.search() takes the raw query TEXT and embeds it
internally via EmbeddingService — you do not pass a vector in, and there is
no separate embedder to inject here (unlike the earlier draft of this file).

VectorStore is synchronous (numpy cosine similarity + JSON persistence), so
calls are pushed to a thread executor.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from . import BaseProvider, ProviderError


class VectorProvider(BaseProvider):
    name = "vector"

    def __init__(self, store: Any = None, timeout: float = 4.0):
        super().__init__(timeout=timeout)
        self._store = store

    def _resolve_store(self):
        if self._store is not None:
            return self._store
        try:
            from core.engine.hybrid.vector_store import get_vector_store  # type: ignore

            self._store = get_vector_store()
            return self._store
        except ImportError as exc:  # pragma: no cover
            raise ProviderError(f"vector: store not injected and import failed: {exc}") from exc

    async def _execute(self, payload: dict) -> dict:
        store = self._resolve_store()

        if payload.get("__health__"):
            return {"ok": True}

        text = payload.get("text", "")
        top_k = int(payload.get("top_k", 5))
        threshold = float(payload.get("threshold", 0.5))
        if not text:
            raise ProviderError("vector: 'text' is required")

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None, partial(store.search, text, top_k=top_k, threshold=threshold)
        )
        # Each item is the stored document dict (id, text, metadata, created_at) + "score"
        return {"text": text, "results": results}

    async def nearest(self, text: str, top_k: int = 5, threshold: float = 0.5) -> list[dict]:
        result = await self.query({"text": text, "top_k": top_k, "threshold": threshold})
        return result.get("results", [])
