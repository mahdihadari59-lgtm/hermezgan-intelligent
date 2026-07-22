from pydantic_settings import BaseSettings
from pydantic import Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    تنظیمات اصلی برنامه
    تمام مقادیر از متغیرهای محیطی خوانده می‌شوند
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ============================================================
    # General
    # ============================================================
    APP_NAME: str = Field(default="هرمزگان هوشمند", description="نام برنامه")
    APP_VERSION: str = Field(default="1.0.0", description="نسخه برنامه")
    APP_DESCRIPTION: str = Field(
        default="سیستم دانش‌گراف هوشمند استان هرمزگان",
        description="توضیحات برنامه"
    )
    ENVIRONMENT: str = Field(default="development", description="محیط اجرا")
    DEBUG: bool = Field(default=True, description="حالت Debug")

    # ============================================================
    # API
    # ============================================================
    API_HOST: str = Field(default="0.0.0.0", description="آدرس میزبانی API")
    API_PORT: int = Field(default=8000, description="پورت API")
    API_PREFIX: str = Field(default="/api/v1", description="پیشوند مسیر API")
    WORKERS: int = Field(default=1, description="تعداد Worker")

    # ============================================================
    # Database
    # ============================================================
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/hermezgan_db",
        description="آدرس اتصال دیتابیس"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="حداکثر اتصالات همزمان")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="اتصالات اضافی")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="زمان انتظار برای اتصال")
    DATABASE_ECHO: bool = Field(default=False, description="نمایش کوئری‌ها در لاگ")

    # ============================================================
    # Redis
    # ============================================================
    REDIS_URL: str = Field(default="redis://localhost:6379", description="آدرس اتصال Redis")
    REDIS_DB: int = Field(default=0, description="شماره دیتابیس Redis")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="رمز عبور Redis")
    REDIS_SSL: bool = Field(default=False, description="استفاده از SSL برای Redis")

    # ============================================================
    # Security
    # ============================================================
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        description="کلید امنیتی JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="الگوریتم رمزنگاری")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="زمان انقضای Access Token")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="زمان انقضای Refresh Token")
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="حداقل طول رمز عبور")
    PASSWORD_MAX_LENGTH: int = Field(default=50, description="حداکثر طول رمز عبور")

    # ============================================================
    # CORS
    # ============================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5000"],
        description="دامنه‌های مجاز CORS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="اجازه ارسال Credentials")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], description="متدهای مجاز")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], description="هدرهای مجاز")
    CORS_EXPOSE_HEADERS: List[str] = Field(
        default=["X-Request-ID", "X-Process-Time"],
        description="هدرهای نمایش داده شده"
    )
    CORS_MAX_AGE: int = Field(default=600, description="حداکثر عمر کش CORS")

    # ============================================================
    # Rate Limit
    # ============================================================
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="حداکثر درخواست در دقیقه")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="حداکثر درخواست در ساعت")
    RATE_LIMIT_PER_DAY: int = Field(default=10000, description="حداکثر درخواست در روز")
    USE_REDIS_RATE_LIMIT: bool = Field(default=True, description="استفاده از Redis برای Rate Limit")

    # ============================================================
    # Logging
    # ============================================================
    LOG_LEVEL: str = Field(default="INFO", description="سطح لاگ")
    LOG_FORMAT: str = Field(default="json", description="فرمت لاگ")
    LOG_BODY: bool = Field(default=False, description="لاگ کردن Body درخواست‌ها")
    LOG_FILE: Optional[str] = Field(default=None, description="مسیر فایل لاگ")
    LOG_MAX_SIZE: int = Field(default=10 * 1024 * 1024, description="حداکثر حجم فایل لاگ")
    LOG_BACKUP_COUNT: int = Field(default=5, description="تعداد فایل‌های بکاپ لاگ")

    # ============================================================
    # Upload
    # ============================================================
    UPLOAD_DIR: str = Field(default="uploads", description="پوشه آپلود")
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,
        description="حداکثر حجم آپلود (بایت)"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".mp3", ".wav", ".mp4"],
        description="پسوندهای مجاز"
    )
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        description="MIME types مجاز برای تصاویر"
    )
    ALLOWED_AUDIO_TYPES: List[str] = Field(
        default=["audio/mpeg", "audio/wav", "audio/ogg"],
        description="MIME types مجاز برای صدا"
    )
    ALLOWED_VIDEO_TYPES: List[str] = Field(
        default=["video/mp4", "video/webm", "video/ogg"],
        description="MIME types مجاز برای ویدئو"
    )

    # ============================================================
    # Cache
    # ============================================================
    CACHE_TTL: int = Field(default=3600, description="زمان کش پیش‌فرض (ثانیه)")
    CACHE_PREFIX: str = Field(default="hermezgan", description="پیشوند کلیدهای کش")
    CACHE_ENABLED: bool = Field(default=True, description="فعال بودن کش")

    # ============================================================
    # Features
    # ============================================================
    ENABLE_WEBSOCKET: bool = Field(default=True, description="فعال بودن WebSocket")
    ENABLE_SPEECH: bool = Field(default=True, description="فعال بودن سرویس صوتی")
    ENABLE_ANALYTICS: bool = Field(default=True, description="فعال بودن تحلیل داده‌ها")
    ENABLE_MAINTENANCE: bool = Field(default=False, description="حالت نگهداری")

    # ============================================================
    # External APIs
    # ============================================================
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, description="کلید API گوگل مپ")
    OPENWEATHER_API_KEY: Optional[str] = Field(default=None, description="کلید API آب و هوا")
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, description="توکن ربات تلگرام")
    SENTRY_DSN: Optional[str] = Field(default=None, description="DSN سنتری")

    # ============================================================
    # Email
    # ============================================================
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="سرور SMTP")
    SMTP_PORT: int = Field(default=587, description="پورت SMTP")
    SMTP_USER: Optional[str] = Field(default=None, description="نام کاربری SMTP")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="رمز عبور SMTP")
    FROM_EMAIL: Optional[str] = Field(default=None, description="ایمیل فرستنده")
    FROM_NAME: str = Field(default="هرمزگان هوشمند", description="نام فرستنده")

    # ============================================================
    # AWS / S3
    # ============================================================
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="کلید دسترسی AWS")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="کلید مخفی AWS")
    AWS_REGION: str = Field(default="us-east-1", description="منطقه AWS")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, description="نام باکت S3")
    AWS_S3_PREFIX: str = Field(default="uploads", description="پیشوند مسیر در S3")
    AWS_CLOUDFRONT_URL: Optional[str] = Field(default=None, description="URL CloudFront")

    # ============================================================
    # Frontend
    # ============================================================
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="آدرس فرانت‌اند")
    FRONTEND_VERIFY_URL: str = Field(default="/verify", description="مسیر تأیید ایمیل")
    FRONTEND_RESET_URL: str = Field(default="/reset-password", description="مسیر بازنشانی رمز")

    # ============================================================
    # Properties
    # ============================================================

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == "staging"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    @property
    def database_url_async(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL

    @property
    def redis_url_async(self) -> str:
        return self.REDIS_URL.replace("redis://", "redis+async://")

    @property
    def redis_url_sync(self) -> str:
        return self.REDIS_URL

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS

    # ============================================================
    # Validators
    # ============================================================

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "your-secret-key-here-change-in-production" and cls.ENVIRONMENT == "production":
            raise ValueError("SECRET_KEY باید در محیط تولید تغییر کند")
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL باید با postgresql:// شروع شود")
        return v

    @validator("REDIS_URL")
    def validate_redis_url(cls, v):
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError("REDIS_URL باید با redis:// یا rediss:// شروع شود")
        return v


settings = Settings()


def is_development() -> bool:
    return settings.is_development


def is_production() -> bool:
    return settings.is_production


def is_staging() -> bool:
    return settings.is_staging


def is_testing() -> bool:
    return settings.is_testing
