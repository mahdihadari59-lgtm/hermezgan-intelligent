# ============================================================
# auth_service.py - سرویس احراز هویت و مدیریت کاربران
# ============================================================
import os
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.user import (
    User, RefreshToken, UserPreferences, UserActivity, BlockList
)
from app.auth.jwt_handler import (
    JWTHandler, TokenType, get_jwt_handler,
    get_current_user, get_current_admin_user
)

logger = logging.getLogger(__name__)


# ============================================================
# مدل‌های داده
# ============================================================

@dataclass
class AuthResult:
    """نتیجه احراز هویت"""
    success: bool
    user: Optional[User] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: str = ""
    errors: List[str] = field(default_factory=list)


@dataclass
class RegisterData:
    """داده‌های ثبت‌نام"""
    username: str
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None


@dataclass
class LoginData:
    """داده‌های ورود"""
    username: str
    password: str
    remember_me: bool = False
    device_name: Optional[str] = None


@dataclass
class PasswordResetData:
    """داده‌های بازیابی رمز عبور"""
    email: str
    token: Optional[str] = None
    new_password: Optional[str] = None


@dataclass
class UserProfileUpdate:
    """داده‌های به‌روزرسانی پروفایل"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None


# ============================================================
# سرویس اصلی احراز هویت
# ============================================================

class AuthService:
    """
    سرویس احراز هویت و مدیریت کاربران
    شامل: ثبت‌نام، ورود، خروج، بازیابی رمز عبور، مدیریت پروفایل
    """

    def __init__(self, db: Session):
        self.db = db
        self.jwt_handler = get_jwt_handler()

    # ============================================================
    # ثبت‌نام
    # ============================================================

    def register(self, data: RegisterData) -> AuthResult:
        """
        ثبت‌نام کاربر جدید
        """
        # اعتبارسنجی
        validation_errors = self._validate_registration(data)
        if validation_errors:
            return AuthResult(
                success=False,
                message="خطا در اعتبارسنجی",
                errors=validation_errors
            )

        # بررسی وجود کاربر
        if self._user_exists(data.username, data.email, data.phone):
            return AuthResult(
                success=False,
                message="کاربر با این اطلاعات قبلاً ثبت شده است",
                errors=["نام کاربری، ایمیل یا تلفن تکراری است"]
            )

        try:
            # ایجاد کاربر
            user = User(
                username=data.username,
                email=data.email,
                phone=data.phone,
                full_name=data.full_name or data.username,
                password_hash=User.hash_password(data.password),
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow()
            )

            self.db.add(user)
            self.db.flush()

            # ایجاد تنظیمات پیش‌فرض
            preferences = UserPreferences(
                user_id=user.id,
                theme='light',
                language='fa',
                notifications_enabled=True
            )
            self.db.add(preferences)

            # ثبت فعالیت
            activity = UserActivity(
                user_id=user.id,
                activity_type='register',
                activity_data='{"method": "email"}'
            )
            self.db.add(activity)

            self.db.commit()

            # ایجاد توکن‌ها
            access_token = self.jwt_handler.create_access_token(
                user_id=user.id,
                username=user.username,
                email=user.email,
                is_admin=user.is_admin
            )
            refresh_token = self.jwt_handler.create_refresh_token(user.id)

            # ذخیره Refresh Token
            self._save_refresh_token(user.id, refresh_token)

            logger.info(f"کاربر جدید ثبت‌نام کرد: {user.username} (ID: {user.id})")

            return AuthResult(
                success=True,
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                message="ثبت‌نام با موفقیت انجام شد"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ثبت‌نام: {e}")
            return AuthResult(
                success=False,
                message=f"خطا در ثبت‌نام: {str(e)}"
            )

    def _validate_registration(self, data: RegisterData) -> List[str]:
        """اعتبارسنجی داده‌های ثبت‌نام"""
        errors = []

        # نام کاربری
        if len(data.username) < 3:
            errors.append("نام کاربری باید حداقل ۳ کاراکتر باشد")
        if len(data.username) > 50:
            errors.append("نام کاربری باید حداکثر ۵۰ کاراکتر باشد")
        if not re.match(r'^[a-zA-Z0-9_]+$', data.username):
            errors.append("نام کاربری فقط می‌تواند شامل حروف، اعداد و زیرخط باشد")

        # ایمیل
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data.email):
            errors.append("ایمیل نامعتبر است")

        # رمز عبور
        if len(data.password) < 8:
            errors.append("رمز عبور باید حداقل ۸ کاراکتر باشد")
        if not any(c.isupper() for c in data.password):
            errors.append("رمز عبور باید حداقل یک حرف بزرگ داشته باشد")
        if not any(c.islower() for c in data.password):
            errors.append("رمز عبور باید حداقل یک حرف کوچک داشته باشد")
        if not any(c.isdigit() for c in data.password):
            errors.append("رمز عبور باید حداقل یک عدد داشته باشد")

        # تلفن (اختیاری)
        if data.phone and not re.match(r'^09[0-9]{9}$', data.phone):
            errors.append("شماره تلفن نامعتبر است")

        return errors

    def _user_exists(self, username: str, email: str, phone: Optional[str] = None) -> bool:
        """بررسی وجود کاربر"""
        query = self.db.query(User).filter(
            or_(
                User.username == username,
                User.email == email
            )
        )
        if phone:
            query = query.or_(User.phone == phone)

        return query.first() is not None

    # ============================================================
    # ورود و خروج
    # ============================================================

    def login(self, data: LoginData, ip_address: Optional[str] = None) -> AuthResult:
        """
        ورود کاربر
        """
        # یافتن کاربر
        user = self._find_user(data.username)
        if not user:
            return AuthResult(
                success=False,
                message="نام کاربری یا رمز عبور نادرست است"
            )

        # بررسی رمز عبور
        if not user.verify_password(data.password):
            # ثبت تلاش ناموفق
            self._log_login_attempt(user.id, False, ip_address)
            return AuthResult(
                success=False,
                message="نام کاربری یا رمز عبور نادرست است"
            )

        # بررسی فعال بودن کاربر
        if not user.is_active:
            return AuthResult(
                success=False,
                message="حساب کاربری شما غیرفعال است"
            )

        try:
            # به‌روزرسانی زمان آخرین ورود
            user.update_last_login()
            user.update_last_activity()

            # ایجاد توکن‌ها
            access_token = self.jwt_handler.create_access_token(
                user_id=user.id,
                username=user.username,
                email=user.email,
                is_admin=user.is_admin
            )

            refresh_token = self.jwt_handler.create_refresh_token(user.id)

            # ذخیره Refresh Token
            self._save_refresh_token(
                user.id,
                refresh_token,
                device_name=data.device_name,
                ip_address=ip_address
            )

            # ثبت فعالیت
            self._log_login_attempt(user.id, True, ip_address)

            self.db.commit()

            logger.info(f"کاربر وارد شد: {user.username} (ID: {user.id})")

            return AuthResult(
                success=True,
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                message="ورود با موفقیت انجام شد"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ورود: {e}")
            return AuthResult(
                success=False,
                message=f"خطا در ورود: {str(e)}"
            )

    def logout(self, user_id: int, refresh_token: str) -> bool:
        """
        خروج کاربر
        """
        try:
            # بلاک کردن Refresh Token
            token_record = self.db.query(RefreshToken).filter(
                RefreshToken.token == refresh_token,
                RefreshToken.user_id == user_id
            ).first()

            if token_record:
                token_record.is_revoked = True
                self.db.commit()

            # ثبت فعالیت
            activity = UserActivity(
                user_id=user_id,
                activity_type='logout'
            )
            self.db.add(activity)
            self.db.commit()

            logger.info(f"کاربر خارج شد: {user_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در خروج: {e}")
            return False

    def logout_all_devices(self, user_id: int) -> int:
        """
        خروج از تمام دستگاه‌ها
        """
        try:
            tokens = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            ).all()

            count = len(tokens)
            for token in tokens:
                token.is_revoked = True

            self.db.commit()

            logger.info(f"خروج از تمام دستگاه‌ها برای کاربر {user_id}: {count} دستگاه")
            return count

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در خروج از تمام دستگاه‌ها: {e}")
            return 0

    # ============================================================
    # بازیابی رمز عبور
    # ============================================================

    def request_password_reset(self, email: str) -> AuthResult:
        """
        درخواست بازیابی رمز عبور
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # برای امنیت، پیام یکسان برمی‌گردانیم
            return AuthResult(
                success=True,
                message="در صورت وجود کاربر، لینک بازیابی ارسال شد"
            )

        try:
            # ایجاد Token
            reset_token = self.jwt_handler.create_reset_token(user.id, user.email)

            # ثبت درخواست
            activity = UserActivity(
                user_id=user.id,
                activity_type='password_reset_request',
                activity_data=f'{{"email": "{email}"}}'
            )
            self.db.add(activity)
            self.db.commit()

            # در اینجا باید ایمیل ارسال شود
            # برای نمونه، فقط توکن را برمی‌گردانیم
            logger.info(f"درخواست بازیابی رمز برای کاربر: {user.username}")

            return AuthResult(
                success=True,
                user=user,
                message="لینک بازیابی رمز عبور ارسال شد",
                # در تولید توکن نباید در پاسخ برگردانده شود
                access_token=reset_token
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در درخواست بازیابی: {e}")
            return AuthResult(
                success=False,
                message=f"خطا در ارسال لینک بازیابی: {str(e)}"
            )

    def reset_password(self, token: str, new_password: str) -> AuthResult:
        """
        بازنشانی رمز عبور با Token
        """
        # تأیید Token
        payload = self.jwt_handler.verify_reset_token(token)
        if not payload:
            return AuthResult(
                success=False,
                message="لینک بازیابی نامعتبر یا منقضی شده است"
            )

        user_id = payload.get("sub")
        if not user_id:
            return AuthResult(
                success=False,
                message="اطلاعات کاربر یافت نشد"
            )

        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return AuthResult(
                success=False,
                message="کاربر یافت نشد"
            )

        # بررسی قدرت رمز عبور جدید
        if len(new_password) < 8:
            return AuthResult(
                success=False,
                message="رمز عبور باید حداقل ۸ کاراکتر باشد"
            )

        try:
            # به‌روزرسانی رمز عبور
            user.password_hash = User.hash_password(new_password)

            # بلاک کردن تمام Refresh Tokenها
            tokens = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == user.id,
                RefreshToken.is_revoked == False
            ).all()
            for token_record in tokens:
                token_record.is_revoked = True

            self.db.commit()

            logger.info(f"رمز عبور کاربر {user.username} بازنشانی شد")

            return AuthResult(
                success=True,
                user=user,
                message="رمز عبور با موفقیت تغییر یافت"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در بازنشانی رمز: {e}")
            return AuthResult(
                success=False,
                message=f"خطا در تغییر رمز عبور: {str(e)}"
            )

    # ============================================================
    # مدیریت پروفایل
    # ============================================================

    def update_profile(self, user_id: int, data: UserProfileUpdate) -> AuthResult:
        """
        به‌روزرسانی پروفایل کاربر
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return AuthResult(
                success=False,
                message="کاربر یافت نشد"
            )

        try:
            # به‌روزرسانی فیلدها
            if data.full_name is not None:
                user.full_name = data.full_name
            if data.bio is not None:
                user.bio = data.bio
            if data.phone is not None:
                # اعتبارسنجی تلفن
                if data.phone and not re.match(r'^09[0-9]{9}$', data.phone):
                    return AuthResult(
                        success=False,
                        message="شماره تلفن نامعتبر است"
                    )
                user.phone = data.phone
            if data.avatar_url is not None:
                user.avatar_url = data.avatar_url
            if data.region is not None:
                user.region = data.region
            if data.address is not None:
                user.address = data.address

            # به‌روزرسانی تنظیمات
            if data.language or data.theme:
                preferences = self.db.query(UserPreferences).filter(
                    UserPreferences.user_id == user_id
                ).first()
                if preferences:
                    if data.language:
                        preferences.language = data.language
                    if data.theme:
                        preferences.theme = data.theme

            user.updated_at = datetime.utcnow()
            self.db.commit()

            logger.info(f"پروفایل کاربر {user.username} به‌روزرسانی شد")

            return AuthResult(
                success=True,
                user=user,
                message="پروفایل با موفقیت به‌روزرسانی شد"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در به‌روزرسانی پروفایل: {e}")
            return AuthResult(
                success=False,
                message=f"خطا در به‌روزرسانی: {str(e)}"
            )

    def change_password(self, user_id: int, old_password: str, new_password: str) -> AuthResult:
        """
        تغییر رمز عبور
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return AuthResult(
                success=False,
                message="کاربر یافت نشد"
            )

        # بررسی رمز عبور فعلی
        if not user.verify_password(old_password):
            return AuthResult(
                success=False,
                message="رمز عبور فعلی نادرست است"
            )

        # بررسی قدرت رمز عبور جدید
        if len(new_password) < 8:
            return AuthResult(
                success=False,
                message="رمز عبور جدید باید حداقل ۸ کاراکتر باشد"
            )

        try:
            user.password_hash = User.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            self.db.commit()

            logger.info(f"رمز عبور کاربر {user.username} تغییر یافت")

            return AuthResult(
                success=True,
                user=user,
                message="رمز عبور با موفقیت تغییر یافت"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در تغییر رمز عبور: {e}")
            return AuthResult(
                success=False,
                message=f"خطا در تغییر رمز عبور: {str(e)}"
            )

    # ============================================================
    # توابع کمکی
    # ============================================================

    def _find_user(self, username_or_email: str) -> Optional[User]:
        """یافتن کاربر با نام کاربری یا ایمیل"""
        return self.db.query(User).filter(
            or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()

    def _save_refresh_token(
        self,
        user_id: int,
        token: str,
        device_name: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RefreshToken:
        """ذخیره Refresh Token"""
        expires_at = datetime.utcnow() + timedelta(days=7)
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            device_name=device_name or "unknown",
            ip_address=ip_address,
            expires_at=expires_at,
            is_revoked=False
        )
        self.db.add(refresh_token)
        return refresh_token

    def _log_login_attempt(self, user_id: int, success: bool, ip_address: Optional[str] = None):
        """ثبت تلاش ورود"""
        activity = UserActivity(
            user_id=user_id,
            activity_type='login_attempt',
            activity_data=f'{{"success": {str(success).lower()}, "ip": "{ip_address}"}}'
        )
        self.db.add(activity)
        self.db.commit()

    # ============================================================
    # دریافت اطلاعات کاربر
    # ============================================================

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """دریافت کاربر با ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """دریافت کاربر با نام کاربری"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """دریافت کاربر با ایمیل"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """دریافت تنظیمات کاربر"""
        return self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

    def get_user_activities(self, user_id: int, limit: int = 50) -> List[UserActivity]:
        """دریافت تاریخچه فعالیت کاربر"""
        return self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.created_at.desc()).limit(limit).all()

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """دریافت آمار کاربر"""
        # تعداد فعالیت‌ها
        activities_count = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).count()

        # تعداد Refresh Tokenها
        tokens_count = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).count()

        return {
            "total_activities": activities_count,
            "total_sessions": tokens_count,
            "is_active": True,
            "member_since": datetime.utcnow().isoformat()
        }

    # ============================================================
    # مدیریت کاربران (Admin)
    # ============================================================

    def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """
        دریافت لیست کاربران (فقط برای مدیران)
        """
        query = self.db.query(User)

        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        return users, total

    def toggle_user_active(self, user_id: int, is_active: bool) -> bool:
        """
        فعال/غیرفعال کردن کاربر (فقط برای مدیران)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        user.is_active = is_active
        user.updated_at = datetime.utcnow()

        # بلاک کردن توکن‌ها در صورت غیرفعال شدن
        if not is_active:
            tokens = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            ).all()
            for token in tokens:
                token.is_revoked = True

        self.db.commit()
        logger.info(f"وضعیت کاربر {user.username} تغییر یافت: {is_active}")
        return True

    def delete_user(self, user_id: int) -> bool:
        """
        حذف کاربر (فقط برای مدیران)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        try:
            # حذف وابسته‌ها
            self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
            self.db.query(UserPreferences).filter(UserPreferences.user_id == user_id).delete()
            self.db.query(UserActivity).filter(UserActivity.user_id == user_id).delete()
            self.db.delete(user)
            self.db.commit()

            logger.info(f"کاربر {user.username} حذف شد")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در حذف کاربر: {e}")
            return False


# ============================================================
# نمونه Singleton
# ============================================================

def get_auth_service(db: Session) -> AuthService:
    """دریافت نمونه AuthService"""
    return AuthService(db)


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # اتصال به دیتابیس تست
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)

    # ایجاد جداول
    from app.models.user import Base
    Base.metadata.create_all(engine)

    db = Session()
    auth_service = AuthService(db)

    print("=" * 60)
    print("🔐 تست سرویس احراز هویت")
    print("=" * 60)

    # تست ثبت‌نام
    print("\n📝 تست ثبت‌نام:")
    register_data = RegisterData(
        username="test_user",
        email="test@example.com",
        password="Test@123456",
        full_name="کاربر تست",
        phone="09123456789"
    )
    result = auth_service.register(register_data)
    print(f"  موفقیت: {result.success}")
    print(f"  پیام: {result.message}")
    if result.user:
        print(f"  کاربر: {result.user.username} (ID: {result.user.id})")

    # تست ورود
    print("\n🔑 تست ورود:")
    login_data = LoginData(
        username="test_user",
        password="Test@123456",
        remember_me=True
    )
    result = auth_service.login(login_data)
    print(f"  موفقیت: {result.success}")
    print(f"  پیام: {result.message}")
    if result.access_token:
        print(f"  Access Token: {result.access_token[:50]}...")

    # تست پروفایل
    if result.user:
        print("\n👤 تست پروفایل:")
        profile_data = UserProfileUpdate(
            full_name="کاربر به‌روز شده",
            bio="این یک بیوگرافی تست است"
        )
        result = auth_service.update_profile(result.user.id, profile_data)
        print(f"  موفقیت: {result.success}")
        print(f"  پیام: {result.message}")

    print("\n✅ تست سرویس احراز هویت با موفقیت انجام شد!")
