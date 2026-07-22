from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database.session import get_db_session_manager

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    مدیریت اتصالات دیتابیس و اطلاعات
    """

    def __init__(self):
        self.manager = get_db_session_manager()
        self.engine = self.manager.engine

    def get_status(self) -> Dict[str, Any]:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                connected = result is not None

            return {
                "connected": connected,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
                "environment": settings.ENVIRONMENT
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

    def get_tables(self) -> List[str]:
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        inspector = inspect(self.engine)

        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)

        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
            row_count = result[0] if result else 0

        return {
            "name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": col.get("default")
                }
                for col in columns
            ],
            "primary_key": primary_keys.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                }
                for fk in foreign_keys
            ],
            "indexes": [
                {
                    "name": idx["name"],
                    "columns": idx["column_names"],
                    "unique": idx["unique"]
                }
                for idx in indexes
            ],
            "row_count": row_count
        }

    def get_database_size(self) -> float:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT pg_database_size(current_database()) / 1024 / 1024
                """)).fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def get_active_connections(self) -> int:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM pg_stat_activity
                    WHERE datname = current_database()
                """)).fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def execute_raw_query(self, query: str) -> List[Dict]:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"❌ Error executing raw query: {e}")
            return []

    def get_schema_info(self) -> Dict[str, Any]:
        tables = self.get_tables()

        return {
            "database": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "unknown",
            "tables": [
                self.get_table_info(table) for table in tables
            ],
            "total_tables": len(tables),
            "database_size_mb": self.get_database_size(),
            "active_connections": self.get_active_connections()
        }


_db_connection = None


def get_connection() -> DatabaseConnection:
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection
