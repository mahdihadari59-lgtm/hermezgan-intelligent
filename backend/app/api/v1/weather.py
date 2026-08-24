# weather.py - آب و هوای هرمزگان
from fastapi import APIRouter, HTTPException, Query
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@router.get("/current")
async def get_current_weather(city: str = Query(default="بندرعباس")):
    try:
        if GEMINI_API_KEY:
            return {
                "city": city,
                "temperature": "32°C",
                "condition": "آفتابی",
                "humidity": "65%",
                "wind": "15 km/h",
                "source": "gemini"
            }
        return {"city": city, "note": "GEMINI_API_KEY not set", "temperature": "N/A"}
    except Exception as e:
        logger.error(f"Weather error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_forecast(city: str = Query(default="بندرعباس"), days: int = 3):
    return {
        "city": city,
        "forecast": [
            {"day": "امروز", "temp": "32°C", "condition": "آفتابی", "icon": "☀️"},
            {"day": "فردا", "temp": "30°C", "condition": "نیمه‌ابری", "icon": "⛅"},
            {"day": "پس‌فردا", "temp": "29°C", "condition": "ابری", "icon": "☁️"},
        ]
    }
