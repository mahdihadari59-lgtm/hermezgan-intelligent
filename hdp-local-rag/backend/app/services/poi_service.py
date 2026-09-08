# ============================================================
# poi_service.py - به‌روزرسانی کامل سرویس POI
# ============================================================

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

from app.database.connection import execute_query, get_table_count

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    محاسبه فاصله بین دو نقطه با فرمول هاورسین
    خروجی: کیلومتر
    """
    R = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


class POIService:
    """
    سرویس مدیریت نقاط جالب توجه (POI)
    شامل: جستجو، فیلتر، نزدیک‌ترین‌ها، آمار
    """

    def __init__(self):
        self._cache: Dict[Tuple[Any, ...], Tuple[float, Any]] = {}
        self._cache_ttl = 300  # ثانیه

    def _cache_get(self, key: Tuple[Any, ...]) -> Any:
        item = self._cache.get(key)
        if not item:
            return None

        ts, value = item
        if time.time() - ts > self._cache_ttl:
            self._cache.pop(key, None)
            return None

        return value

    def _cache_set(self, key: Tuple[Any, ...], value: Any) -> None:
        self._cache[key] = (time.time(), value)

    @staticmethod
    def _row_to_dict(row: Any) -> Dict[str, Any]:
        if row is None:
            return {}
        if isinstance(row, dict):
            return dict(row)
        try:
            return dict(row)
        except Exception:
            try:
                return {
                    "id": row[0],
                    "category": row[1],
                    "name": row[2],
                    "lat": row[3],
                    "lon": row[4],
                    "city": row[5],
                    "district": row[6],
                    "address": row[7],
                    "phone": row[8],
                    "website": row[9],
                }
            except Exception:
                return {"value": row}

    @staticmethod
    def _validate_lat_lng(lat: float, lng: float) -> None:
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            raise ValueError("lat/lng must be numeric")
        if not (-90.0 <= float(lat) <= 90.0):
            raise ValueError("Invalid latitude")
        if not (-180.0 <= float(lng) <= 180.0):
            raise ValueError("Invalid longitude")

    @staticmethod
    def _validate_radius(radius: float) -> float:
        radius = float(radius)
        if radius <= 0:
            raise ValueError("radius must be > 0")
        return min(radius, 100.0)

    @staticmethod
    def _validate_limit(limit: int) -> int:
        limit = int(limit)
        if limit < 1:
            return 1
        return min(limit, 200)

    @staticmethod
    def _bbox(lat: float, lng: float, radius_km: float) -> Tuple[float, float, float, float]:
        lat_delta = radius_km / 111.0

        cos_lat = math.cos(math.radians(lat))
        cos_lat = max(cos_lat, 0.01)
        lng_delta = radius_km / (111.0 * cos_lat)

        lat_min = lat - lat_delta
        lat_max = lat + lat_delta
        lng_min = lng - lng_delta
        lng_max = lng + lng_delta

        return lat_min, lat_max, lng_min, lng_max

    def get_nearby_pois(
        self,
        lat: float,
        lng: float,
        category: Optional[str] = None,
        radius: float = 5.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            self._validate_lat_lng(lat, lng)
            radius = self._validate_radius(radius)
            limit = self._validate_limit(limit)
            category = _normalize_text(category) or None

            cache_key = (
                "nearby",
                round(float(lat), 5),
                round(float(lng), 5),
                category,
                round(float(radius), 3),
                limit,
            )
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            lat_min, lat_max, lng_min, lng_max = self._bbox(lat, lng, radius)

            sql = """
                SELECT
                    id,
                    cat AS category,
                    name,
                    lat,
                    lon,
                    city,
                    district,
                    address,
                    phone,
                    website
                FROM pois
                WHERE lat IS NOT NULL
                  AND lon IS NOT NULL
                  AND lat BETWEEN ? AND ?
                  AND lon BETWEEN ? AND ?
            """
            params: List[Any] = [lat_min, lat_max, lng_min, lng_max]

            if category:
                sql += " AND LOWER(COALESCE(cat, '')) = LOWER(?)"
                params.append(category)

            rows = execute_query(sql, tuple(params)) or []

            results: List[Dict[str, Any]] = []
            for row in rows:
                item = self._row_to_dict(row)

                row_lat = item.get("lat")
                row_lng = item.get("lon")
                if row_lat is None or row_lng is None:
                    continue

                try:
                    distance_km = haversine_distance(
                        float(lat),
                        float(lng),
                        float(row_lat),
                        float(row_lng),
                    )
                except Exception:
                    continue

                if distance_km <= radius:
                    item["distance"] = distance_km
                    results.append(item)

            results.sort(key=lambda x: x.get("distance", 999999.0))
            results = results[:limit]

            self._cache_set(cache_key, results)
            return results

        except Exception as e:
            logger.error(f"خطا در دریافت POIهای نزدیک: {e}")
            return []

    def search_pois(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            query = _normalize_text(query)
            if not query:
                return []

            limit = self._validate_limit(limit)
            category = _normalize_text(category) or None

            cache_key = (
                "search",
                query.lower(),
                category,
                limit,
            )
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            pattern = f"%{query}%"

            sql = """
                SELECT
                    id,
                    cat AS category,
                    name,
                    lat,
                    lon,
                    city,
                    district,
                    address,
                    phone,
                    website
                FROM pois
                WHERE (
                    LOWER(COALESCE(name, '')) LIKE LOWER(?)
                    OR LOWER(COALESCE(address, '')) LIKE LOWER(?)
                    OR LOWER(COALESCE(city, '')) LIKE LOWER(?)
                    OR LOWER(COALESCE(district, '')) LIKE LOWER(?)
                )
            """
            params: List[Any] = [pattern, pattern, pattern, pattern]

            if category:
                sql += " AND LOWER(COALESCE(cat, '')) = LOWER(?)"
                params.append(category)

            rows = execute_query(sql, tuple(params)) or []
            results = [self._row_to_dict(r) for r in rows]

            q_lower = query.lower()

            def score(item: Dict[str, Any]) -> Tuple[int, str]:
                name = _normalize_text(item.get("name")).lower()
                city = _normalize_text(item.get("city")).lower()
                district = _normalize_text(item.get("district")).lower()
                address = _normalize_text(item.get("address")).lower()

                if name == q_lower:
                    rank = 0
                elif name.startswith(q_lower):
                    rank = 1
                elif q_lower in name:
                    rank = 2
                elif q_lower in city:
                    rank = 3
                elif q_lower in district:
                    rank = 4
                elif q_lower in address:
                    rank = 5
                else:
                    rank = 6

                return rank, name

            results.sort(key=score)
            results = results[:limit]

            self._cache_set(cache_key, results)
            return results

        except Exception as e:
            logger.error(f"خطا در جستجوی POIها: {e}")
            return []

    def get_poi_by_id(self, poi_id: int) -> Optional[Dict[str, Any]]:
        try:
            poi_id = int(poi_id)

            cache_key = ("poi_by_id", poi_id)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            sql = """
                SELECT
                    id,
                    cat AS category,
                    name,
                    lat,
                    lon,
                    city,
                    district,
                    address,
                    phone,
                    website
                FROM pois
                WHERE id = ?
                LIMIT 1
            """
            results = execute_query(sql, (poi_id,)) or []
            item = self._row_to_dict(results[0]) if results else None

            self._cache_set(cache_key, item)
            return item

        except Exception as e:
            logger.error(f"خطا در دریافت POI با شناسه {poi_id}: {e}")
            return None

    def get_pois_by_category(
        self,
        category: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        try:
            category = _normalize_text(category)
            if not category:
                return []

            limit = self._validate_limit(limit)

            cache_key = ("pois_by_category", category.lower(), limit)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            sql = """
                SELECT
                    id,
                    cat AS category,
                    name,
                    lat,
                    lon,
                    city,
                    district,
                    address,
                    phone,
                    website
                FROM pois
                WHERE LOWER(COALESCE(cat, '')) = LOWER(?)
                ORDER BY name ASC
                LIMIT ?
            """
            results = execute_query(sql, (category, limit)) or []
            data = [self._row_to_dict(r) for r in results]

            self._cache_set(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"خطا در دریافت POIهای دسته {category}: {e}")
            return []

    def get_pois_by_city(
        self,
        city: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        try:
            city = _normalize_text(city)
            if not city:
                return []

            limit = self._validate_limit(limit)

            cache_key = ("pois_by_city", city.lower(), limit)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            sql = """
                SELECT
                    id,
                    cat AS category,
                    name,
                    lat,
                    lon,
                    city,
                    district,
                    address,
                    phone,
                    website
                FROM pois
                WHERE LOWER(COALESCE(city, '')) LIKE LOWER(?)
                ORDER BY name ASC
                LIMIT ?
            """
            results = execute_query(sql, (f"%{city}%", limit)) or []
            data = [self._row_to_dict(r) for r in results]

            self._cache_set(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"خطا در دریافت POIهای شهر {city}: {e}")
            return []

    def get_categories(self) -> List[Dict[str, Any]]:
        try:
            cache_key = ("categories",)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            sql = """
                SELECT
                    COALESCE(cat, 'unknown') AS category,
                    COUNT(*) AS count
                FROM pois
                GROUP BY COALESCE(cat, 'unknown')
                ORDER BY count DESC, category ASC
            """
            results = execute_query(sql) or []
            data = [self._row_to_dict(r) for r in results]

            self._cache_set(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"خطا در دریافت دسته‌بندی‌ها: {e}")
            return []

    def get_cities(self) -> List[Dict[str, Any]]:
        try:
            cache_key = ("cities",)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            sql = """
                SELECT
                    city,
                    COUNT(*) AS count
                FROM pois
                WHERE city IS NOT NULL
                  AND TRIM(city) != ''
                GROUP BY city
                ORDER BY count DESC, city ASC
                LIMIT 50
            """
            results = execute_query(sql) or []
            data = [self._row_to_dict(r) for r in results]

            self._cache_set(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"خطا در دریافت شهرها: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        try:
            total = get_table_count("pois")
            categories = self.get_categories()
            cities = self.get_cities()

            return {
                "total_pois": total,
                "categories": categories,
                "top_cities": cities,
                "has_data": total > 0,
            }

        except Exception as e:
            logger.error(f"خطا در دریافت آمار: {e}")
            return {
                "total_pois": 0,
                "categories": [],
                "top_cities": [],
                "has_data": False,
                "error": str(e),
            }

    def get_nearby_stats(
        self,
        lat: float,
        lng: float,
        radius: float = 5.0
    ) -> Dict[str, Any]:
        try:
            self._validate_lat_lng(lat, lng)
            radius = self._validate_radius(radius)

            lat_min, lat_max, lng_min, lng_max = self._bbox(lat, lng, radius)

            total_sql = """
                SELECT COUNT(*) AS total
                FROM pois
                WHERE lat IS NOT NULL
                  AND lon IS NOT NULL
                  AND lat BETWEEN ? AND ?
                  AND lon BETWEEN ? AND ?
            """
            total_result = execute_query(total_sql, (lat_min, lat_max, lng_min, lng_max)) or []
            total = int(total_result[0]["total"]) if total_result else 0

            cat_sql = """
                SELECT
                    COALESCE(cat, 'unknown') AS category,
                    COUNT(*) AS count
                FROM pois
                WHERE lat IS NOT NULL
                  AND lon IS NOT NULL
                  AND lat BETWEEN ? AND ?
                  AND lon BETWEEN ? AND ?
                GROUP BY COALESCE(cat, 'unknown')
                ORDER BY count DESC, category ASC
            """
            categories = execute_query(cat_sql, (lat_min, lat_max, lng_min, lng_max)) or []
            categories = [self._row_to_dict(r) for r in categories]

            return {
                "total": total,
                "categories": categories,
                "location": {"lat": float(lat), "lng": float(lng)},
                "radius": float(radius),
            }

        except Exception as e:
            logger.error(f"خطا در دریافت آمار نزدیک: {e}")
            return {
                "total": 0,
                "categories": [],
                "location": {"lat": lat, "lng": lng},
                "radius": radius,
                "error": str(e),
            }


_poi_service_instance: Optional[POIService] = None


def get_poi_service() -> POIService:
    global _poi_service_instance
    if _poi_service_instance is None:
        _poi_service_instance = POIService()
    return _poi_service_instance


if __name__ == "__main__":
    print("=" * 60)
    print("📍 تست سرویس POI")
    print("=" * 60)

    service = get_poi_service()

    print("\n📊 دسته‌بندی‌ها:")
    categories = service.get_categories()
    for cat in categories[:10]:
        print(f"   - {cat.get('category')}: {cat.get('count')}")

    print("\n🏙️ شهرها:")
    cities = service.get_cities()
    for city in cities[:10]:
        print(f"   - {city.get('city')}: {city.get('count')}")

    print("\n📊 آمار کلی:")
    stats = service.get_stats()
    print(f"   کل POIها: {stats['total_pois']}")
    print(f"   تعداد دسته‌بندی‌ها: {len(stats['categories'])}")

    print("\n📍 POIهای نزدیک به بندرعباس:")
    pois = service.get_nearby_pois(27.2158, 56.2808, radius=3, limit=5)
    for poi in pois:
        print(f"   - {poi.get('name')} ({poi.get('category')}) - {poi.get('distance', 0):.2f}km")

    print("\n✅ تست سرویس POI با موفقیت انجام شد!")
