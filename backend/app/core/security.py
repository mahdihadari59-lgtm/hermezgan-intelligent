# ============================================================
# security.py - ماژول امنیت و احراز هویت
# ============================================================
import os
import jwt
import bcrypt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================
# تنظیمات امنیتی
# ============================================================

class TokenType(Enum):
    """نوع توکن"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFY = "verify"


@dataclass
class SecurityConfig:
    """تنظیمات امنیتی"""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_hours: int = 24
    verify_token_expire_hours: int = 72
    bcrypt_rounds: int = 12


# ============================================================
# مدیریت توکن
# ============================================================

class TokenManager:
    """مدیریت توکن‌های JWT"""

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()

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

        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

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
            "type": TokenType.RESET.value,
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
            "type": TokenType.VERIFY.value,
            "exp": expires,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)

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

    def verify_token(self, token: str, token_type: Optional[TokenType] = None) -> Optional[Dict[str, Any]]:
        """
        تأیید اعتبار توکن
        """
        payload = self.decode_token(token)
        if not payload:
            return None

        # بررسی نوع توکن
        if token_type and payload.get("type") != token_type.value:
            logger.warning(f"نوع توکن اشتباه است. مورد انتظار: {token_type.value}")
            return None

        return payload

    def get_user_id_from_token(self, token: str) -> Optional[Union[int, str]]:
        """
        استخراج User ID از توکن
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        تجدید Access Token با استفاده از Refresh Token
        """
        payload = self.verify_token(refresh_token, TokenType.REFRESH)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # در اینجا باید کاربر را از دیتابیس دریافت کرد
        # برای نمونه، اطلاعات پایه استفاده می‌شود
        return self.create_access_token(
            user_id=user_id,
            username="user",
            email="user@example.com",
            is_admin=False
        )


# ============================================================
# مدیریت رمز عبور
# ============================================================

class PasswordManager:
    """مدیریت رمز عبور با bcrypt"""

    def __init__(self, rounds: int = 12):
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        """
        رمزنگاری رمز عبور
        """
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        بررسی رمز عبور
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"خطا در بررسی رمز عبور: {e}")
            return False

    def is_password_strong(self, password: str) -> Dict[str, Any]:
        """
        بررسی قدرت رمز عبور
        """
        result = {
            "is_strong": True,
            "issues": [],
            "strength": "weak"
        }

        # حداقل طول
        if len(password) < 8:
            result["is_strong"] = False
            result["issues"].append("حداقل ۸ کاراکتر")

        # شامل حرف بزرگ
        if not any(c.isupper() for c in password):
            result["is_strong"] = False
            result["issues"].append("حداقل یک حرف بزرگ")

        # شامل حرف کوچک
        if not any(c.islower() for c in password):
            result["is_strong"] = False
            result["issues"].append("حداقل یک حرف کوچک")

        # شامل عدد
        if not any(c.isdigit() for c in password):
            result["is_strong"] = False
            result["issues"].append("حداقل یک عدد")

        # شامل کاراکتر خاص
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            result["is_strong"] = False
            result["issues"].append("حداقل یک کاراکتر خاص")

        # محاسبه قدرت
        if result["is_strong"]:
            if len(password) >= 12:
                result["strength"] = "strong"
            else:
                result["strength"] = "medium"
        else:
            result["strength"] = "weak"

        return result


# ============================================================
# مدیریت Session
# ============================================================

class SessionManager:
    """مدیریت نشست‌های کاربر"""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._cleanup_interval = 3600  # ۱ ساعت

    def create_session(self, user_id: Union[int, str], data: Optional[Dict[str, Any]] = None) -> str:
        """
        ایجاد نشست جدید
        """
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = {
            "user_id": str(user_id),
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "data": data or {},
            "is_active": True
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات نشست
        """
        session = self._sessions.get(session_id)
        if session and session.get("is_active"):
            session["last_activity"] = datetime.utcnow()
            return session
        return None

    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        به‌روزرسانی نشست
        """
        session = self._sessions.get(session_id)
        if session and session.get("is_active"):
            session["data"].update(data)
            session["last_activity"] = datetime.utcnow()
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        حذف نشست
        """
        if session_id in self._sessions:
            self._sessions[session_id]["is_active"] = False
            return True
        return False

    def clear_expired_sessions(self, max_age_hours: int = 24):
        """
        پاک کردن نشست‌های منقضی
        """
        now = datetime.utcnow()
        expired = []
        for session_id, session in self._sessions.items():
            age = (now - session["created_at"]).total_seconds() / 3600
            if age > max_age_hours or not session.get("is_active"):
                expired.append(session_id)

        for session_id in expired:
            del self._sessions[session_id]

        return len(expired)


