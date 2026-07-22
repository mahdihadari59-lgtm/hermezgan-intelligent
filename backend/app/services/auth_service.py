from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_refresh_token,
    hash_password,
    verify_password,
    generate_verification_token,
    validate_password_strength
)
from app.core.exceptions import (
    UnauthorizedException,
    ValidationException,
    NotFoundException,
    ConflictException,
    ForbiddenException
)
from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatRepository
from app.models.user import User, RefreshToken
from app.schemas.user import UserCreate, UserLogin, TokenResponse

logger = logging.getLogger(__name__)


class AuthService:
    """سرویس احراز هویت"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.chat_repo = ChatRepository(db)

    def register(self, data: UserCreate) -> Dict[str, Any]:
        """
        ثبت‌نام کاربر جدید

        Args:
            data: اطلاعات ثبت‌نام

        Returns:
            Dict: اطلاعات کاربر و توکن‌ها

        Raises:
            ConflictException: اگر کاربر قبلاً ثبت شده باشد
            ValidationException: اگر رمز عبور ضعیف باشد
        """
        # بررسی وجود کاربر
        if self.user_repo.get_by_username(data.username):
            raise ConflictException("نام کاربری قبلاً استفاده شده است")

        if self.user_repo.get_by_email(data.email):
            raise ConflictException("ایمیل قبلاً ثبت شده است")

        if data.phone and self.user_repo.get_by_phone(data.phone):
            raise ConflictException("شماره تلفن قبلاً ثبت شده است")

        # بررسی قدرت رمز عبور
        is_valid, message = validate_password_strength(data.password)
        if not is_valid:
            raise ValidationException(message)

        # ایجاد کاربر
        user = User(
            username=data.username,
            email=data.email,
            phone=data.phone,
            full_name=data.full_name,
            password_hash=hash_password(data.password)
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # ایجاد تنظیمات پیش‌فرض
        from app.models.user import UserPreferences
        preferences = UserPreferences(user_id=user.id)
        self.db.add(preferences)
        self.db.commit()

        logger.info(f"✅ کاربر جدید ثبت شد: {user.username} (ID: {user.id})")

        # تولید توکن‌ها
        tokens = self._generate_tokens(user)

        return {
            "user": user.to_dict(),
            **tokens
        }

    def login(self, data: UserLogin) -> Dict[str, Any]:
        """
        ورود کاربر

        Args:
            data: اطلاعات ورود

        Returns:
            Dict: اطلاعات کاربر و توکن‌ها

        Raises:
            UnauthorizedException: اگر نام کاربری یا رمز عبور نادرست باشد
            ForbiddenException: اگر کاربر غیرفعال باشد
        """
        # یافتن کاربر
        user = self.user_repo.get_by_username(data.username)
        if not user:
            user = self.user_repo.get_by_email(data.username)

        if not user:
            raise UnauthorizedException("نام کاربری یا رمز عبور نادرست است")

        # بررسی رمز عبور
        if not user.verify_password(data.password):
            raise UnauthorizedException("نام کاربری یا رمز عبور نادرست است")

        # بررسی فعال بودن
        if not user.is_active:
            raise ForbiddenException("حساب کاربری غیرفعال است")

        # به‌روزرسانی آخرین ورود
        user.last_login = datetime.utcnow()
        self.db.commit()

        logger.info(f"✅ کاربر وارد شد: {user.username} (ID: {user.id})")

        # تولید توکن‌ها
        tokens = self._generate_tokens(user)

        return {
            "user": user.to_dict(),
            **tokens
        }

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        تجدید Access Token

        Args:
            refresh_token: Refresh Token

        Returns:
            Dict: توکن‌های جدید

        Raises:
            UnauthorizedException: اگر Refresh Token نامعتبر باشد
        """
        # بررسی Refresh Token
        user_id = decode_refresh_token(refresh_token)
        if not user_id:
            raise UnauthorizedException("Refresh Token نامعتبر است")

        # یافتن کاربر
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("کاربر یافت نشد")

        if not user.is_active:
            raise ForbiddenException("حساب کاربری غیرفعال است")

        # تولید توکن‌های جدید
        tokens = self._generate_tokens(user)

        logger.info(f"🔄 Refresh Token برای کاربر: {user.username}")

        return tokens

    def logout(self, refresh_token: str) -> bool:
        """
        خروج کاربر

        Args:
            refresh_token: Refresh Token

        Returns:
            bool: موفقیت عملیات
        """
        # یافتن و باطل کردن Refresh Token
        token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()

        if token:
            token.is_revoked = True
            self.db.commit()
            logger.info(f"🚪 کاربر خارج شد: {token.user_id}")
            return True

        return False

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        تغییر رمز عبور

        Args:
            user_id: شناسه کاربر
            old_password: رمز عبور فعلی
            new_password: رمز عبور جدید

        Returns:
            bool: موفقیت عملیات

        Raises:
            UnauthorizedException: اگر رمز عبور فعلی نادرست باشد
            ValidationException: اگر رمز عبور جدید ضعیف باشد
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")

        if not user.verify_password(old_password):
            raise UnauthorizedException("رمز عبور فعلی نادرست است")

        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationException(message)

        user.password_hash = hash_password(new_password)
        self.db.commit()

        logger.info(f"🔑 رمز عبور کاربر تغییر کرد: {user.username}")

        return True

    def _generate_tokens(self, user: User) -> Dict[str, Any]:
        """
        تولید توکن‌های Access و Refresh

        Args:
            user: کاربر

        Returns:
            Dict: توکن‌ها
        """
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin
        )

        refresh_token = create_refresh_token(user.id)

        # ذخیره Refresh Token
        from datetime import timedelta
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        self.db.add(refresh_token_obj)
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 دقیقه
        }

    def get_current_user(self, token: str) -> Optional[User]:
        """
        دریافت کاربر فعلی از توکن

        Args:
            token: Access Token

        Returns:
            Optional[User]: کاربر یا None
        """
        token_data = verify_token(token)
        if not token_data:
            return None

        user_id = int(token_data.get("sub"))
        return self.user_repo.get_by_id(user_id)
