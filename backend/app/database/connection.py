# ============================================================
# connection.py - اتصال به دیتابیس SQLite
# ============================================================
import sqlite3
import os
from typing import Dict, Any, List, Optional
import logging
import math

logger = logging.getLogger(__name__)


def _haversine(lat1, lon1, lat2, lon2):
    """فاصله بین دو نقطه جغرافیایی به کیلومتر"""
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

# مسیر دیتابیس
DB_PATH = os.getenv("DATABASE_PATH", "")

# اگر در .env تنظیم نشده، مسیرهای احتمالی را بررسی کن
if not DB_PATH or not os.path.exists(DB_PATH):
    possible_paths = [
        "../hormozgan_geo_project/hormozgan_data/hormozgan_geodata.db",
        "hormozgan_data/hormozgan_geodata.db",
        "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_geodata.db",
        "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan.db",
        os.path.expanduser("~/hormozgan_geo_project/hormozgan_data/hormozgan_geodata.db"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            DB_PATH = path
            logger.info(f"✅ دیتابیس در مسیر {DB_PATH} پیدا شد")
            break
    
    if not DB_PATH:
        logger.warning("⚠️ دیتابیس در هیچ مسیری یافت نشد")
        # جستجوی خودکار
        import subprocess
        result = subprocess.run(['find', '/data/data/com.termux/files/home', '-name', 'hormozgan_geodata.db', '-type', 'f'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            DB_PATH = result.stdout.strip().split('\n')[0]
            logger.info(f"✅ دیتابیس با find پیدا شد: {DB_PATH}")


def get_db_connection():
    """دریافت اتصال به دیتابیس"""
    if not DB_PATH or not os.path.exists(DB_PATH):
        logger.error(f"❌ دیتابیس در مسیر {DB_PATH} وجود ندارد")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.create_function("distance", 4, _haversine)
        return conn
    except Exception as e:
        logger.error(f"خطا در اتصال به دیتابیس: {e}")
        return None


def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """اجرای کوئری و بازگرداندن نتایج"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # تبدیل به دیکشنری
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"خطا در اجرای کوئری: {e}")
        if conn:
            conn.close()
        return []


def execute_write(query: str, params: tuple = ()) -> int:
    """اجرای کوئری نوشتن (INSERT, UPDATE, DELETE)"""
    conn = get_db_connection()
    if not conn:
        return -1
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    except Exception as e:
        logger.error(f"خطا در اجرای کوئری نوشتن: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return -1


def get_tables() -> List[str]:
    """دریافت لیست تمام جداول"""
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    results = execute_query(query)
    return [row["name"] for row in results]


def get_table_count(table_name: str) -> int:
    """دریافت تعداد رکوردهای یک جدول"""
    query = f"SELECT COUNT(*) as count FROM {table_name}"
    result = execute_query(query)
    return result[0]["count"] if result else 0


def get_table_info(table_name: str) -> Dict[str, Any]:
    """دریافت اطلاعات یک جدول"""
    query = f"PRAGMA table_info({table_name})"
    results = execute_query(query)
    return {
        "columns": [row["name"] for row in results],
        "count": get_table_count(table_name)
    }