# ============================================================
# ابزارهای امنیتی
# ============================================================

class SecurityUtils:
    """ابزارهای کمکی امنیتی"""

    @staticmethod
    def generate_csrf_token() -> str:
        """تولید CSRF Token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_api_key() -> str:
        """تولید API Key"""
        return f"hk_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_data(data: str, salt: Optional[str] = None) -> str:
        """هش کردن داده"""
        if salt:
            return hashlib.sha256((data + salt).encode()).hexdigest()
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def validate_email(email: str) -> bool:
        """اعتبارسنجی ایمیل"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """اعتبارسنجی شماره تلفن ایران"""
        import re
        pattern = r'^09[0-9]{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def sanitize_input(text: str) -> str:
        """پالایش ورودی برای جلوگیری از XSS"""
        import html
        return html.escape(text.strip())

    @staticmethod
    def is_rate_limited(key: str, limit: int = 100, window_seconds: int = 60) -> bool:
        """
        بررسی محدودیت نرخ درخواست
        پیاده‌سازی ساده - در تولید از Redis استفاده کنید
        """
        import time
        from collections import defaultdict

        if not hasattr(SecurityUtils, '_rate_limiter'):
            SecurityUtils._rate_limiter = defaultdict(list)

        now = time.time()
        window_start = now - window_seconds

        # پاک کردن درخواست‌های قدیمی
        requests = SecurityUtils._rate_limiter[key]
        requests = [t for t in requests if t > window_start]
        SecurityUtils._rate_limiter[key] = requests

        if len(requests) >= limit:
            return True

        requests.append(now)
        return False


# ============================================================
# نمونه‌های Singleton
# ============================================================

_token_manager = None
_password_manager = None
_session_manager = None


def get_token_manager() -> TokenManager:
    """دریافت نمونه TokenManager"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager


def get_password_manager() -> PasswordManager:
    """دریافت نمونه PasswordManager"""
    global _password_manager
    if _password_manager is None:
        _password_manager = PasswordManager()
    return _password_manager


def get_session_manager() -> SessionManager:
    """دریافت نمونه SessionManager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# ============================================================
# Dependency برای FastAPI
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency برای دریافت کاربر فعلی
    """
    token = credentials.credentials
    token_manager = get_token_manager()
    payload = token_manager.verify_token(token, TokenType.ACCESS)

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
    # در اینجا می‌توانید بررسی کنید که کاربر فعال است یا خیر
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


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔐 تست ماژول امنیت")
    print("=" * 60)

    # تست Token Manager
    token_manager = get_token_manager()
    print("\n🔑 تست توکن:")
    access_token = token_manager.create_access_token(
        user_id=1,
        username="test_user",
        email="test@example.com",
        is_admin=True
    )
    print(f"  Access Token: {access_token[:50]}...")

    refresh_token = token_manager.create_refresh_token(user_id=1)
    print(f"  Refresh Token: {refresh_token[:50]}...")

    # تست رمزگشایی
    decoded = token_manager.decode_token(access_token)
    print(f"  Decoded: {decoded}")

    # تست Password Manager
    password_manager = get_password_manager()
    print("\n🔒 تست رمز عبور:")
    password = "Test@123456"
    hashed = password_manager.hash_password(password)
    print(f"  رمز عبور: {password}")
    print(f"  هش شده: {hashed}")
    print(f"  بررسی: {password_manager.verify_password(password, hashed)}")

    # تست قدرت رمز عبور
    strength = password_manager.is_password_strong(password)
    print(f"  قدرت رمز: {strength}")

    # تست Session Manager
    session_manager = get_session_manager()
    print("\n📋 تست نشست:")
    session_id = session_manager.create_session(1, {"name": "Test User"})
    print(f"  Session ID: {session_id}")
    session = session_manager.get_session(session_id)
    print(f"  Session Data: {session}")

    # تست ابزارها
    print("\n🛠️ تست ابزارها:")
    csrf = SecurityUtils.generate_csrf_token()
    print(f"  CSRF Token: {csrf}")
    api_key = SecurityUtils.generate_api_key()
    print(f"  API Key: {api_key}")
    sanitized = SecurityUtils.sanitize_input("<script>alert('xss')</script>")
    print(f"  Sanitized: {sanitized}")

    print("\n✅ تست امنیت با موفقیت انجام شد!")
