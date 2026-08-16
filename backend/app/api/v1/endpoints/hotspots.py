from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/hotspots", tags=["Hotspots"])

# داده‌های نمونه نقاط حادثه‌خیز
MOCK_HOTSPOTS = [
    {
        "id": 101,
        "type": "accident",
        "lat": 27.2200,
        "lng": 56.2850,
        "title": "تصادف در تقاطع خیابان شهید رجایی",
        "description": "تصادف بین دو خودرو - ترافیک سنگین",
        "severity": "high",
        "status": "active",
        "reported_by": "پلیس راهور",
        "reported_at": datetime.utcnow().isoformat()
    },
    {
        "id": 102,
        "type": "traffic",
        "lat": 27.2180,
        "lng": 56.2750,
        "title": "ترافیک سنگین خیابان ولیعصر",
        "description": "ترافیک بسیار سنگین - زمان انتظار ۳۰ دقیقه",
        "severity": "medium",
        "status": "active",
        "reported_by": "سیستم ترافیکی",
        "reported_at": datetime.utcnow().isoformat()
    },
    {
        "id": 103,
        "type": "danger",
        "lat": 27.2250,
        "lng": 56.2900,
        "title": "منطقه خطرناک - رانندگان پرسرعت",
        "description": "رانندگان با سرعت بالا - عدم رعایت علائم",
        "severity": "high",
        "status": "active",
        "reported_by": "پلیس راهور",
        "reported_at": datetime.utcnow().isoformat()
    }
]

@router.get("/")
async def get_hotspots(
    type: Optional[str] = Query(None, description="نوع حادثه"),
    severity: Optional[str] = Query(None, description="شدت"),
    limit: int = Query(50, description="تعداد نتایج")
):
    """دریافت نقاط حادثه‌خیز"""
    
    results = MOCK_HOTSPOTS.copy()
    
    if type:
        results = [h for h in results if h["type"] == type]
    
    if severity:
        results = [h for h in results if h["severity"] == severity]
    
    return {
        "hotspots": results[:limit],
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/nearby")
async def get_nearby_hotspots(
    lat: float = Query(..., description="عرض جغرافیایی"),
    lng: float = Query(..., description="طول جغرافیایی"),
    radius: float = Query(5.0, description="شعاع جستجو")
):
    """نقاط حادثه‌خیز نزدیک"""
    
    from math import radians, sin, cos, sqrt, asin
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c
    
    results = []
    for hotspot in MOCK_HOTSPOTS:
        dist = haversine(lat, lng, hotspot["lat"], hotspot["lng"])
        if dist <= radius:
            results.append({**hotspot, "distance": round(dist, 2)})
    
    return {
        "hotspots": sorted(results, key=lambda x: x["distance"]),
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/report")
async def report_hotspot(
    type: str,
    lat: float,
    lng: float,
    title: str,
    description: str,
    severity: str = "medium"
):
    """گزارش نقطه حادثه‌خیز جدید"""
    
    new_hotspot = {
        "id": max([h["id"] for h in MOCK_HOTSPOTS]) + 1,
        "type": type,
        "lat": lat,
        "lng": lng,
        "title": title,
        "description": description,
        "severity": severity,
        "status": "active",
        "reported_by": "کاربر",
        "reported_at": datetime.utcnow().isoformat()
    }
    
    MOCK_HOTSPOTS.append(new_hotspot)
    
    return {
        "status": "reported",
        "hotspot": new_hotspot,
        "timestamp": datetime.utcnow().isoformat()
    }
