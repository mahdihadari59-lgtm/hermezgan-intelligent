from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

from app.core.exceptions import NotFoundException, ConflictError, ValidationError
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """سرویس مدیریت کاربران"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user(self, user_id: int) -> Optional[User]:
        """دریافت کاربر"""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """دریافت کاربر بر اساس نام کاربری"""
        return self.user_repo.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """دریافت کاربر بر اساس ایمیل"""
        return self.user_repo.get_by_email(email)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """دریافت لیست کاربران"""
        return self.user_repo.get_all(skip, limit)

    def update_user(self, user_id: int, data: UserUpdate) -> Optional[User]:
        """به‌روزرسانی کاربر"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")

        # بررسی تکراری بودن
        if data.username and data.username != user.username:
            if self.user_repo.get_by_username(data.username):
                raise ConflictError("نام کاربری قبلاً استفاده شده است")

        if data.email and data.email != user.email:
            if self.user_repo.get_by_email(data.email):
                raise ConflictError("ایمیل قبلاً ثبت شده است")

        if data.phone and data.phone != user.phone:
            if self.user_repo.get_by_phone(data.phone):
                raise ConflictError("شماره تلفن قبلاً ثبت شده است")

        return self.user_repo.update(user_id, **data.dict(exclude_unset=True))

    def delete_user(self, user_id: int) -> bool:
        """حذف کاربر (نرم)"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")

        user.is_active = False
        self.db.commit()
        logger.info(f"🗑️ کاربر حذف شد: {user.username} (ID: {user_id})")
        return True

    def activate_user(self, user_id: int) -> bool:
        """فعال کردن کاربر"""
        user = self.user_repo.activate_user(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")
        logger.info(f"✅ کاربر فعال شد: {user.username}")
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """غیرفعال کردن کاربر"""
        user = self.user_repo.deactivate_user(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")
        logger.info(f"⛔ کاربر غیرفعال شد: {user.username}")
        return True

    def search_users(self, query: str, limit: int = 20) -> List[User]:
        """جستجوی کاربران"""
        return self.user_repo.search_users(query, limit)

    def get_user_stats(self) -> Dict[str, Any]:
        """آمار کاربران"""
        return self.user_repo.get_user_stats()

    def update_location(self, user_id: int, latitude: float, longitude: float) -> Optional[User]:
        """به‌روزرسانی موقعیت کاربر"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")

        user.latitude = latitude
        user.longitude = longitude
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """دریافت تنظیمات کاربر"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")

        if not user.preferences:
            return {}

        return {
            "theme": user.preferences.theme,
            "language": user.preferences.language,
            "notifications_enabled": user.preferences.notifications_enabled,
            "email_notifications": user.preferences.email_notifications,
            "push_notifications": user.preferences.push_notifications,
            "sms_notifications": user.preferences.sms_notifications
        }

    def update_user_preferences(self, user_id: int, preferences: Dict) -> Dict:
        """به‌روزرسانی تنظیمات کاربر"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")

        if not user.preferences:
            from app.models.user import UserPreferences
            user.preferences = UserPreferences(user_id=user.id)

        for key, value in preferences.items():
            if hasattr(user.preferences, key):
                setattr(user.preferences, key, value)

        self.db.commit()
        self.db.refresh(user.preferences)

        return self.get_user_preferences(user_id)
