"""
providers/bandari_provider.py

Wraps the standalone Bandari Engine service (dialect detection, morphology,
dictionary lookup, LLM adapter) running on http://127.0.0.1:5200.

This is the ONLY place in the backend that should know the Bandari Engine's
network address. Everything else (chat_service, hybrid_engine, gateway)
talks to it through this provider so the engine can move host/port later
without touching call sites.
"""

from __future__ import annotations

from typing import Optional

from . import BaseProvider, ProviderError


class BandariProvider(BaseProvider):
    name = "bandari"

    def __init__(self, base_url: str = "http://127.0.0.1:5200", timeout: float = 3.0):
        super().__init__(timeout=timeout, failure_threshold=5, recovery_timeout=20.0)
        self.base_url = base_url.rstrip("/")

    async def _execute(self, payload: dict) -> dict:
        if payload.get("__health__"):
            return await self._http_get(f"{self.base_url}/api/stats")

        text = payload.get("text", "")
        if not text:
            raise ProviderError("bandari: 'text' is required")

        return await self._http_post(
            f"{self.base_url}/api/translate",
            {"text": text, "direction": payload.get("direction", "auto")},
        )

    async def translate(self, text: str, direction: str = "auto") -> dict:
        """Convenience wrapper: Bandari <-> Standard Persian translation + dialect detection."""
        return await self.query({"text": text, "direction": direction})

    async def stats(self) -> Optional[dict]:
        try:
            return await self.query({"__health__": True})
        except ProviderError:
            return None
