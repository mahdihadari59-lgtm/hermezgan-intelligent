"""
experts/traffic_expert.py

Answers traffic/road-condition questions. Adds live data from the existing
hotspot_repository / camera_repository (already in repositories/) so
answers reflect current conditions, not just static knowledge content.
"""

from __future__ import annotations

from typing import Any

from app.experts import BaseExpert
from app.pipelines.rag_pipeline import RAGResult


class TrafficExpert(BaseExpert):
    domain = "traffic"
    category = "traffic"

    def __init__(self, rag, hotspot_repository: Any = None, camera_repository: Any = None):
        super().__init__(rag)
        self.hotspot_repository = hotspot_repository
        self.camera_repository = camera_repository

    async def enrich(self, user_text: str, result: RAGResult) -> dict:
        extra: dict = {}

        if self.hotspot_repository is not None and hasattr(self.hotspot_repository, "get_active"):
            try:
                extra["active_hotspots"] = self.hotspot_repository.get_active()
            except Exception:  # noqa: BLE001 - live data is best-effort
                extra["active_hotspots"] = []

        if self.camera_repository is not None and hasattr(self.camera_repository, "get_nearby_text_match"):
            try:
                extra["nearby_cameras"] = self.camera_repository.get_nearby_text_match(user_text)
            except Exception:  # noqa: BLE001
                extra["nearby_cameras"] = []

        return extra
