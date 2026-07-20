
import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from pathlib import Path

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =======================================================
# Database Configuration
# =======================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = str(BASE_DIR / "hdp_v2.db")

class SQLiteService:
    """سرویس دیتابیس SQLite با پشتیبانی از محیط چندنخی"""

    def __init__(self, db_path: str = None):
        """
        Initialize SQLite service
        
        Args:
            db_path: Path to database file. If None, uses DATABASE_PATH from config
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        
        # Ensure directory exists
        db_dir = self._get_db_dir()
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        logger.info(f"SQLiteService initialized with: {self.db_path}")

    def _get_db_dir(self) -> str:
        """دریافت مسیر پوشه دیتابیس"""
        db_dir = os.path.dirname(self.db_path)
        return db_dir if db_dir else "."

    @contextmanager
    def get_connection(self):
        """
        ایجاد یک Connection جدید برای هر درخواست
        استفاده از context manager برای بستن خودکار
        """
        db_dir = self._get_db_dir()
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-10000")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def create_tables(self):
        """ایجاد جدول‌های مورد نیاز"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # جدول دانش
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        original_title TEXT,
                        content TEXT NOT NULL,
                        category TEXT,
                        keywords TEXT,
                        source TEXT,
                        views INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # جدول FTS5
                cursor.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS hormozgan_fts USING fts5(
                        title,
                        content,
                        category,
                        tokenize='unicode61 remove_diacritics 2'
                    )
                ''')

                # جدول Embeddings (برای Hybrid Engine)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                        node_id TEXT PRIMARY KEY,
                        embedding BLOB NOT NULL,
                        node_type TEXT,
                        category TEXT,
                        dimension INTEGER DEFAULT 128,
                        embedding_type TEXT DEFAULT 'hybrid',
                        model_version TEXT DEFAULT 'v1.0.0',
                        checksum TEXT,
                        score REAL DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # جدول Graph (برای Knowledge Graph)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge_graph (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        from_entity TEXT NOT NULL,
                        to_entity TEXT NOT NULL,
                        relation_type TEXT NOT NULL,
                        weight REAL DEFAULT 1.0,
                        confidence REAL DEFAULT 0.8,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (from_entity) REFERENCES knowledge(id),
                        FOREIGN KEY (to_entity) REFERENCES knowledge(id)
                    )
                ''')

                conn.commit()
                logger.info(f"Tables created successfully in {self.db_path}")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def execute_query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """
        اجرای یک کوئری SELECT و برگرداندن نتایج
        هر بار یک Connection و Cursor جدید ایجاد می‌شود
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            logger.error(f"SQLite operational error: {e}")
            logger.error(f"SQL: {sql}")
            logger.error(f"Params: {params}")
            raise
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def execute_write(self, sql: str, params: tuple = ()) -> int:
        """
        اجرای یک کوئری نوشتنی (INSERT/UPDATE/DELETE)
        برگرداندن آخرین ID درج شده
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else 0
        except Exception as e:
            logger.error(f"Write execution error: {e}")
            logger.error(f"SQL: {sql}")
            logger.error(f"Params: {params}")
            raise

    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """
        اجرای چندین کوئری نوشتنی (Bulk Insert/Update)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Bulk execution error: {e}")
            raise

    def execute_transaction(self, operations: List[Dict]) -> bool:
        """
        اجرای یک تراکنش شامل چندین عملیات
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                for op in operations:
                    sql = op.get('sql')
                    params = op.get('params', ())
                    cursor.execute(sql, params)
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            return False

    def get_table_info(self, table_name: str) -> List[Dict]:
        """دریافت اطلاعات ساختار جدول"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return []

    def get_table_count(self, table_name: str) -> int:
        """دریافت تعداد رکوردهای یک جدول"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting table count: {e}")
            return 0

    def vacuum(self):
        """بهینه‌سازی دیتابیس"""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuum completed")
        except Exception as e:
            logger.error(f"Vacuum error: {e}")

    def check_connection(self):
        """
        بررسی اتصال به دیتابیس
        """
        try:
            with self.get_connection() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def close(self):
        """بستن اتصال‌ها (برای سازگاری)"""
        logger.info("SQLiteService closing connections")
        # Connections are managed per request, nothing to close globally

    def stats(self) -> Dict:
        """دریافت آمار دیتابیس"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # تعداد جدول‌ها
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # اندازه دیتابیس
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                # آمار هر جدول
                table_stats = {}
                for table in tables:
                    if table.startswith('sqlite_'):
                        continue
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_stats[table] = count
                
                return {
                    'db_path': self.db_path,
                    'db_size_mb': round(db_size / (1024 * 1024), 2),
                    'tables': len([t for t in tables if not t.startswith('sqlite_')]),
                    'table_stats': table_stats,
                    'journal_mode': conn.execute("PRAGMA journal_mode").fetchone()[0],
                    'cache_size': conn.execute("PRAGMA cache_size").fetchone()[0],
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# =======================================================
# Singleton instance
# =======================================================

_sqlite_service = None


def get_sqlite_service(db_path: str = None) -> SQLiteService:
    """Get or create SQLiteService singleton"""
    global _sqlite_service
    if _sqlite_service is None or (db_path and _sqlite_service.db_path != db_path):
        _sqlite_service = SQLiteService(db_path)
    return _sqlite_service



# =======================================================
# Legacy compatibility
# =======================================================

db = get_sqlite_service(DEFAULT_DB_PATH)

# =======================================================
# Usage Example
# =======================================================

if __name__ == "__main__":
    # Test the service
    service = SQLiteService()
    print(f"Database: {service.db_path}")
    print(f"Tables created: {service.create_tables()}")
    print(f"Stats: {service.stats()}")
