from __future__ import annotations

import threading
from typing import Any, Dict, List

from app.config import DEFAULT_BANDARI_URL
from app.providers.bandari_provider import BandariProvider

MAX_HISTORY_PER_USER = 50


class ChatService:
    """Direct HDP chat service wired to Bandari Engine."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._bandari = BandariProvider(
                        base_url=DEFAULT_BANDARI_URL
                    )
                    inst._history: Dict[str, List[dict]] = {}
                    print(
                        "✅ ChatService → BandariProvider → "
                        f"{DEFAULT_BANDARI_URL}"
                    )
                    cls._instance = inst
        return cls._instance

    async def process_message(
        self,
        message: str,
        user_id: str = "anonymous",
        **kwargs: Any,
    ) -> Dict[str, Any]:

        text = (message or "").strip()

        if not text:
            return {
                "response": "پیام خالی است",
                "intent": "general",
                "source": "validation",
                "confidence": 0.0,
                "dialect": {},
                "suggestions": [],
                "success": False,
            }

        try:
            result = await self._bandari.translate(
                text=text,
                session_id=kwargs.get("session_id"),
            )

            response = result.get(
                "translation",
                result.get("response", ""),
            )

            output = {
                "response": response,
                "intent": result.get("intent", "general"),
                "source": result.get("source", "bandari"),
                "confidence": result.get("confidence", 0.0),
                "normalized_text": text,
                "dialect": result.get("dialect", {}),
                "suggestions": result.get("suggestions", []),
                "search_results": {
                    "knowledge_count": 0
                },
                "success": result.get("success", True),
            }

        except Exception as exc:
            output = {
                "response": f"خطا در اتصال به موتور بندری: {exc}",
                "intent": "general",
                "source": "bandari_error",
                "confidence": 0.0,
                "dialect": {},
                "suggestions": [],
                "search_results": {
                    "knowledge_count": 0
                },
                "success": False,
            }

        history = self._history.setdefault(user_id, [])
        history.append(output)

        if len(history) > MAX_HISTORY_PER_USER:
            del history[:-MAX_HISTORY_PER_USER]

        return output

    async def get_chat_history(
        self,
        user_id: str,
        limit: int = 50,
    ) -> List[Dict]:
        return self._history.get(user_id, [])[-limit:]


def get_chat_service() -> ChatService:
    return ChatService()
