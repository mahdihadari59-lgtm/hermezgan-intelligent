# ============================================================
# jwt_handler.py - مدیریت توکن‌های JWT
# ============================================================
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================
# تنظیمات
# ============================================================

class TokenType(Enum):
    """نوع توکن"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFY = "email_verify"


@dataclass
class JWTConfig:
    """تنظیمات JWT"""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    reset_token_expire_hours: int = 24
    verify_token_expire_hours: int = 72


# ============================================================
# کلاس اصلی مدیریت JWT
# ============================================================

class JWTHandler:
    """
    مدیریت توکن‌های JWT
    شامل: ایجاد، رمزگشایی، تأیید اعتبار
    """

    def __init__(self, config: Optional[JWTConfig] = None):
        self.config = config or JWTConfig()
        self._blacklist = set()  # کش برای توکن‌های بلاک شده

    # ============================================================
    # ایجاد توکن
    # ============================================================

    def create_access_token(
        self,
        user_id: Union[int, str],
        username: str,
        email: str,
        is_admin: bool = False,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        ایجاد Access Token
        """
        expires = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "username": username,
            "email": email,
            "is_admin": is_admin,
            "type": TokenType.ACCESS.value,
            "exp": expires,
            "iat": datetime.utcnow()
        }
        if extra_data:
            payload.update(extra_data)

        token = jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        return token

    def create_refresh_token(self, user_id: Union[int, str]) -> str:
        """
        ایجاد Refresh Token
        """
        expires = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "type": TokenType.REFRESH.value,
            "exp": expires,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

    def create_reset_token(self, user_id: Union[int, str], email: str) -> str:
        """
        ایجاد Token بازیابی رمز عبور
        """
        expires = datetime.utcnow() + timedelta(hours=self.config.reset_token_expire_hours)
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": TokenType.RESET_PASSWORD.value,
            "exp": expires,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

    def create_verify_token(self, user_id: Union[int, str], email: str) -> str:
        """
        ایجاد Token تأیید ایمیل
        """
        expires = datetime.utcnow() + timedelta(hours=self.config.verify_token_expire_hours)
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": TokenType.EMAIL_VERIFY.value,
            "exp": expires,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

    def create_oauth_token(
        self,
        user_id: Union[int, str],
        username: str,
        email: str,
        provider: str = "google",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        ایجاد توکن برای OAuth
        """
        expires = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "username": username,
            "email": email,
            "provider": provider,
            "type": TokenType.ACCESS.value,
            "exp": expires,
            "iat": datetime.utcnow()
        }
        if extra_data:
            payload.update(extra_data)

        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

    # ============================================================
    # رمزگشایی و تأیید
    # ============================================================

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        رمزگشایی توکن
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("توکن منقضی شده است")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"توکن نامعتبر: {e}")
            return None

    def verify_token(
        self,
        token: str,
        token_type: Optional[TokenType] = None,
        check_blacklist: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        تأیید اعتبار توکن
        """
        # بررسی بلاک لیست
        if check_blacklist and self.is_token_blacklisted(token):
            logger.warning("توکن در بلاک لیست است")
            return None

        payload = self.decode_token(token)
        if not payload:
            return None

        # بررسی نوع توکن
        if token_type and payload.get("type") != token_type.value:
            logger.warning(f"نوع توکن اشتباه است. مورد انتظار: {token_type.value}")
            return None

        return payload

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """تأیید Access Token"""
        return self.verify_token(token, TokenType.ACCESS)

    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """تأیید Refresh Token"""
        return self.verify_token(token, TokenType.REFRESH)

    def verify_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """تأیید Reset Token"""
        return self.verify_token(token, TokenType.RESET_PASSWORD)

    def verify_verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """تأیید Verify Token"""
        return self.verify_token(token, TokenType.EMAIL_VERIFY)

    # ============================================================
    # استخراج اطلاعات
    # ============================================================

    def get_user_id_from_token(self, token: str) -> Optional[Union[int, str]]:
        """استخراج User ID از توکن"""
        payload = self.decode_token(token)
        if payload:
            return payload.get("sub")
        return None

    def get_email_from_token(self, token: str) -> Optional[str]:
        """استخراج Email از توکن"""
        payload = self.decode_token(token)
        if payload:
            return payload.get("email")
        return None

    def get_username_from_token(self, token: str) -> Optional[str]:
        """استخراج Username از توکن"""
        payload = self.decode_token(token)
        if payload:
            return payload.get("username")
        return None

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """دریافت زمان انقضای توکن"""
        payload = self.decode_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None

    def get_token_remaining_time(self, token: str) -> Optional[int]:
        """
        دریافت زمان باقی‌مانده توکن (ثانیه)
        """
        expiry = self.get_token_expiry(token)
        if expiry:
            remaining = (expiry - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))
        return None

    # ============================================================
    # مدیریت بلاک لیست
    # ============================================================

    def blacklist_token(self, token: str) -> bool:
        """
        افزودن توکن به بلاک لیست
        """
        payload = self.decode_token(token)
        if payload:
            # کلید منحصر به فرد بر اساس JTI یا ترکیبی از داده‌ها
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self._blacklist.add(token_hash)
            logger.info(f"توکن به بلاک لیست اضافه شد: {token_hash[:10]}...")
            return True
        return False

    def is_token_blacklisted(self, token: str) -> bool:
        """بررسی وجود توکن در بلاک لیست"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash in self._blacklist

    def clear_blacklist(self):
        """پاک کردن بلاک لیست"""
        self._blacklist.clear()
        logger.info("بلاک لیست توکن‌ها پاک شد")

    # ============================================================
    # Refresh Token
    # ============================================================

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        تجدید Access Token با استفاده از Refresh Token
        """
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # در اینجا باید کاربر را از دیتابیس دریافت کرد
        # برای نمونه، اطلاعات پایه استفاده می‌شود
        new_access_token = self.create_access_token(
            user_id=user_id,
            username="user",
            email="user@example.com",
            is_admin=False
        )

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.config.access_token_expire_minutes * 60
        }

    # ============================================================
    # ابزارهای کمکی
    # ============================================================

    @staticmethod
    def generate_jti() -> str:
        """تولید JTI (JWT ID) منحصر به فرد"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_token_parts(token: str) -> Dict[str, str]:
        """
        جدا کردن بخش‌های توکن
        """
        parts = token.split('.')
        return {
            "header": parts[0] if len(parts) > 0 else "",
            "payload": parts[1] if len(parts) > 1 else "",
            "signature": parts[2] if len(parts) > 2 else ""
        }

    @staticmethod
    def is_token_format_valid(token: str) -> bool:
        """بررسی فرمت توکن"""
        parts = token.split('.')
        return len(parts) == 3 and all(parts)


# ============================================================
# نمونه Singleton
# ============================================================

_jwt_handler_instance = None


def get_jwt_handler() -> JWTHandler:
    """دریافت نمونه JWTHandler"""
    global _jwt_handler_instance
    if _jwt_handler_instance is None:
        _jwt_handler_instance = JWTHandler()
    return _jwt_handler_instance


# ============================================================
# FastAPI Dependency
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency برای دریافت کاربر فعلی از توکن
    """
    token = credentials.credentials
    jwt_handler = get_jwt_handler()
    payload = jwt_handler.verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "email": payload.get("email"),
        "is_admin": payload.get("is_admin", False)
    }


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency برای دریافت کاربر فعال
    """
    return current_user


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency برای دریافت کاربر مدیر
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی مدیر لازم است"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Dependency برای دریافت کاربر اختیاری (بدون خطا)
    """
    if not credentials:
        return None

    token = credentials.credentials
    jwt_handler = get_jwt_handler()
    payload = jwt_handler.verify_access_token(token)

    if not payload:
        return None

    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "email": payload.get("email"),
        "is_admin": payload.get("is_admin", False)
    }


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔑 تست JWT Handler")
    print("=" * 60)

    jwt_handler = get_jwt_handler()

    # تست ایجاد توکن
    print("\n📝 ایجاد توکن:")
    access_token = jwt_handler.create_access_token(
        user_id=1,
        username="test_user",
        email="test@example.com",
        is_admin=True,
        extra_data={"role": "admin"}
    )
    print(f"  Access Token: {access_token[:60]}...")

    refresh_token = jwt_handler.create_refresh_token(user_id=1)
    print(f"  Refresh Token: {refresh_token[:60]}...")

    reset_token = jwt_handler.create_reset_token(user_id=1, email="test@example.com")
    print(f"  Reset Token: {reset_token[:60]}...")

    # تست رمزگشایی
    print("\n🔓 رمزگشایی توکن:")
    decoded = jwt_handler.decode_token(access_token)
    print(f"  Decoded: {decoded}")

    # تست تأیید
    print("\n✅ تأیید توکن:")
    verified = jwt_handler.verify_access_token(access_token)
    print(f"  Verified: {verified is not None}")

    # تست استخراج اطلاعات
    print("\n📊 استخراج اطلاعات:")
    user_id = jwt_handler.get_user_id_from_token(access_token)
    email = jwt_handler.get_email_from_token(access_token)
    username = jwt_handler.get_username_from_token(access_token)
    remaining = jwt_handler.get_token_remaining_time(access_token)

    print(f"  User ID: {user_id}")
    print(f"  Email: {email}")
    print(f"  Username: {username}")
    print(f"  زمان باقی‌مانده: {remaining} ثانیه")

    # تست بلاک لیست
    print("\n🚫 تست بلاک لیست:")
    jwt_handler.blacklist_token(access_token)
    is_blacklisted = jwt_handler.is_token_blacklisted(access_token)
    print(f"  توکن بلاک شده: {is_blacklisted}")
    verified_after = jwt_handler.verify_access_token(access_token)
    print(f"  تأیید بعد از بلاک: {verified_after is None}")

    print("\n✅ تست JWT Handler با موفقیت انجام شد!")
