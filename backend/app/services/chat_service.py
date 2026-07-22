import time
import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.chat import ChatConversation, ChatMessage, ChatCache

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.CACHE_TTL = 3600
    
    def _generate_cache_key(self, message: str, latitude: float, longitude: float) -> str:
        key_str = f"{message}:{latitude}:{longitude}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, message: str, latitude: float, longitude: float) -> Optional[Dict]:
        cache_key = self._generate_cache_key(message, latitude, longitude)
        
        db_cache = self.db.query(ChatCache).filter(
            ChatCache.query_hash == cache_key,
            ChatCache.expires_at > datetime.utcnow()
        ).first()
        
        if db_cache:
            db_cache.hits += 1
            self.db.commit()
            return db_cache.response
        
        return None
    
    def _set_cache(self, message: str, latitude: float, longitude: float, response: Dict):
        cache_key = self._generate_cache_key(message, latitude, longitude)
        expires_at = datetime.utcnow() + timedelta(seconds=self.CACHE_TTL)
        
        db_cache = ChatCache(
            query_hash=cache_key,
            response=response,
            expires_at=expires_at
        )
        self.db.add(db_cache)
        self.db.commit()
    
    def _detect_intent(self, message: str) -> tuple:
        intents = {
            'hospital': ['بیمارستان', 'بیمار', 'درمان', 'داکتر', 'پزشک'],
            'restaurant': ['رستوران', 'غذا', 'کباب', 'شام', 'نهار'],
            'taxi': ['تاکسی', 'خودرو', 'رفتن', 'حمل', 'مسافر'],
            'location': ['کجا', 'نزدیک', 'فاصله', 'موقعیت', 'مکان'],
        }
        
        for intent, keywords in intents.items():
            if any(k in message for k in keywords):
                return intent, 0.9
        
        return 'general', 0.5
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> Dict:
        start_time = time.time()
        
        cached = self._get_from_cache(message, latitude or 0, longitude or 0)
        if cached:
            cached['from_cache'] = True
            return cached
        
        conversation = None
        if session_id:
            conversation = self.db.query(ChatConversation).filter(
                ChatConversation.session_id == session_id
            ).first()
        
        if not conversation:
            conversation = ChatConversation(
                user_id=user_id,
                session_id=session_id or f"{user_id}_{int(time.time())}",
                latitude=latitude,
                longitude=longitude,
            )
            self.db.add(conversation)
            self.db.commit()
        
        intent, confidence = self._detect_intent(message)
        bot_response = self._generate_response(intent, message, latitude, longitude)
        
        processing_time = time.time() - start_time
        chat_message = ChatMessage(
            conversation_id=conversation.id,
            user_message=message,
            bot_response=bot_response['response'],
            intent=intent,
            confidence=confidence,
            processing_time=processing_time,
            location={"lat": latitude, "lng": longitude} if latitude and longitude else None,
        )
        self.db.add(chat_message)
        self.db.commit()
        
        response = {
            "response": bot_response['response'],
            "intent": intent,
            "confidence": confidence,
            "suggestions": bot_response.get('suggestions', []),
            "processing_time": processing_time,
            "from_cache": False,
            "message_id": chat_message.id,
        }
        
        self._set_cache(message, latitude or 0, longitude or 0, response)
        
        return response
    
    def _generate_response(self, intent: str, message: str, latitude: Optional[float], longitude: Optional[float]) -> Dict:
        responses = {
            'hospital': {
                'response': '🏥 نزدیک‌ترین بیمارستان: بیمارستان امام خمینی در فاصله ۲.۵ کیلومتری',
                'suggestions': ['📞 تماس', '🧭 مسیریابی', '🔄 بیمارستان دیگر']
            },
            'restaurant': {
                'response': '🍽️ رستوران تالار خلیج با امتیاز ۴.۵ در فاصله ۱.۲ کیلومتری',
                'suggestions': ['⭐ نظرات', '📞 رزرو', '🍴 منو']
            },
            'taxi': {
                'response': '🚗 تاکسی برای شما فراخوانده شد. حدود ۳ دقیقه دیگر می‌رسد.',
                'suggestions': ['⏱️ پیگیری', '📞 تماس راننده', '❌ لغو']
            },
            'location': {
                'response': f'📍 موقعیت شما: عرض {latitude or "نامشخص"}، طول {longitude or "نامشخص"}',
                'suggestions': ['🏥 خدمات نزدیک', '🍽️ رستوران‌ها', '🗺️ نقشه']
            },
            'general': {
                'response': '🌊 چطور می‌تونم کمکتون کنم؟ می‌تونم اطلاعات خدمات، بیمارستان‌ها یا رستوران‌ها رو براتون جستجو کنم.',
                'suggestions': ['🏥 بیمارستان', '🍽️ رستوران', '🚗 تاکسی', '📍 موقعیت']
            }
        }
        
        return responses.get(intent, responses['general'])
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        conversation = self.db.query(ChatConversation).filter(
            ChatConversation.session_id == session_id
        ).first()
        
        if not conversation:
            return []
        
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation.id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        
        return [{
            "id": msg.id,
            "user": msg.user_message,
            "bot": msg.bot_response,
            "intent": msg.intent,
            "confidence": msg.confidence,
            "processing_time": msg.processing_time,
            "timestamp": msg.created_at.isoformat()
        } for msg in reversed(messages)]
    
    def rate_response(self, message_id: int, helpful: bool) -> bool:
        message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if message:
            message.is_helpful = 1 if helpful else -1
            self.db.commit()
            return True
        return False
