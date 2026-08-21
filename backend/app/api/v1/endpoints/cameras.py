from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/cameras", tags=["Cameras"])

# داده‌های نمونه دوربین‌ها
MOCK_CAMERAS = [
    {
        "id": "ba-001",
        "name": "چهارراه غزی",
        "region": "bandar-abbas",
        "lat": 27.2158,
        "lng": 56.2808,
        "types": ["traffic-light", "speed"],
        "status": "active",
        "installed": "۱۴۰۳/۰۶/۱۵"
    },
    {
        "id": "ba-002",
        "name": "میدان سپاه",
        "region": "bandar-abbas",
        "lat": 27.2200,
        "lng": 56.2850,
        "types": ["traffic-light"],
        "status": "active",
        "installed": "۱۴۰۳/۰۶/۱۰"
    },
    {
        "id": "ba-003",
        "name": "بلوار امام خمینی",
        "region": "bandar-abbas",
        "lat": 27.2180,
        "lng": 56.2750,
        "types": ["speed"],
        "status": "active",
        "installed": "۱۴۰۳/۰۷/۰۱"
    },
    {
        "id": "ba-004",
        "name": "پل خواجو",
        "region": "bandar-abbas",
        "lat": 27.2250,
        "lng": 56.2900,
        "types": ["speed", "plate"],
        "status": "installing",
        "installed": "۱۴۰۵/۰۶/۰۵"
    },
    {
        "id": "ba-005",
        "name": "بلوار هرمز (هدیش)",
        "region": "bandar-abbas",
        "lat": 27.2100,
        "lng": 56.2700,
        "types": ["speed", "night-ir"],
        "status": "pending",
        "priority": "urgent"
    }
]

@router.get("/")
async def get_cameras(
    region: Optional[str] = Query(None, description="منطقه"),
    status: Optional[str] = Query(None, description="وضعیت"),
    limit: int = Query(50, description="تعداد نتایج")
):
    """دریافت لیست دوربین‌ها"""
    
    results = MOCK_CAMERAS.copy()
    
    if region:
        results = [c for c in results if c["region"] == region]
    
    if status:
        results = [c for c in results if c["status"] == status]
    
    return {
        "cameras": results[:limit],
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    """دریافت اطلاعات یک دوربین"""
    
    camera = next((c for c in MOCK_CAMERAS if c["id"] == camera_id), None)
    if not camera:
        raise HTTPException(status_code=404, detail="دوربین یافت نشد")
    
    return camera

@router.post("/{camera_id}/report")
async def report_camera_issue(
    camera_id: str,
    issue: str
):
    """گزارش مشکل دوربین"""
    
    camera = next((c for c in MOCK_CAMERAS if c["id"] == camera_id), None)
    if not camera:
        raise HTTPException(status_code=404, detail="دوربین یافت نشد")
    
    return {
        "status": "reported",
        "camera_id": camera_id,
        "issue": issue,
        "timestamp": datetime.utcnow().isoformat()
    }
