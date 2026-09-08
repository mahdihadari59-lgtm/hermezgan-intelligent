# app/api/v1/endpoints/traffic.py
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
import random

router = APIRouter(prefix="/traffic", tags=["Traffic"])

TRAFFIC_DATA = [
    {
        "lat": 27.2158,
        "lng": 56.2808,
        "name": "چهارراه غزی",
        "level": "heavy",
        "speed": 8,
        "delay": 15,
        "timestamp": datetime.now().isoformat()
    },
    {
        "lat": 27.2200,
        "lng": 56.2850,
        "name": "میدان سپاه",
        "level": "heavy",
        "speed": 10,
        "delay": 12,
        "timestamp": datetime.now().isoformat()
    },
    {
        "lat": 27.2180,
        "lng": 56.2750,
        "name": "بلوار امام خمینی",
        "level": "medium",
        "speed": 25,
        "delay": 8,
        "timestamp": datetime.now().isoformat()
    },
    {
        "lat": 27.2250,
        "lng": 56.2900,
        "name": "پل خواجو",
        "level": "light",
        "speed": 40,
        "delay": 3,
        "timestamp": datetime.now().isoformat()
    },
    {
        "lat": 27.2100,
        "lng": 56.2700,
        "name": "سه‌راه ایسین",
        "level": "heavy",
        "speed": 5,
        "delay": 20,
        "timestamp": datetime.now().isoformat()
    },
    {
        "lat": 27.2300,
        "lng": 56.2700,
        "name": "بلوار هرمز (هدیش)",
        "level": "medium",
        "speed": 20,
        "delay": 10,
        "timestamp": datetime.now().isoformat()
    }
]

@router.get("/")
async def get_traffic(limit: int = 50):
    return {"status": "success", "data": TRAFFIC_DATA[:limit], "total": len(TRAFFIC_DATA)}

@router.post("/report")
async def report_traffic(location: str, severity: str, description: str):
    report_id = random.randint(1000, 9999)
    return {"status": "success", "message": "گزارش ثبت شد", "report_id": report_id}
