import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from loguru import logger

from app.services.geo_link_service import enrich_geo as _enrich_geo
from app.core.engine.hybrid.hybrid_engine import get_hybrid_engine


class ChatService:
    def __init__(self, db=None):
        self.db = db
        self._cache = {}
        self._hybrid_engine = None

    @property
    def hybrid_engine(self):
        if self._hybrid_engine is None:
            self._hybrid_engine = get_hybrid_engine()
        return self._hybrid_engine

    def process_message(
        self,
        message: str,
        user_id: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        msg_lower = message.lower()

        # فست‌پث برای احوال‌پرسی ساده - نیازی به سرچ نداره
        if any(w in msg_lower for w in ["سلام", "درود", "هی", "خوبی", "چطوری"]):
            return {
                "message": message,
                "response": "سلام! 🌊 من دستیار هوشمند هرمزگان هستم. چطور می‌تونم کمکتون کنم؟",
                "intent": "greeting",
                "confidence": 0.95,
                "suggestions": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
                "retrieved_documents": [],
                "user_id": user_id,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        service_type = self.extract_service_type(message)
        intent = service_type or "general"

        try:
            result = self.hybrid_engine.answer(message)
            response = result.get("answer", "متأسفانه اطلاعاتی پیدا نشد.")
            confidence = result.get("confidence", 0.5)
            sources = result.get("sources", [])
        except Exception as e:
            logger.error(f"HybridEngine error: {e}")
            response = "در حال حاضر امکان جستجو وجود نداره، لطفاً دوباره امتحان کنید."
            confidence = 0.0
            sources = []

        suggestions = ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
        if intent == "location_query" and not (latitude and longitude):
            suggestions = ["📍 اشتراک موقعیت"]

        return {
            "message": message,
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "suggestions": suggestions,
            "retrieved_documents": sources,
            "user_id": user_id,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

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
                return _enrich_geo(result)
        return None


_chat_service_instance = None


def get_chat_service(db=None) -> ChatService:
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService(db)
    return _chat_service_instance
