import time
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class ChatService:
    def __init__(self, db=None):
        self.db = db
        self._cache = {}

    def process_message(self, message: str, user_id: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
        start_time = time.time()
        msg_lower = message.lower()
        intent = "general"
        confidence = 0.5
        response = ""
        suggestions = []
        
        # تشخیص نیت
        if any(w in msg_lower for w in ["کجا", "نزدیک", "فاصله", "موقعیت", "مکان", "آدرس", "محله", "منطقه"]):
            intent = "location_query"
            confidence = 0.85
            response = "موقعیت شما در حال بررسی است."
            suggestions = ["📍 اشتراک موقعیت"]
        elif any(w in msg_lower for w in ["سلام", "درود", "هی", "خوبی", "چطوری"]):
            intent = "greeting"
            confidence = 0.95
            response = "سلام! 🌊 من دستیار هوشمند هرمزگان هستم."
            suggestions = ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
        elif any(w in msg_lower for w in ["بیمارستان", "بیمار", "درمان", "داکتر", "پزشک"]):
            intent = "hospital"
            confidence = 0.9
            if latitude and longitude:
                response = "نزدیک‌ترین بیمارستان: بیمارستان امام خمینی - ۲.۵ کیلومتر"
                suggestions = ["📞 تماس", "🧭 مسیریابی"]
            else:
                response = "لطفاً موقعیت خود را به اشتراک بگذارید."
                suggestions = ["📍 اشتراک موقعیت"]
        elif any(w in msg_lower for w in ["رستوران", "غذا", "کباب", "شام", "ناهار"]):
            intent = "restaurant"
            confidence = 0.9
            response = "رستوران تالار خلیج - ۱.۲ کیلومتر"
            suggestions = ["🍽️ صفحه رستوران", "⭐ نظرات"]
        elif any(w in msg_lower for w in ["تاکسی", "خودرو", "رفتن", "اسنپ", "تپسی"]):
            intent = "taxi"
            confidence = 0.9
            response = "تاکسی برای شما فراخوانده شد."
            suggestions = ["⏱️ زمان", "📞 تماس"]
        else:
            response = "چطور می‌تونم کمکتون کنم؟"
            suggestions = ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
        
        return {
            "message": message,
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "suggestions": suggestions,
            "user_id": user_id,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
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
            "دانشگا": "university",
            "دانش": "university"
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


_chat_service_instance = None

def get_chat_service(db=None) -> ChatService:
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService(db)
    return _chat_service_instance
