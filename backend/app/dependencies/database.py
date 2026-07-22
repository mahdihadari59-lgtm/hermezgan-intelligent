from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
from typing import Optional, Generator
import os
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================
# PostgreSQL
# ============================================================

# ایجاد engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.ENVIRONMENT == "development"
)

# ایجاد SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    دریافت جلسه دیتابیس

    Yields:
        Session: جلسه SQLAlchemy

    Usage:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_connection() -> Session:
    """
    دریافت اتصال دیتابیس (برای استفاده در زمینه‌های خاص)

    Returns:
        Session: جلسه SQLAlchemy
    """
    return SessionLocal()


# ============================================================
# Redis
# ============================================================

# اتصال Redis
redis_client: Optional[redis.Redis] = None


def init_redis():
    """مقداردهی اولیه Redis"""
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        redis_client.ping()
        logger.info("✅ Redis متصل شد")
    except Exception as e:
        logger.warning(f"⚠️ Redis متصل نشد: {e}")
        redis_client = None


def get_redis() -> Optional[redis.Redis]:
    """
    دریافت کلاینت Redis

    Returns:
        Optional[redis.Redis]: کلاینت Redis یا None در صورت عدم اتصال

    Usage:
        redis_client = Depends(get_redis)
    """
    return redis_client


def get_redis_or_fail() -> redis.Redis:
    """
    دریافت کلاینت Redis (با خطا در صورت عدم اتصال)

    Returns:
        redis.Redis: کلاینت Redis

    Raises:
        HTTPException: اگر Redis متصل نباشد
    """
    if redis_client is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="سرویس کش در دسترس نیست"
        )
    return redis_client


# ============================================================
# Cache Manager
# ============================================================

from app.cache import CacheManager


def get_cache_manager(
    redis_client: Optional[redis.Redis] = Depends(get_redis)
) -> CacheManager:
    """
    دریافت مدیر کش

    Returns:
        CacheManager: مدیر کش
    """
    return CacheManager()


# ============================================================
# Transaction Management
# ============================================================

from contextlib import contextmanager


@contextmanager
def transaction(db: Session):
    """
    مدیریت تراکنش

    Usage:
        with transaction(db):
            # انجام عملیات
            db.add(something)
            # commit خودکار در صورت عدم خطا
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_transaction(db: Session = Depends(get_db)) -> Session:
    """
    دریافت جلسه دیتابیس با مدیریت تراکنش

    Returns:
        Session: جلسه SQLAlchemy
    """
    return db
