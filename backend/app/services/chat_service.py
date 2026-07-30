"""
services/chat_service.py

PATCHED: the previous version was a pure keyword-matching stub with no
connection to the knowledge base, Bandari Engine, or any LLM — every
"hospital"/"restaurant"/"taxi" reply was a hardcoded string. This version:

1. Keeps a fast, cheap rule-based path for greeting / location_query, since
   those don't need retrieval or generation.
2. Routes everything else through CopilotGateway (Bandari normalization ->
   knowledge/graph/vector search -> domain expert or general RAG -> LLM),
   per the architecture agreed in WIRING.md.
3. Fixes a real bug in the old code: `process_message()` never returned a
   `retrieved_documents` key, but api/v1/endpoints/chat.py's ChatResponse
   model requires one — that would 500 on every request. This version
   always includes it.
4. `process_message` is now `async` because CopilotGateway is async
   end-to-end (it awaits sync engines via a thread executor internally).
   The endpoint must `await` it — see the patched endpoints/chat.py.

If no gateway is wired yet (e.g. during early integration), it falls back
to the original rule-based responses instead of crashing, so the endpoint
keeps working while you finish wiring providers/pipelines.
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

# from gateway.copilot_gateway import CopilotGateway, GatewayResponse  # adjust to real import path


class ChatService:
    def __init__(self, db=None, gateway=None):
        """
        `gateway` should be a constructed CopilotGateway (see WIRING.md,
        typically obtained once at startup via get_copilot_gateway() and
        passed in here). Optional so this file still imports/works before
        the gateway is wired up.
        """
        self.db = db
        self.gateway = gateway
        self._cache = {}

    async def process_message(
        self,
        message: str,
        user_id: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        msg_lower = message.lower()

        # --- fast path: greeting / location_query need no retrieval ---
        if any(w in msg_lower for w in ["سلام", "درود", "هی", "خوبی", "چطوری"]):
            return self._finalize(
                message, user_id, start_time,
                response="سلام! 🌊 من دستیار هوشمند هرمزگان هستم.",
                intent="greeting", confidence=0.95,
                suggestions=["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
                retrieved_documents=[],
            )

        if any(w in msg_lower for w in ["کجا", "نزدیک", "فاصله", "موقعیت", "مکان", "آدرس", "محله", "منطقه"]) and not (latitude and longitude):
            return self._finalize(
                message, user_id, start_time,
                response="لطفاً موقعیت خود را به اشتراک بگذارید.",
                intent="location_query", confidence=0.85,
                suggestions=["📍 اشتراک موقعیت"],
                retrieved_documents=[],
            )

        # --- everything else goes through CopilotGateway ---
        if self.gateway is not None:
            try:
                gw_response = await self.gateway.handle_message(message, session_id=user_id)
                return self._finalize(
                    message, user_id, start_time,
                    response=gw_response.answer,
                    intent=gw_response.intent,
                    confidence=gw_response.confidence,
                    suggestions=self._suggestions_for_intent(gw_response.intent),
                    retrieved_documents=self._sources_to_documents(gw_response.sources),
                    extra=gw_response.extra,
                )
            except Exception:
                # Gateway failure must never 500 the whole chat endpoint —
                # fall through to the rule-based reply below.
                pass

        return self._finalize(
            message, user_id, start_time,
            response="چطور می‌تونم کمکتون کنم؟",
            intent="general", confidence=0.4,
            suggestions=["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
            retrieved_documents=[],
        )

    def _finalize(
        self, message, user_id, start_time, *, response, intent, confidence,
        suggestions, retrieved_documents, extra=None,
    ) -> Dict[str, Any]:
        return {
            "message": message,
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "suggestions": suggestions,
            "retrieved_documents": retrieved_documents,
            "extra": extra or {},
            "user_id": user_id,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _suggestions_for_intent(self, intent: str) -> List[str]:
        return {
            "tourism": ["🏖️ جاذبه‌های نزدیک", "🍽️ رستوران‌ها", "🏨 هتل‌ها"],
            "traffic": ["🚦 وضعیت راه", "📷 دوربین‌های نزدیک"],
            "medical": ["🏥 نزدیک‌ترین بیمارستان", "📞 اورژانس ۱۱۵"],
            "transport": ["🚕 تاکسی", "⛽ پمپ بنزین نزدیک"],
            "general": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
        }.get(intent, ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"])

    def _sources_to_documents(self, sources: list) -> List[Dict[str, Any]]:
        docs = []
        for s in sources:
            # `s` is a pipelines.search_pipeline.RankedResult dataclass
            docs.append({
                "source": getattr(s, "source", ""),
                "title": getattr(s, "title", ""),
                "content": getattr(s, "content", ""),
                "score": getattr(s, "score", 0.0),
            })
        return docs

    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        return []

    def extract_service_type(self, text: str) -> Optional[str]:
        service_map = {
            "بیمارستان": "hospital",
            "درمانگاه": "hospital",
            "رستوران": "restaurant",
            "کافه": "restaurant",
            "تاکسی": "taxi",
            "اسنپ": "taxi",
            "تپسی": "taxi",
            "داروخانه": "pharmacy",
            "مدرسه": "school",
            "دانشگاه": "university",
            "دانشگا": "university",
            "دانش": "university",
        }
        for keyword, service_type in service_map.items():
            if keyword in text:
                return service_type
        return None

    def _extract_service_type(self, entities: List[Dict]) -> Optional[str]:
        if not entities:
            return None
        for entity in entities:
            word = entity.get("word", "")
            result = self.extract_service_type(word)
            if result:
                return result
        return None


# NOTE: no module-level singleton/getter here on purpose. ChatService is
# constructed exclusively through FastAPI's dependency injection — see
# `get_chat_service()` in dependencies/services.py, which resolves `db`
# and `gateway` (itself resolved from get_copilot_gateway, which resolves
# hotspot/camera/analytics services) before building it. A second
# `get_chat_service()` defined here would shadow/collide with that one if
# ever imported by mistake, silently bypassing DI and leaving `gateway`
# unset (this happened in an earlier draft of this integration).
