# ============================================================
# pois.py - API برای نقاط جالب توجه (POI)
# ============================================================
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.database_service import get_db_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
db_service = get_db_service()


@router.get("/nearby")
async def get_nearby_pois(
    lat: float = Query(..., ge=-90, le=90, description="عرض جغرافیایی"),
    lng: float = Query(..., ge=-180, le=180, description="طول جغرافیایی"),
    category: Optional[str] = Query(None, description="دسته‌بندی"),
    radius: float = Query(5.0, ge=0.5, le=50, description="شعاع جستجو (کیلومتر)"),
    limit: int = Query(20, ge=1, le=100, description="تعداد نتایج")
):
    """دریافت POIهای نزدیک"""
    results = db_service.get_nearby_pois(lat, lng, category, radius, limit)
    return {
        "location": {"lat": lat, "lng": lng},
        "radius": radius,
        "category": category,
        "results": results,
        "total": len(results)
    }


@router.get("/search")
async def search_pois(
    query: str = Query(..., min_length=2, description="متن جستجو"),
    category: Optional[str] = Query(None, description="دسته‌بندی"),
    limit: int = Query(20, ge=1, le=100, description="تعداد نتایج")
):
    """جستجوی POIها"""
    results = db_service.search_pois(query, category, limit)
    return {
        "query": query,
        "category": category,
        "results": results,
        "total": len(results)
    }




@router.get("/categories")
async def get_categories():
    """دریافت لیست دسته‌بندی‌ها"""
    categories = db_service.get_categories()
    return {
        "categories": categories,
        "total": len(categories)
    }

@router.get("/cities")
async def get_cities():
    """دریافت لیست شهرها"""
    cities = db_service.get_cities()
    return {
        "cities": cities,
        "total": len(cities)
    }

@router.get("/stats")
async def get_stats():
    """دریافت آمار کلی POIها"""
    stats = db_service.get_stats()
    return stats


@router.get("/{poi_id}")
async def get_poi(poi_id: int):
    """دریافت جزئیات یک POI"""
    poi = db_service.get_poi_by_id(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail=f"POI با شناسه {poi_id} یافت نشد")
    return poi


@router.get("/category/{category}")
async def get_pois_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=200)
):
    """دریافت POIها بر اساس دسته‌بندی"""
    results = db_service.get_pois_by_category(category, limit)
    return {
        "category": category,
        "results": results,
        "total": len(results)
    }


@router.get("/city/{city}")
async def get_pois_by_city(
    city: str,
    limit: int = Query(50, ge=1, le=200)
):
    """دریافت POIها بر اساس شهر"""
    results = db_service.get_pois_by_city(city, limit)
    return {
        "city": city,
        "results": results,
        "total": len(results)
    }



