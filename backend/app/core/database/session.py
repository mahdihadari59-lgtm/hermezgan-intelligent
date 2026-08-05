from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
from typing import Generator, Optional, Any
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseSession:
    """
    مدیریت جلسات دیتابیس
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
        """مقداردهی اولیه"""
        try:
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

            @event.listens_for(self._engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                conn.info.setdefault('query_start_time', []).append(time.time())

            @event.listens_for(self._engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                total = time.time() - conn.info['query_start_time'].pop(-1)
                if total > 1.0:
                    logger.warning(f"🐢 Slow query ({total:.2f}s): {statement[:200]}")

            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False
            )

            self._scoped_session = scoped_session(self._session_factory)

            logger.info("✅ Database Session initialized")
            logger.info(f"   Pool Size: {settings.DATABASE_POOL_SIZE}")
            logger.info(f"   Max Overflow: {settings.DATABASE_MAX_OVERFLOW}")

        except Exception as e:
            logger.error(f"❌ Database Session initialization failed: {e}")
            raise

    @property
    def engine(self):
        return self._engine

    @property
    def session_factory(self):
        return self._session_factory

    def get_session(self) -> Session:
        return self._scoped_session()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
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
        if session is None:
            session = self.get_session()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def close(self):
        if self._scoped_session:
            self._scoped_session.remove()
        if self._engine:
            self._engine.dispose()
            logger.info("✅ Database connections closed")

    def ping(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"❌ Database ping failed: {e}")
            return False


_db_session = None


def get_db_session_manager() -> DatabaseSession:
    global _db_session
    if _db_session is None:
        _db_session = DatabaseSession()
    return _db_session


def get_db() -> Generator[Session, None, None]:
    manager = get_db_session_manager()
    session = manager.get_session()
    try:
        yield session
    finally:
        session.close()


def get_db_session() -> Session:
    manager = get_db_session_manager()
    return manager.get_session()


@contextmanager
def db_transaction(session: Optional[Session] = None):
    manager = get_db_session_manager()
    with manager.transaction(session) as sess:
        yield sess
