# ============================================================
# orchestrator.py - هماهنگ‌کننده هوشمند سرویس‌ها
# ============================================================
import os
import logging
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

DB_PATH = "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"


class OrchestratorRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None
    location: Optional[Dict[str, float]] = None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.post("/chat")
async def orchestrator_chat(payload: OrchestratorRequest):
    """هماهنگ‌کننده هوشمند — انتخاب بهترین سرویس"""
    try:
        msg = payload.message.lower()

        # تشخیص نیت و هدایت به سرویس مناسب
        if any(k in msg for k in ["ترافیک", "جاده", "مسیر", "راه", "شلوغی"]):
            return {
                "service": "routing",
                "action": "get_traffic",
                "message": "در حال دریافت وضعیت ترافیک...",
                "redirect_to": "/api/v1/routing/directions"
            }

        elif any(k in msg for k in ["هتل", "غذا", "رستوران", "گردشگری", "جاذبه", "تفریح"]):
            return {
                "service": "tourism",
                "action": "search_poi",
                "message": "در حال جستجوی اطلاعات گردشگری...",
                "redirect_to": "/api/v1/copilot/message"
            }

        elif any(k in msg for k in ["بندرعباس", "شهر", "جمعیت", "مساحت"]):
            conn = get_db()
            cursor = conn.execute("SELECT * FROM city_info LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            return {
                "service": "city_info",
                "data": dict(row) if row else {},
                "message": "اطلاعات شهر بندرعباس"
            }

        elif any(k in msg for k in ["بندری", "گویش", "لهجه", "ضرب المثل"]):
            return {
                "service": "bandari",
                "action": "search_dialect",
                "message": "در حال جستجوی گویش بندری...",
                "redirect_to": "/api/v1/copilot/message"
            }

        elif any(k in msg for k in ["هوا", "آب و هوا", "دما", "باران"]):
            return {
                "service": "weather",
                "action": "get_weather",
                "message": "در حال دریافت وضعیت آب و هوا...",
                "redirect_to": "/api/v1/weather/current"
            }

        else:
            # پیش‌فرض: Copilot
            return {
                "service": "copilot",
                "action": "general_query",
                "message": "در حال پردازش درخواست شما...",
                "redirect_to": "/api/v1/copilot/message"
            }

    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def orchestrator_status():
    """وضعیت سرویس Orchestrator"""
    return {
        "status": "active",
        "service": "orchestrator",
        "available_services": ["routing", "tourism", "city_info", "bandari", "weather", "copilot"],
        "database": DB_PATH,
        "database_exists": os.path.exists(DB_PATH)
    }
