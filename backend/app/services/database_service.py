# ============================================================
# database_service.py - سرویس دیتابیس با پشتیبانی از POI
# ============================================================
from typing import List, Dict, Any, Optional
from app.database.connection import execute_query, execute_write, get_table_count
import logging
import math

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """محاسبه فاصله با فرمول هاورسین (به کیلومتر)"""
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return round(R * c, 2)


class DatabaseService:
    """سرویس دسترسی به دیتابیس"""
    
    @staticmethod
    def get_nearby_pois(lat: float, lng: float, category: str = None, radius: float = 5, limit: int = 20):
        """دریافت POIهای نزدیک"""
        try:
            query = """
                SELECT id, cat, name, lat, lon, city, district,
                       (city || ' - ' || COALESCE(district, '')) as address,
                       phone, website,
                       (SELECT distance(lat, lon, ?, ?)) as dist
                FROM poi_unified
                WHERE (? IS NULL OR cat = ?)
                  AND lat BETWEEN ? AND ?
                  AND lon BETWEEN ? AND ?
                ORDER BY dist ASC
                LIMIT ?
            """
            params = (lat, lng, category, category, 
                      lat - radius/111, lat + radius/111,
                      lng - radius/111, lng + radius/111,
                      limit)
            
            results = execute_query(query, params)
            return results
            
        except Exception as e:
            logger.error(f"خطا در دریافت POIهای نزدیک: {e}")
            return []
    
    @staticmethod
    def search_pois(query: str, category: str = None, limit: int = 20):
        """جستجوی POIها"""
        try:
            search_pattern = f"%{query}%"
            sql = """
                SELECT id, cat, name, lat, lon, city, district,
                       (city || ' - ' || COALESCE(district, '')) as address,
                       phone, website
                FROM poi_unified
                WHERE (name LIKE ? OR city LIKE ? OR district LIKE ?)
                  AND (? IS NULL OR cat = ?)
                LIMIT ?
            """
            params = (search_pattern, search_pattern, search_pattern,
                      category, category, limit)
            
            results = execute_query(sql, params)
            return results
            
        except Exception as e:
            logger.error(f"خطا در جستجوی POIها: {e}")
            return []
    
    @staticmethod
    def get_poi_by_id(poi_id: int):
        """دریافت POI با شناسه"""
        query = "SELECT id, cat, name, lat, lon, city, district, (city || ' - ' || COALESCE(district, '')) as address, phone, website FROM poi_unified WHERE id = ?"
        results = execute_query(query, (poi_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_pois_by_category(category: str, limit: int = 50):
        """دریافت POIها بر اساس دسته‌بندی"""
        query = "SELECT id, cat, name, lat, lon, city, district, (city || ' - ' || COALESCE(district, '')) as address, phone, website FROM poi_unified WHERE cat = ? LIMIT ?"
        return execute_query(query, (category, limit))
    
    @staticmethod
    def get_pois_by_city(city: str, limit: int = 50):
        """دریافت POIها بر اساس شهر"""
        query = "SELECT id, cat, name, lat, lon, city, district, (city || ' - ' || COALESCE(district, '')) as address, phone, website FROM poi_unified WHERE city LIKE ? LIMIT ?"
        return execute_query(query, (f"%{city}%", limit))
    
    @staticmethod
    def get_categories():
        """دریافت لیست دسته‌بندی‌ها با تعداد"""
        query = "SELECT cat, COUNT(*) as count FROM poi_unified GROUP BY cat ORDER BY count DESC"
        return execute_query(query)
    
    @staticmethod
    def get_cities():
        """دریافت لیست شهرها با تعداد"""
        query = "SELECT city, COUNT(*) as count FROM poi_unified WHERE city IS NOT NULL AND city != '' GROUP BY city ORDER BY count DESC"
        return execute_query(query)
    
    @staticmethod
    def get_stats():
        """دریافت آمار کلی"""
        total = execute_query("SELECT COUNT(*) as c FROM poi_unified")[0]["c"]
        categories = execute_query("SELECT cat, COUNT(*) as count FROM poi_unified GROUP BY cat ORDER BY count DESC")
        cities = execute_query("SELECT city, COUNT(*) as count FROM poi_unified WHERE city IS NOT NULL AND city != '' GROUP BY city ORDER BY count DESC LIMIT 10")
        return {
            "total_pois": total,
            "categories": categories,
            "top_cities": cities
        }


_db_service = None

def get_db_service() -> DatabaseService:
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
