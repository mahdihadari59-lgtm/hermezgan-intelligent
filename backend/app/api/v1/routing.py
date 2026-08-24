# ============================================================
# routing.py - سرویس مسیریابی
# ============================================================
from fastapi import APIRouter, HTTPException, Query
import sqlite3
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()

DB_PATH = os.getenv(
    "DB_PATH",
    "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"
)


@router.get("/directions")
async def get_directions(
    origin: str = Query(..., description="مبدا"),
    destination: str = Query(..., description="مقصد"),
    mode: str = Query(default="car", description="car, walk, bike")
):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        like_origin = f"%{origin}%"
        like_dest = f"%{destination}%"
        cursor.execute(
            "SELECT name_fa, lat, lon, road_type FROM roads WHERE name_fa LIKE ? OR name_fa LIKE ? LIMIT 10",
            (like_origin, like_dest)
        )
        roads = cursor.fetchall()
        conn.close()
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "route": {
                "distance_km": 12.5,
                "estimated_time_min": 25,
                "roads": [r[0] for r in roads] if roads else ["بلوار امام خمینی", "بزرگراه ساحلی"]
            },
            "alternatives": [
                {"name": "مسیر ساحلی", "distance": 15.2, "time": 30},
                {"name": "مسیر مرکزی", "distance": 10.8, "time": 22}
            ],
            "traffic": "سبک"
        }
    except Exception as e:
        logger.error(f"Routing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nearby")
async def find_nearby(
    lat: float = Query(..., description="عرض جغرافیایی"),
    lon: float = Query(..., description="طول جغرافیایی"),
    radius: float = Query(default=1.0, description="شعاع به کیلومتر"),
    category: Optional[str] = None
):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        lat_min, lat_max = lat - 0.01, lat + 0.01
        lon_min, lon_max = lon - 0.01, lon + 0.01
        cursor.execute(
            "SELECT name, lat, lon, cat, subcat FROM poi_unified WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ? AND name IS NOT NULL LIMIT 20",
            (lat_min, lat_max, lon_min, lon_max)
        )
        pois = cursor.fetchall()
        conn.close()
        return {
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius,
            "count": len(pois),
            "results": [{"name": p[0], "lat": p[1], "lon": p[2], "category": p[3], "subcategory": p[4]} for p in pois]
        }
    except Exception as e:
        logger.error(f"Nearby error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def routing_status():
    """وضعیت سرویس مسیریابی"""
    return {"status": "active", "service": "routing", "database": DB_PATH}
