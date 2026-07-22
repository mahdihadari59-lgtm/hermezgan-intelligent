from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.camera_repository import CameraRepository
from app.repositories.hotspot_repository import HotspotRepository
from app.dependencies.database import get_db


# ============================================================
# User Repository
# ============================================================

def get_user_repository(
    db: Session = Depends(get_db)
) -> UserRepository:
    """
    دریافت Repository کاربران

    Returns:
        UserRepository: Repository کاربران
    """
    return UserRepository(db)


# ============================================================
# Chat Repository
# ============================================================

def get_chat_repository(
    db: Session = Depends(get_db)
) -> ChatRepository:
    """
    دریافت Repository چت

    Returns:
        ChatRepository: Repository چت
    """
    return ChatRepository(db)


# ============================================================
# Service Repository
# ============================================================

def get_service_repository(
    db: Session = Depends(get_db)
) -> ServiceRepository:
    """
    دریافت Repository خدمات

    Returns:
        ServiceRepository: Repository خدمات
    """
    return ServiceRepository(db)


# ============================================================
# Camera Repository
# ============================================================

def get_camera_repository(
    db: Session = Depends(get_db)
) -> CameraRepository:
    """
    دریافت Repository دوربین‌ها

    Returns:
        CameraRepository: Repository دوربین‌ها
    """
    return CameraRepository(db)


# ============================================================
# Hotspot Repository
# ============================================================

def get_hotspot_repository(
    db: Session = Depends(get_db)
) -> HotspotRepository:
    """
    دریافت Repository نقاط حادثه‌خیز

    Returns:
        HotspotRepository: Repository نقاط حادثه‌خیز
    """
    return HotspotRepository(db)
