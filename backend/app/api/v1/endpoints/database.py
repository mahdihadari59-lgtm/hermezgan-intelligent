from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional, List
import json

from app.core.database import get_db
from app.models.hormozgan import Market, Healthcare, Education, City

router = APIRouter(prefix="/db", tags=["Database"])

@router.get("/markets/nearby")
async def get_nearby_markets(
    lat: float,
    lon: float,
    radius: float = 5.0,
    limit: int = 50,
    city: Optional[str] = None,
    shop_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    دریافت فروشگاه‌های نزدیک به یک نقطه
    """
    query = db.query(Market)
    
    # فیلتر بر اساس فاصله (محاسبه تقریبی)
    query = query.filter(
        (Market.lat - lat) * (Market.lat - lat) + 
        (Market.lon - lon) * (Market.lon - lon) < (radius / 111) ** 2
    )
    
    if city:
        query = query.filter(Market.city == city)
    if shop_type:
        query = query.filter(Market.shop_type == shop_type)
    
    results = query.limit(limit).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": m.id,
                "name": m.name_fa or m.name,
                "type": m.shop_type,
                "lat": m.lat,
                "lng": m.lon,
                "city": m.city,
                "phone": m.phone,
                "distance": ((m.lat - lat) ** 2 + (m.lon - lon) ** 2) ** 0.5 * 111
            }
            for m in results
        ]
    }

@router.get("/markets/cities")
async def get_city_markets(
    city: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """دریافت تمام فروشگاه‌های یک شهر"""
    results = db.query(Market).filter(Market.city == city).limit(limit).all()
    
    return {
        "status": "success",
        "city": city,
        "total": len(results),
        "data": [
            {
                "id": m.id,
                "name": m.name_fa or m.name,
                "type": m.shop_type,
                "lat": m.lat,
                "lng": m.lon,
                "brand": m.brand
            }
            for m in results
        ]
    }

@router.get("/healthcare/hospitals")
async def get_hospitals(
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """دریافت لیست بیمارستان‌ها"""
    query = db.query(Healthcare).filter(Healthcare.healthcare_type == 'hospital')
    if city:
        query = query.filter(Healthcare.city == city)
    
    results = query.all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": h.id,
                "name": h.name_fa,
                "lat": h.lat,
                "lng": h.lon,
                "city": h.city,
                "phone": h.phone
            }
            for h in results
        ]
    }

@router.get("/education/schools")
async def get_schools(
    city: Optional[str] = None,
    edu_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """دریافت لیست مدارس"""
    query = db.query(Education)
    if city:
        query = query.filter(Education.city == city)
    if edu_type:
        query = query.filter(Education.edu_type == edu_type)
    
    results = query.limit(100).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": e.id,
                "name": e.name_fa,
                "type": e.edu_type,
                "lat": e.lat,
                "lng": e.lon,
                "city": e.city
            }
            for e in results
        ]
    }

@router.get("/stats")
async def get_db_stats(db: Session = Depends(get_db)):
    """آمار کلی دیتابیس"""
    tables = ["markets", "healthcare", "education", "roads", "offices", "transport", "cities"]
    stats = {}
    
    for table in tables:
        count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        stats[table] = count
    
    # شهرهای دارای بیشترین فروشگاه
    top_cities = db.execute(
        text("SELECT city, COUNT(*) as count FROM markets GROUP BY city ORDER BY count DESC LIMIT 10")
    ).all()
    
    return {
        "status": "success",
        "total_records": sum(stats.values()),
        "table_counts": stats,
        "top_cities": [{"city": c[0], "count": c[1]} for c in top_cities]
    }

@router.get("/geojson/markets")
async def get_markets_geojson(
    city: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """خروجی GeoJSON برای نقشه"""
    query = db.query(Market)
    if city:
        query = query.filter(Market.city == city)
    
    results = query.limit(limit).all()
    
    features = []
    for m in results:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [m.lon, m.lat]
            },
            "properties": {
                "id": m.id,
                "name": m.name_fa or m.name,
                "type": m.shop_type,
                "city": m.city,
                "brand": m.brand
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
