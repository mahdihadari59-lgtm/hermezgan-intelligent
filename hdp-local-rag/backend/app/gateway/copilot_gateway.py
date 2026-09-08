from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import HDP_KNOWLEDGE_DB_PATH, DEFAULT_BANDARI_URL
from app.pipelines.search_pipeline import SearchPipeline
from app.providers.bandari_provider import BandariProvider
from app.providers.knowledge_provider import KnowledgeProvider
from app.providers.graph_provider import GraphProvider
from app.providers.vector_provider import VectorProvider


class CopilotGateway:
    def __init__(
        self,
        db_path: Optional[str] = None,
        bandari_url: str = DEFAULT_BANDARI_URL,
    ):
        db_path = db_path or str(HDP_KNOWLEDGE_DB_PATH)
        self.bandari = BandariProvider(base_url=bandari_url)
        self.knowledge = KnowledgeProvider(db_path)
        self.graph = GraphProvider(db_path)
        self.vector = VectorProvider(db_path)
        self.search_pipeline = SearchPipeline(self.knowledge, self.graph, self.vector)

    def _normalize_intent(self, bandari_intent: Any) -> tuple[Optional[str], Optional[str], float]:
        if not isinstance(bandari_intent, dict):
            return None, None, 1.0

        raw_intent = (bandari_intent.get("intent") or "").strip().lower()
        raw_category = (bandari_intent.get("category") or "").strip().lower()
        confidence = bandari_intent.get("confidence", 1.0)

        try:
            confidence = float(confidence)
        except Exception:
            confidence = 1.0

        if raw_intent in {"", "general", "unknown", "other", "none"}:
            raw_intent = None
        if raw_category in {"", "general", "unknown", "other", "none"}:
            raw_category = None

        return raw_intent, raw_category, confidence

    async def handle_message(
        self,
        text: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        bandari_intent: Dict[str, Any] = {}
        bandari_detect: Dict[str, Any] = {}
        intent: Optional[str] = None
        category: Optional[str] = None
        confidence: float = 1.0

        try:
            bandari_intent = await self.bandari.intent(text)
            bandari_detect = await self.bandari.detect(text)
            intent, category, confidence = self._normalize_intent(bandari_intent)
        except Exception:
            bandari_intent = {}
            bandari_detect = {}
            intent = None
            category = None
            confidence = 1.0

        search_result = await self.search_pipeline.answer(
            text,
            limit=5,
            category=category,
            intent=intent,
        )

        return {
            "response": search_result["answer"],
            "intent": intent or "general",
            "confidence": confidence,
            "suggestions": [],
            "retrieved_documents": search_result.get("results", []),
            "knowledge": search_result,
            "dialect": bandari_detect,
            "session_id": session_id,
            "user_id": user_id,
            "answer": search_result["answer"],
        }
