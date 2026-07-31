from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import HDP_KNOWLEDGE_DB_PATH
from app.gateway.copilot_gateway import CopilotGateway


_gateway = CopilotGateway(db_path=str(HDP_KNOWLEDGE_DB_PATH))

_DEFAULT_SUGGESTIONS = {
    "hospital": ["📞 تماس", "🧭 مسیریابی", "دیگر بیمارستان‌ها"],
    "restaurant": ["🍽️ صفحه رستوران", "⭐ نظرات", "📞 تماس"],
    "taxi": ["⏱️ زمان باقی‌مانده", "📞 تماس راننده", "❌ لغو"],
    "greeting": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
    "general": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
}


class ChatService:
    async def process_message(
        self,
        message: str,
        user_id: str,
        latitude: float | None = None,
        longitude: float | None = None,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        result = await _gateway.handle_message(
            text=message,
            session_id=session_id,
            user_id=user_id,
        )

        intent_data = result.get("intent") or {}
        if not isinstance(intent_data, dict):
            intent_data = {}

        knowledge = result.get("knowledge") or {}
        if not isinstance(knowledge, dict):
            knowledge = {}

        intent_name = str(
            intent_data.get("intent")
            or intent_data.get("category")
            or "general"
        ).strip().lower()

        response_text = (
            result.get("response")
            or knowledge.get("answer")
            or result.get("answer")
            or "پاسخی پیدا نشد."
        )

        confidence = intent_data.get("confidence", 1.0)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 1.0

        retrieved_documents = knowledge.get("results") or []
        if not isinstance(retrieved_documents, list):
            retrieved_documents = []

        return {
            "response": response_text,
            "intent": intent_name or "general",
            "confidence": confidence,
            "suggestions": _DEFAULT_SUGGESTIONS.get(intent_name, _DEFAULT_SUGGESTIONS["general"]),
            "retrieved_documents": retrieved_documents,
            "dialect": result.get("dialect"),
            "knowledge": knowledge,
            "session_id": session_id,
            "location": {
                "lat": latitude,
                "lng": longitude,
            } if latitude is not None and longitude is not None else None,
        }

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await _gateway.handle_message(
            text=message,
            session_id=session_id,
            user_id=user_id,
        )

    async def handle_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.chat(
            message,
            session_id=session_id,
            user_id=user_id,
        )


async def chat(
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    return await _gateway.handle_message(
        text=message,
        session_id=session_id,
        user_id=user_id,
    )


def get_chat_service() -> ChatService:
    """
    FastAPI dependency provider
    """
    return ChatService()
