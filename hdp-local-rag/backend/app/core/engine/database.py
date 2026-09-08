from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import contextmanager
from typing import Generator, Optional, Any
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseEngine:
    """
    موتور دیتابیس با قابلیت‌های پیشرفته
    مدیریت اتصالات، Connection Pool، Query Monitoring
    """

    _instance = None
    _engine = None
    _session_factory = None
    _scoped_session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """مقداردهی اولیه موتور دیتابیس"""
        try:
            # ایجاد موتور SQLAlchemy
            self._engine = create_engine(
                settings.DATABASE_URL,
                poolclass=QueuePool if settings.ENVIRONMENT == "production" else NullPool,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_recycle=3600,
                pool_pre_ping=True,
                echo=settings.DATABASE_ECHO,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": f"hermezgan_{settings.ENVIRONMENT}"
                }
            )

            # افزودن شنونده برای نمایش کوئری‌های کند
            @event.listens_for(self._engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                conn.info.setdefault('query_start_time', []).append(time.time())

            @event.listens_for(self._engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                total = time.time() - conn.info['query_start_time'].pop(-1)
                if total > 1.0:  # کوئری‌های بیش از ۱ ثانیه
                    logger.warning(f"🐢 Slow query ({total:.2f}s): {statement[:200]}")

            # ایجاد Session Factory
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False
            )

            # Scoped Session برای Thread Safety
            self._scoped_session = scoped_session(self._session_factory)

            logger.info("✅ Database Engine initialized successfully")
            logger.info(f"   Pool Size: {settings.DATABASE_POOL_SIZE}")
            logger.info(f"   Max Overflow: {settings.DATABASE_MAX_OVERFLOW}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Database Engine: {e}")
            raise

    @property
    def engine(self):
        return self._engine

    @property
    def session_factory(self):
        return self._session_factory

    def get_session(self) -> Session:
        """دریافت جلسه دیتابیس"""
        return self._scoped_session()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context Manager برای مدیریت جلسه دیتابیس
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def transaction(self, session: Optional[Session] = None) -> Generator[Session, None, None]:
        """
        Context Manager برای مدیریت تراکنش
        """
        if session is None:
            session = self.get_session()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def close(self):
        """بستن تمام اتصالات"""
        if self._scoped_session:
            self._scoped_session.remove()
        if self._engine:
            self._engine.dispose()
            logger.info("✅ Database connections closed")

    def ping(self) -> bool:
        """بررسی اتصال به دیتابیس"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"❌ Database ping failed: {e}")
            return False

    def get_connection_info(self) -> dict:
        """دریافت اطلاعات اتصال"""
        return {
            "url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
            "status": "connected" if self.ping() else "disconnected"
        }


# ============================================================
# Convenience Functions
# ============================================================

_db_engine = None


def get_db_engine() -> DatabaseEngine:
    """دریافت نمونه Database Engine"""
    global _db_engine
    if _db_engine is None:
        _db_engine = DatabaseEngine()
    return _db_engine


def get_db() -> Generator[Session, None, None]:
    """
    Dependency برای دریافت جلسه دیتابیس
    استفاده در FastAPI: db: Session = Depends(get_db)
    """
    engine = get_db_engine()
    session = engine.get_session()
    try:
        yield session
    finally:
        session.close()


def get_db_session() -> Session:
    """دریافت جلسه دیتابیس (بدون Dependency)"""
    engine = get_db_engine()
    return engine.get_session()


@contextmanager
def db_transaction(session: Optional[Session] = None):
    """Context Manager برای تراکنش دیتابیس"""
    engine = get_db_engine()
    with engine.transaction(session) as sess:
        yield sess
