from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base
import uuid

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), index=True, nullable=True)
    title = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=True)
    intent = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    location = Column(JSON, nullable=True)
    context_data = Column(JSON, nullable=True)
    is_helpful = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    conversation = relationship("ChatConversation", back_populates="messages")

class ChatCache(Base):
    __tablename__ = "chat_cache"
    
    id = Column(Integer, primary_key=True)
    query_hash = Column(String(100), unique=True, index=True)
    response = Column(JSON, nullable=False)
    ttl = Column(Integer, default=3600)
    hits = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), index=True)
