"""
experts/transport_expert.py

Covers ride-hailing, public transport, and fuel-station questions — the
domains closest to HDP's original hormozgandriver.ir product. Enriches
with live fuel-station data from api/fuel.py when available.
"""

from __future__ import annotations

from typing import Any

from app.experts import BaseExpert
from app.pipelines.rag_pipeline import RAGResult


class TransportExpert(BaseExpert):
    domain = "transport"
    category = "transport"

    def __init__(self, rag, fuel_service: Any = None):
        super().__init__(rag)
        self.fuel_service = fuel_service

    async def enrich(self, user_text: str, result: RAGResult) -> dict:
        extra: dict = {}

        if self.fuel_service is not None and hasattr(self.fuel_service, "search_stations"):
            try:
                extra["fuel_stations"] = self.fuel_service.search_stations(user_text)
            except Exception:  # noqa: BLE001
                extra["fuel_stations"] = []

        return extra
