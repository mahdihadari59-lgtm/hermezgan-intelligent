# ============================================================
# user.py - مدل کاربران و احراز هویت
# ============================================================
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt
import jwt
import os
from typing import Optional, Dict, Any

Base = declarative_base()


# ============================================================
# مدل کاربر
# ============================================================

class User(Base):
    """
    جدول کاربران سیستم
    """
    __tablename__ = "users"

    # اطلاعات اصلی
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # اطلاعات پروفایل
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    birth_date = Column(DateTime, nullable=True)

    # وضعیت کاربر
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # موقعیت مکانی
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)

    # اطلاعات زمانی
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)

    # تنظیمات
    language = Column(String(10), default='fa')
    theme = Column(String(20), default='light')
    notifications_enabled = Column(Boolean, default=True)

    # روابط
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    user_preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_email_phone', 'email', 'phone'),
        Index('idx_user_region', 'region'),
        Index('idx_user_active', 'is_active'),
    )

    def verify_password(self, password: str) -> bool:
        """بررسی صحت رمز عبور"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        """رمزنگاری رمز عبور با bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def update_last_login(self):
        """به‌روزرسانی زمان آخرین ورود"""
        self.last_login = datetime.utcnow()

    def update_last_activity(self):
        """به‌روزرسانی زمان آخرین فعالیت"""
        self.last_activity = datetime.utcnow()

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        تبدیل مدل به دیکشنری
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "region": self.region,
            "address": self.address,
            "language": self.language,
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data["password_hash"] = self.password_hash

        return data

    def to_public_dict(self) -> Dict[str, Any]:
        """
        تبدیل به دیکشنری عمومی (بدون اطلاعات حساس)
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "region": self.region,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
        }


# ============================================================
# مدل Refresh Token
# ============================================================

class RefreshToken(Base):
    """
    جدول ذخیره Refresh Tokenها
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    token = Column(String(500), unique=True, index=True, nullable=False)
    device_name = Column(String(100), nullable=True)
    device_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)

    # روابط
    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index('idx_refresh_token_user', 'user_id', 'is_revoked'),
        Index('idx_refresh_token_expires', 'expires_at'),
    )

    def is_expired(self) -> bool:
        """بررسی منقضی شدن توکن"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """بررسی اعتبار توکن"""
        return not self.is_revoked and not self.is_expired()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "token": self.token,
            "device_name": self.device_name,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_revoked": self.is_revoked,
        }


# ============================================================
# مدل تنظیمات کاربر
# ============================================================

class UserPreferences(Base):
    """
    جدول تنظیمات کاربر
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)

    # تنظیمات ظاهری
    theme = Column(String(20), default='light')  # light, dark, system
    language = Column(String(10), default='fa')  # fa, en, ar

    # تنظیمات اعلانات
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)

    # تنظیمات حریم خصوصی
    show_email = Column(Boolean, default=False)
    show_phone = Column(Boolean, default=False)
    show_location = Column(Boolean, default=True)

    # تنظیمات پیشرفته
    chat_tts_enabled = Column(Boolean, default=True)
    chat_stt_enabled = Column(Boolean, default=True)
    map_satellite_view = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    user = relationship("User", back_populates="user_preferences")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theme": self.theme,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "sms_notifications": self.sms_notifications,
            "show_email": self.show_email,
            "show_phone": self.show_phone,
            "show_location": self.show_location,
            "chat_tts_enabled": self.chat_tts_enabled,
            "chat_stt_enabled": self.chat_stt_enabled,
            "map_satellite_view": self.map_satellite_view,
        }


# ============================================================
# مدل تاریخچه فعالیت
# ============================================================

class UserActivity(Base):
    """
    جدول تاریخچه فعالیت کاربران
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    activity_type = Column(String(50), index=True, nullable=False)  # login, logout, search, chat, map, etc.
    activity_data = Column(Text, nullable=True)  # JSON داده‌های فعالیت
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=True)  # مدت زمان به ثانیه

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_activity_user_type', 'user_id', 'activity_type'),
        Index('idx_activity_created', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "activity_data": self.activity_data,
            "ip_address": self.ip_address,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# مدل بلاک‌لیست (IP یا کاربر)
# ============================================================

class BlockList(Base):
    """
    جدول بلاک‌لیست IP و کاربران
    """
    __tablename__ = "block_list"

    id = Column(Integer, primary_key=True, index=True)
    block_type = Column(String(20), nullable=False)  # ip, user, email, phone
    block_value = Column(String(255), nullable=False, index=True)
    reason = Column(Text, nullable=True)
    blocked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index('idx_block_type_value', 'block_type', 'block_value'),
        Index('idx_block_active', 'is_active'),
    )

    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired()


# ============================================================
# توابع کمکی
# ============================================================

def create_user(
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    is_admin: bool = False
) -> User:
    """
    ایجاد کاربر جدید
    """
    user = User(
        username=username,
        email=email,
        full_name=full_name or username,
        phone=phone,
        password_hash=User.hash_password(password),
        is_admin=is_admin,
        is_active=True,
        created_at=datetime.utcnow()
    )
    return user


def get_user_by_email(db_session, email: str) -> Optional[User]:
    """دریافت کاربر بر اساس ایمیل"""
    return db_session.query(User).filter(User.email == email).first()


def get_user_by_username(db_session, username: str) -> Optional[User]:
    """دریافت کاربر بر اساس نام کاربری"""
    return db_session.query(User).filter(User.username == username).first()


def get_user_by_phone(db_session, phone: str) -> Optional[User]:
    """دریافت کاربر بر اساس شماره تلفن"""
    return db_session.query(User).filter(User.phone == phone).first()


def authenticate_user(db_session, username: str, password: str) -> Optional[User]:
    """
    احراز هویت کاربر
    """
    user = get_user_by_username(db_session, username) or get_user_by_email(db_session, username)
    if user and user.verify_password(password):
        return user
    return None


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("👤 تست مدل کاربر")
    print("=" * 60)

    # تست ایجاد کاربر
    user = create_user(
        username="test_user",
        email="test@example.com",
        password="Test@123456",
        full_name="کاربر تست",
        phone="09123456789"
    )

    print(f"\n📝 کاربر ایجاد شد:")
    print(f"  ID: {user.id}")
    print(f"  نام کاربری: {user.username}")
    print(f"  ایمیل: {user.email}")
    print(f"  نام کامل: {user.full_name}")
    print(f"  تلفن: {user.phone}")
    print(f"  مدیر: {user.is_admin}")

    # تست رمز عبور
    print(f"\n🔐 تست رمز عبور:")
    print(f"  رمز عبور صحیح: {user.verify_password('Test@123456')}")
    print(f"  رمز عبور اشتباه: {user.verify_password('wrong')}")

    # تست تبدیل به دیکشنری
    print(f"\n📊 تبدیل به دیکشنری:")
    print(f"  Public: {user.to_public_dict()}")
    print(f"  Full: {user.to_dict(include_sensitive=True)}")

    print("\n✅ تست مدل کاربر با موفقیت انجام شد!")
