"""
اتصال مرکزی به دیتابیس HDP
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """مدیریت اتصال به دیتابیس HDP"""
    
    _instance = None
    _connection = None
    _db_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        
        # مسیر درست دیتابیس
        self._db_path = Path("/data/data/com.termux/files/home/hermezgan-intelligent-backup-20260729/backend/hdp_v2.db")
        
        logger.info(f"📁 Database path: {self._db_path}")
        self._connect()
    
    def _connect(self):
        """اتصال به دیتابیس"""
        try:
            if not self._db_path.exists():
                logger.error(f"❌ Database not found: {self._db_path}")
                self._connection = None
                return
            
            self._connection = sqlite3.connect(str(self._db_path))
            self._connection.row_factory = sqlite3.Row
            size_mb = self._db_path.stat().st_size / 1024 / 1024
            logger.info(f"✅ Connected to database: {self._db_path} ({size_mb:.1f} MB)")
            
            # نمایش جدول‌ها
            cursor = self._connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 10")
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]
            logger.info(f"📊 Tables found: {table_names}")
            
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            self._connection = None
    
    def get_connection(self):
        """دریافت اتصال"""
        if self._connection is None:
            self._connect()
        return self._connection
    
    def get_db_path(self):
        """دریافت مسیر دیتابیس"""
        return self._db_path
    
    def close(self):
        """بستن اتصال"""
        if self._connection:
            self._connection.close()
            self._connection = None


# نمونه Singleton
db_connection = DatabaseConnection()
