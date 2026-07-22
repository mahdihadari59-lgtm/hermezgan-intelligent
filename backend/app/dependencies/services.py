from sqlalchemy.orm import Session
from typing import Optional
import redis

from app.services.chat_service import ChatService
from app.services.nlp_service import NLPService
from app.services.location_service import LocationService
from app.services.camera_service import CameraService
from app.services.hotspot_service import HotspotService
from app.services.analytics_service import AnalyticsService
from app.dependencies.database import get_db, get_redis


# ============================================================
# Chat Service
# ============================================================

def get_chat_service(
    db: Session = Depends(get_db),
    redis_client: Optional[redis.Redis] = Depends(get_redis)
) -> ChatService:
    """
    دریافت سرویس چت‌بات

    Returns:
        ChatService: سرویس چت‌بات
    """
    return ChatService(db, redis_client)


# ============================================================
# NLP Service
# ============================================================

def get_nlp_service(
    db: Session = Depends(get_db)
) -> NLPService:
    """
    دریافت سرویس NLP

    Returns:
        NLPService: سرویس پردازش زبان طبیعی
    """
    return NLPService(db)


# ============================================================
# Location Service
# ============================================================

def get_location_service(
    db: Session = Depends(get_db)
) -> LocationService:
    """
    دریافت سرویس مکان‌یابی

    Returns:
        LocationService: سرویس مکان‌یابی
    """
    return LocationService(db)


# ============================================================
# Camera Service
# ============================================================

def get_camera_service(
    db: Session = Depends(get_db)
) -> CameraService:
    """
    دریافت سرویس دوربین‌ها

    Returns:
        CameraService: سرویس دوربین‌ها
    """
    return CameraService(db)


# ============================================================
# Hotspot Service
# ============================================================

def get_hotspot_service(
    db: Session = Depends(get_db)
) -> HotspotService:
    """
    دریافت سرویس نقاط حادثه‌خیز

    Returns:
        HotspotService: سرویس نقاط حادثه‌خیز
    """
    return HotspotService(db)


# ============================================================
# Analytics Service
# ============================================================

def get_analytics_service(
    db: Session = Depends(get_db)
) -> AnalyticsService:
    """
    دریافت سرویس تحلیل داده‌ها

    Returns:
        AnalyticsService: سرویس تحلیل
    """
    return AnalyticsService(db)
