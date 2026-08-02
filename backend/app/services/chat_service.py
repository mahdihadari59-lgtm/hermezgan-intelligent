from __future__ import annotations

import threading
import logging
from typing import Any, Dict, List

from app.config import HDP_KNOWLEDGE_DB_PATH, DEFAULT_BANDARI_URL
from app.gateway.copilot_gateway import CopilotGateway

logger = logging.getLogger(__name__)

MAX_HISTORY_PER_USER = 50


class ChatService:
    """Wrapper نازک روی CopilotGateway؛ فقط تاریخچه‌ی مکالمه رو اضافه می‌کند."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._gateway = CopilotGateway(
                        db_path=str(HDP_KNOWLEDGE_DB_PATH),
                        bandari_url=DEFAULT_BANDARI_URL,
                    )
                    inst._history: Dict[str, List[dict]] = {}
                    logger.info("✅ ChatService wired to CopilotGateway")
                    cls._instance = inst
        return cls._instance

    async def process_message(self, message: str, user_id: str = "anonymous", **kwargs) -> Dict[str, Any]:
        text = message.strip()
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
            gw_result = await self._gateway.handle_message(
                text=text,
                session_id=kwargs.get("session_id"),
                user_id=user_id,
            )
        except Exception:
            logger.exception("CopilotGateway.handle_message failed")
            return {
                "response": "خطا در پردازش پیام؛ لطفاً دوباره تلاش کنید.",
                "intent": "general",
                "source": "error",
                "confidence": 0.0,
                "dialect": {},
                "suggestions": [],
                "success": False,
            }

        retrieved = gw_result.get("retrieved_documents") or []

        result = {
            "response": gw_result.get("response", ""),
            "intent": gw_result.get("intent", "general"),
            "source": "knowledge" if retrieved else "fallback",
            "confidence": gw_result.get("confidence", 0.0),
            "normalized_text": text,
            "dialect": gw_result.get("dialect", {}),
            "suggestions": gw_result.get("suggestions", []),
            "search_results": {"knowledge_count": len(retrieved)},
            "success": True,
        }

        hist = self._history.setdefault(user_id, [])
        hist.append(result)
        if len(hist) > MAX_HISTORY_PER_USER:
            del hist[0: len(hist) - MAX_HISTORY_PER_USER]

        return result

    async def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        return self._history.get(user_id, [])[-limit:]


def get_chat_service() -> ChatService:
    return ChatService()
