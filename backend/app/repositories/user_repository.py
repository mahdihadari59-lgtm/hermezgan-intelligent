from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository برای مدیریت کاربران"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        """دریافت کاربر بر اساس نام کاربری"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """دریافت کاربر بر اساس ایمیل"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        """دریافت کاربر بر اساس شماره تلفن"""
        return self.db.query(User).filter(User.phone == phone).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """دریافت کاربران فعال"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def get_admin_users(self) -> List[User]:
        """دریافت کاربران ادمین"""
        return self.db.query(User).filter(User.is_admin == True).all()

    def update_last_login(self, user_id: int) -> Optional[User]:
        """به‌روزرسانی زمان آخرین ورود"""
        from datetime import datetime
        return self.update(user_id, last_login=datetime.utcnow())

    def verify_user(self, user_id: int) -> Optional[User]:
        """تأیید کاربر"""
        return self.update(user_id, is_verified=True)

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """غیرفعال کردن کاربر"""
        return self.update(user_id, is_active=False)

    def activate_user(self, user_id: int) -> Optional[User]:
        """فعال کردن کاربر"""
        return self.update(user_id, is_active=True)

    def search_users(self, query: str, limit: int = 20) -> List[User]:
        """جستجوی کاربران"""
        return self.db.query(User).filter(
            (User.username.ilike(f"%{query}%")) |
            (User.full_name.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%"))
        ).limit(limit).all()

    def get_user_stats(self) -> dict:
        """آمار کاربران"""
        from sqlalchemy import func
        total = self.db.query(func.count(User.id)).scalar() or 0
        active = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        verified = self.db.query(func.count(User.id)).filter(User.is_verified == True).scalar() or 0
        admin = self.db.query(func.count(User.id)).filter(User.is_admin == True).scalar() or 0

        return {
            "total": total,
            "active": active,
            "verified": verified,
            "admin": admin,
            "inactive": total - active,
            "unverified": total - verified
        }
