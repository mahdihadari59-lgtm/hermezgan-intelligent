"""
gateway/copilot_gateway.py

Single coordination point for the whole system, as specified:

    Frontend -> FastAPI -> CopilotService
                              |-- HybridEngine (via SearchPipeline)
                              |-- KnowledgeBase (via KnowledgeProvider)
                              |-- BandariEngine (via BandariProvider)
                              |-- Weather
                              |-- Analytics
                              |-- Tourism / Traffic / Medical / Transport experts

No other endpoint should call providers/pipelines/experts directly — every
chat-style request from api/v1/chat.py (or endpoints/chat.py, voice.py)
should go through `CopilotGateway.handle_message` / `handle_voice`.

Intent routing here is deliberately simple (keyword scoring, stdlib-only,
no ML dependency) so it works offline on Termux. Swap `_classify_intent`
for a real classifier later without touching call sites.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from app.experts import BaseExpert, ExpertResponse
from app.experts.medical_expert import MedicalExpert
from app.experts.tourism_expert import TourismExpert
from app.experts.traffic_expert import TrafficExpert
from app.experts.transport_expert import TransportExpert
from app.pipelines.rag_pipeline import RAGPipeline
from app.pipelines.voice_pipeline import VoicePipeline, VoiceResult

logger = logging.getLogger("hdp.gateway")

# Keyword sets used for lightweight intent routing. Extend freely; this is
# intentionally simple and transparent rather than a black-box classifier.
_INTENT_KEYWORDS: dict[str, list[str]] = {
    "tourism": ["جاذبه", "گردشگری", "ساحل", "هتل", "بازدید", "توریست", "رستوران", "غذا", "کباب", "کافه"],
    "traffic": ["ترافیک", "تصادف", "بسته", "شلوغی", "جاده", "مسیر"],
    "medical": ["بیمارستان", "درمانگاه", "پزشک", "اورژانس", "دارو"],
    "transport": ["تاکسی", "اسنپ", "تپسی", "پمپ بنزین", "سوخت", "اتوبوس", "حمل"],
}


@dataclass
class GatewayResponse:
    intent: str
    expert: Optional[str]
    answer: str
    confidence: float = 0.5
    sources: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)


class CopilotGateway:
    def __init__(
        self,
        rag: RAGPipeline,
        voice: Optional[VoicePipeline] = None,
        analytics_service: Any = None,
        tourism: Optional[TourismExpert] = None,
        traffic: Optional[TrafficExpert] = None,
        medical: Optional[MedicalExpert] = None,
        transport: Optional[TransportExpert] = None,
    ):
        self.rag = rag
        self.voice = voice
        self.analytics_service = analytics_service
        self._experts: dict[str, BaseExpert] = {
            e.domain: e
            for e in (tourism, traffic, medical, transport)
            if e is not None
        }

    async def handle_message(self, user_text: str, session_id: str | None = None) -> GatewayResponse:
        intent, confidence = self._classify_intent(user_text)
        expert = self._experts.get(intent)

        if expert is not None:
            resp: ExpertResponse = await expert.answer(user_text)
            self._log_analytics(session_id, intent, user_text)
            return GatewayResponse(
                intent=intent, expert=expert.domain, answer=resp.answer,
                confidence=confidence, sources=resp.sources, extra=resp.extra,
            )

        # No specialized expert matched -> general RAG over the whole knowledge base.
        result = await self.rag.answer(user_text, category=None)
        self._log_analytics(session_id, "general", user_text)
        return GatewayResponse(intent="general", expert=None, answer=result.answer, confidence=confidence, sources=result.sources)

    async def handle_voice(self, audio_bytes: bytes, session_id: str | None = None) -> VoiceResult:
        if self.voice is None:
            raise RuntimeError("CopilotGateway: voice pipeline not configured")
        result = await self.voice.handle_audio(audio_bytes)
        self._log_analytics(session_id, "voice", result.transcript)
        return result

    def _classify_intent(self, text: str) -> tuple[str, float]:
        scores = {intent: 0 for intent in _INTENT_KEYWORDS}
        for intent, keywords in _INTENT_KEYWORDS.items():
            scores[intent] = sum(1 for kw in keywords if kw in text)

        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        if best_score == 0:
            return "general", 0.4
        # More keyword hits -> higher confidence, capped so it never claims certainty.
        confidence = min(0.95, 0.6 + 0.15 * best_score)
        return best_intent, confidence

    def _log_analytics(self, session_id: str | None, intent: str, text: str) -> None:
        if self.analytics_service is None:
            return
        try:
            if hasattr(self.analytics_service, "log_interaction"):
                self.analytics_service.log_interaction(session_id=session_id, intent=intent, text=text)
        except Exception as exc:  # noqa: BLE001 - analytics must never break the chat path
            logger.warning("gateway: analytics logging failed: %s", exc)
