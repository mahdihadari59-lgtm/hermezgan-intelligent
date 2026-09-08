# app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Query
from typing import Optional, List

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/stats")
async def get_stats():
    """دریافت آمار کلی"""
    return {
        "totalUsers": 1234,
        "activeUsers": 856,
        "totalServices": 567,
        "completedQueries": 3421,
        "hotspots": 45,
        "cameras": 58
    }

@router.get("/user-growth")
async def get_user_growth(
    time_filter: str = "weekly"
):
    """دریافت رشد کاربران"""
    data = {
        "daily": [
            {"date": "امروز", "users": 45, "queries": 120},
            {"date": "دیروز", "users": 38, "queries": 98}
        ],
        "weekly": [
            {"date": "شنبه", "users": 120, "queries": 240},
            {"date": "یکشنبه", "users": 132, "queries": 221},
            {"date": "دوشنبه", "users": 101, "queries": 229},
            {"date": "سه‌شنبه", "users": 165, "queries": 200},
            {"date": "چهارشنبه", "users": 203, "queries": 214},
            {"date": "پنجشنبه", "users": 176, "queries": 257},
            {"date": "جمعه", "users": 195, "queries": 290}
        ],
        "monthly": [
            {"date": "هفته ۱", "users": 450, "queries": 890},
            {"date": "هفته ۲", "users": 520, "queries": 950},
            {"date": "هفته ۳", "users": 480, "queries": 920},
            {"date": "هفته ۴", "users": 560, "queries": 1050}
        ]
    }
    return {"data": data.get(time_filter, data["weekly"])}

@router.get("/service-distribution")
async def get_service_distribution():
    """دریافت توزیع خدمات"""
    return {
        "distribution": [
            {"name": "بیمارستان‌ها", "value": 156, "color": "#ff4757"},
            {"name": "رستوران‌ها", "value": 234, "color": "#ffa502"},
            {"name": "تاکسی‌ها", "value": 98, "color": "#2ed573"},
            {"name": "داروخانه‌ها", "value": 67, "color": "#1e90ff"},
            {"name": "مدارس", "value": 45, "color": "#9b59b6"}
        ]
    }

@router.get("/activities")
async def get_recent_activities(limit: int = 10):
    """دریافت فعالیت‌های اخیر"""
    activities = [
        {"id": 1, "user": "علی محمدی", "action": "جستجوی بیمارستان", "timestamp": "۱۰ دقیقه پیش", "status": "موفق"},
        {"id": 2, "user": "فاطمه احمدی", "action": "درخواست مسیریابی", "timestamp": "۲۵ دقیقه پیش", "status": "موفق"},
        {"id": 3, "user": "محمد علی", "action": "جستجوی رستوران", "timestamp": "۴۵ دقیقه پیش", "status": "موفق"},
        {"id": 4, "user": "زهرا کریمی", "action": "درخواست تاکسی", "timestamp": "۱ ساعت پیش", "status": "درحال انجام"}
    ]
    return {"activities": activities[:limit]}
