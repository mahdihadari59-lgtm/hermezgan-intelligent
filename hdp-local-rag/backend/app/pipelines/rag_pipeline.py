from __future__ import annotations

from typing import Any, Dict, Optional

from app.pipelines.search_pipeline import SearchPipeline
from app.providers.bandari_provider import BandariProvider


class RagPipeline:
    def __init__(self, bandari: BandariProvider, search_pipeline: SearchPipeline):
        self.bandari = bandari
        self.search_pipeline = search_pipeline

    async def run(self, text: str, session_id: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        bandari_intent = await self.bandari.intent(text)
        bandari_detect = await self.bandari.detect(text)
        search_result = await self.search_pipeline.answer(
            text,
            limit=limit,
            category=bandari_intent.get("category"),
            intent=bandari_intent.get("intent"),
        )
        return {
            "input": text,
            "intent": bandari_intent,
            "dialect": bandari_detect,
            "knowledge": search_result,
            "answer": search_result["answer"],
        }
