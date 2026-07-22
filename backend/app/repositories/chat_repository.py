from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from app.models.chat import ChatConversation, ChatMessage, ChatIntent, ChatEntity, ChatCache
from app.repositories.base_repository import BaseRepository


class ChatRepository:
    """Repository برای مدیریت چت‌ها"""

    def __init__(self, db: Session):
        self.db = db
        self.conversation_repo = BaseRepository(ChatConversation, db)
        self.message_repo = BaseRepository(ChatMessage, db)

    # ========== Conversation ==========

    def get_conversation_by_session(self, session_id: str) -> Optional[ChatConversation]:
        """دریافت مکالمه بر اساس Session ID"""
        return self.db.query(ChatConversation).filter(
            ChatConversation.session_id == session_id
        ).first()

    def get_conversations_by_user(self, user_id: str, limit: int = 50) -> List[ChatConversation]:
        """دریافت مکالمات کاربر"""
        return self.db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).order_by(desc(ChatConversation.created_at)).limit(limit).all()

    def create_conversation(self, user_id: str, session_id: str, **kwargs) -> ChatConversation:
        """ایجاد مکالمه جدید"""
        return self.conversation_repo.create(
            user_id=user_id,
            session_id=session_id,
            **kwargs
        )

    def update_conversation(self, conversation_id: int, **kwargs) -> Optional[ChatConversation]:
        """به‌روزرسانی مکالمه"""
        return self.conversation_repo.update(conversation_id, **kwargs)

    # ========== Messages ==========

    def get_messages_by_conversation(self, conversation_id: int, limit: int = 50) -> List[ChatMessage]:
        """دریافت پیام‌های یک مکالمه"""
        return self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit).all()

    def get_messages_by_user(self, user_id: str, limit: int = 100) -> List[ChatMessage]:
        """دریافت پیام‌های کاربر"""
        return self.db.query(ChatMessage).join(
            ChatConversation
        ).filter(
            ChatConversation.user_id == user_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit).all()

    def create_message(self, conversation_id: int, user_message: str, bot_response: str, **kwargs) -> ChatMessage:
        """ایجاد پیام جدید"""
        return self.message_repo.create(
            conversation_id=conversation_id,
            user_message=user_message,
            bot_response=bot_response,
            **kwargs
        )

    def rate_message(self, message_id: int, helpful: bool) -> Optional[ChatMessage]:
        """ثبت امتیاز مفید بودن پیام"""
        return self.message_repo.update(message_id, is_helpful=1 if helpful else -1)

    def get_message_stats(self, conversation_id: int) -> dict:
        """آمار پیام‌های یک مکالمه"""
        total = self.db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.conversation_id == conversation_id
        ).scalar() or 0

        avg_time = self.db.query(
            func.avg(ChatMessage.processing_time)
        ).filter(
            ChatMessage.conversation_id == conversation_id
        ).scalar() or 0

        return {
            "total_messages": total,
            "avg_processing_time": round(avg_time, 3),
            "user_messages": self.db.query(func.count(ChatMessage.id)).filter(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.user_message.isnot(None)
            ).scalar() or 0,
            "bot_messages": self.db.query(func.count(ChatMessage.id)).filter(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.bot_response.isnot(None)
            ).scalar() or 0
        }

    # ========== Intent & Entities ==========

    def get_all_intents(self) -> List[ChatIntent]:
        """دریافت تمام نیت‌ها"""
        return self.db.query(ChatIntent).all()

    def get_intent_by_name(self, name: str) -> Optional[ChatIntent]:
        """دریافت نیت بر اساس نام"""
        return self.db.query(ChatIntent).filter(ChatIntent.name == name).first()

    def create_intent(self, name: str, keywords: List[str], response_template: str, **kwargs) -> ChatIntent:
        """ایجاد نیت جدید"""
        intent = ChatIntent(
            name=name,
            keywords=keywords,
            response_template=response_template,
            **kwargs
        )
        self.db.add(intent)
        self.db.commit()
        self.db.refresh(intent)
        return intent

    def get_entity_by_name(self, name: str) -> Optional[ChatEntity]:
        """دریافت موجودیت بر اساس نام"""
        return self.db.query(ChatEntity).filter(ChatEntity.name == name).first()

    def create_entity(self, name: str, entity_type: str, synonyms: List[str], **kwargs) -> ChatEntity:
        """ایجاد موجودیت جدید"""
        entity = ChatEntity(
            name=name,
            entity_type=entity_type,
            synonyms=synonyms,
            **kwargs
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    # ========== Cache ==========

    def get_cached_response(self, query_hash: str) -> Optional[ChatCache]:
        """دریافت پاسخ کش شده"""
        from datetime import datetime
        return self.db.query(ChatCache).filter(
            ChatCache.query_hash == query_hash,
            ChatCache.expires_at > datetime.utcnow()
        ).first()

    def create_cache(self, query_hash: str, response: Dict, ttl: int = 3600) -> ChatCache:
        """ذخیره پاسخ در کش"""
        from datetime import datetime, timedelta
        cache = ChatCache(
            query_hash=query_hash,
            response=response,
            ttl=ttl,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl)
        )
        self.db.add(cache)
        self.db.commit()
        self.db.refresh(cache)
        return cache

    def increment_cache_hits(self, cache_id: int) -> Optional[ChatCache]:
        """افزایش تعداد بازدید کش"""
        cache = self.db.query(ChatCache).filter(ChatCache.id == cache_id).first()
        if cache:
            cache.hits += 1
            self.db.commit()
            self.db.refresh(cache)
        return cache

    def clean_expired_cache(self) -> int:
        """پاکسازی کش‌های منقضی شده"""
        from datetime import datetime
        deleted = self.db.query(ChatCache).filter(
            ChatCache.expires_at < datetime.utcnow()
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def get_chat_stats(self) -> dict:
        """آمار کلی چت‌بات"""
        total_messages = self.db.query(func.count(ChatMessage.id)).scalar() or 0
        avg_processing_time = self.db.query(
            func.avg(ChatMessage.processing_time)
        ).scalar() or 0

        intents = self.db.query(
            ChatMessage.intent,
            func.count(ChatMessage.id).label('count')
        ).group_by(ChatMessage.intent).all()

        helpful_count = self.db.query(
            func.count(ChatMessage.id)
        ).filter(ChatMessage.is_helpful == 1).scalar() or 0

        return {
            "total_messages": total_messages,
            "avg_processing_time": round(avg_processing_time, 3),
            "intents": [
                {"intent": i[0], "count": i[1]} for i in intents
            ],
            "helpful_rate": round(helpful_count / total_messages * 100, 1) if total_messages > 0 else 0
        }
