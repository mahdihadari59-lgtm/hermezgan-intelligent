# ============================================================
# pois.py - Router کامل و بدون تداخل مسیر
# ============================================================

from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional

from app.services.poi_service import get_poi_service

router = APIRouter(prefix="/api/v1/pois", tags=["POI"])
poi_service = get_poi_service()


@router.get("/categories")
def get_categories():
    items = poi_service.get_categories()
    return {
        "items": items,
        "total": len(items),
    }


@router.get("/cities")
def get_cities():
    items = poi_service.get_cities()
    return {
        "items": items,
        "total": len(items),
    }


@router.get("/search")
def search_pois(
    q: str = Query(..., min_length=1, description="عبارت جستجو"),
    category: Optional[str] = Query(None, description="فیلتر دسته‌بندی"),
    limit: int = Query(20, ge=1, le=200),
):
    items = poi_service.search_pois(q, category=category, limit=limit)
    return {
        "query": q,
        "category": category,
        "items": items,
        "total": len(items),
    }


@router.get("/nearby")
def nearby_pois(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: float = Query(5.0, gt=0, le=100),
    limit: int = Query(20, ge=1, le=200),
    category: Optional[str] = Query(None),
):
    items = poi_service.get_nearby_pois(
        lat=lat,
        lng=lng,
        category=category,
        radius=radius,
        limit=limit,
    )
    return {
        "location": {"lat": lat, "lng": lng},
        "radius": radius,
        "category": category,
        "results": items,
        "total": len(items),
    }


@router.get("/stats")
def pois_stats():
    return poi_service.get_stats()


@router.get("/nearby/stats")
def nearby_stats(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: float = Query(5.0, gt=0, le=100),
):
    return poi_service.get_nearby_stats(lat=lat, lng=lng, radius=radius)


@router.get("/category/{category}")
def pois_by_category(
    category: str = Path(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
):
    items = poi_service.get_pois_by_category(category=category, limit=limit)
    return {
        "category": category,
        "items": items,
        "total": len(items),
    }


@router.get("/city/{city}")
def pois_by_city(
    city: str = Path(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
):
    items = poi_service.get_pois_by_city(city=city, limit=limit)
    return {
        "city": city,
        "items": items,
        "total": len(items),
    }


@router.get("/{poi_id:int}")
def get_poi(poi_id: int):
    item = poi_service.get_poi_by_id(poi_id)
    if not item:
        raise HTTPException(status_code=404, detail="POI not found")
    return item
