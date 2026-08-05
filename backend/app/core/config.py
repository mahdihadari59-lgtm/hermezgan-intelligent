#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
config.py - تنظیمات اصلی برنامه
============================================================
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    تنظیمات اصلی برنامه
    """
    
    # ============================================================
    # تنظیمات عمومی
    # ============================================================
    APP_NAME: str = "هرمزگان هوشمند"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # ============================================================
    # تنظیمات سرور
    # ============================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    WORKERS: int = 4
    
    # ============================================================
    # تنظیمات CORS
    # ============================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "https://hermezgan.ir",
        "https://www.hermezgan.ir"
    ]
    CORS_ORIGINS_REGEX: str = "^https://.*hermezgan.ir$,^http://localhost:.*$"
    CORS_POLICY: str = "relaxed"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 86400
    CORS_METHODS: str = "GET,POST,PUT,DELETE,PATCH,OPTIONS"
    
    # ============================================================
    # تنظیمات دیتابیس
    # ============================================================
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/hermezgan_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False
    
    # ============================================================
    # تنظیمات Redis
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600
    
    # ============================================================
    # تنظیمات JWT و امنیت
    # ============================================================
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_HOURS: int = 24
    VERIFY_TOKEN_EXPIRE_HOURS: int = 72
    
    # ============================================================
    # تنظیمات BCrypt
    # ============================================================
    BCRYPT_ROUNDS: int = 12
    
    # ============================================================
    # تنظیمات API و Third-party
    # ============================================================
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # ============================================================
    # تنظیمات ایمیل
    # ============================================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@hermezgan.ir"
    
    # ============================================================
    # تنظیمات لاگ
    # ============================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    
    # ============================================================
    # تنظیمات آپلود فایل
    # ============================================================
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = ".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx"
    
    # ============================================================
    # تنظیمات AWS
    # ============================================================
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "me-south-1"
    AWS_S3_BUCKET: Optional[str] = None
    AWS_CLOUDFRONT_URL: Optional[str] = None
    
    # ============================================================
    # تنظیمات Monitoring
    # ============================================================
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # ============================================================
    # تنظیمات Rate Limiting
    # ============================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # ============================================================
    # تنظیمات Feature Flags
    # ============================================================
    FEATURE_CHATBOT_ENABLED: bool = True
    FEATURE_MAP_ENABLED: bool = True
    FEATURE_DASHBOARD_ENABLED: bool = True
    FEATURE_CAMERAS_ENABLED: bool = True
    FEATURE_HOTSPOTS_ENABLED: bool = True
    FEATURE_VOICE_ENABLED: bool = True
    
    # ============================================================
    # تنظیمات دیگر
    # ============================================================
    TIMEZONE: str = "Asia/Tehran"
    DEFAULT_LANGUAGE: str = "fa"
    DEFAULT_THEME: str = "light"
    PROJECT_ROOT: str = "/app"
    
    # ============================================================
    # تنظیمات دیتابیس HDP
    # ============================================================
    HDP_DB_PATH: str = "data/hdp_v2.db"
    
    class Config:
        """تنظیمات Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# ============================================================
# ایجاد نمونه تنظیمات
# ============================================================
settings = Settings()


# ============================================================
# توابع کمکی
# ============================================================

def get_settings() -> Settings:
    """دریافت تنظیمات"""
    return settings


def is_development() -> bool:
    """بررسی محیط توسعه"""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """بررسی محیط تولید"""
    return settings.ENVIRONMENT == "production"


def is_testing() -> bool:
    """بررسی محیط تست"""
    return settings.ENVIRONMENT == "testing"


# ============================================================
# تست سریع
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("✅ تست تنظیمات")
    print("=" * 60)
    
    print(f"\n📋 APP_NAME: {settings.APP_NAME}")
    print(f"📋 APP_VERSION: {settings.APP_VERSION}")
    print(f"📋 ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"📋 DATABASE_URL: {settings.DATABASE_URL}")
    print(f"📋 REDIS_URL: {settings.REDIS_URL}")
    print(f"📋 CORS_ORIGINS: {settings.CORS_ORIGINS}")
    print(f"📋 HDP_DB_PATH: {settings.HDP_DB_PATH}")
    
    print("\n✅ تنظیمات با موفقیت بارگذاری شد!")
