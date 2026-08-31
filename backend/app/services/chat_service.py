from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hdp_ai_v6_dual import HDPAIV6Dual

MAX_HISTORY_PER_USER = 50


class ChatService:
    """HDP chat service wired to HDPAIV6Dual (bandari dialect + hormozgan DB search)."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._ai = HDPAIV6Dual()
                    inst._history: Dict[str, List[dict]] = {}
                    print("✅ ChatService → HDPAIV6Dual (dual DB) wired")
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
            lat = kwargs.get("latitude")
            lon = kwargs.get("longitude")
            r = self._ai.process(text, user_lat=lat, user_lon=lon)

            output = {
                "response": r.response,
                "intent": r.intent,
                "source": "hdp_ai_v6_dual",
                "confidence": r.confidence,
                "normalized_text": text,
                "dialect": {"code": r.dialect},
                "suggestions": [],
                "search_results": {
                    "knowledge_count": len(r.results)
                },
                "results": r.results,
                "translation": r.translation,
                "elapsed_ms": r.elapsed_ms,
                "success": True,
            }
        except Exception as exc:
            output = {
                "response": f"خطا در پردازش: {exc}",
                "intent": "general",
                "source": "hdp_ai_error",
                "confidence": 0.0,
                "dialect": {},
                "suggestions": [],
                "search_results": {"knowledge_count": 0},
                "success": False,
            }

        history = self._history.setdefault(user_id, [])
        history.append(output)
        if len(history) > MAX_HISTORY_PER_USER:
            del history[:-MAX_HISTORY_PER_USER]

        return output

    async def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        return self._history.get(user_id, [])[-limit:]


def get_chat_service() -> ChatService:
    return ChatService()
