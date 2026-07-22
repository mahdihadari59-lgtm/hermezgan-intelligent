from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import BaseModel, TimestampMixin
from app.core.security import hash_password, verify_password


class User(BaseModel, TimestampMixin):
    """مدل کاربران"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    last_login = Column(DateTime, nullable=True)
    
    chat_messages = relationship("ChatMessage", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_username_active', 'username', 'is_active'),
    )

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.pop('password_hash', None)
        return data


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired


class UserPreferences(BaseModel):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, unique=True, nullable=False, index=True)
    theme = Column(String(20), default='light', nullable=False)
    language = Column(String(10), default='fa', nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="preferences")
