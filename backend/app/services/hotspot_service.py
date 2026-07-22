from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.repositories.hotspot_repository import HotspotRepository
from app.models.hotspot import Hotspot
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class HotspotService:
    """سرویس مدیریت نقاط حادثه‌خیز"""

    def __init__(self, db: Session):
        self.db = db
        self.hotspot_repo = HotspotRepository(db)

    def get_hotspots(
        self,
        hotspot_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: str = "active",
        skip: int = 0,
        limit: int = 100
    ) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز با فیلتر"""
        query = self.db.query(Hotspot)

        if status:
            query = query.filter(Hotspot.status == status)

        if hotspot_type:
            query = query.filter(Hotspot.type == hotspot_type)

        if severity:
            query = query.filter(Hotspot.severity == severity)

        return query.offset(skip).limit(limit).all()

    def get_hotspot(self, hotspot_id: int) -> Optional[Hotspot]:
        """دریافت نقطه حادثه‌خیز"""
        return self.hotspot_repo.get_by_id(hotspot_id)

    def get_active_hotspots(self) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز فعال"""
        return self.hotspot_repo.get_active_hotspots()

    def get_critical_hotspots(self) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز بحرانی"""
        return self.hotspot_repo.get_critical_hotspots()

    def get_nearby_hotspots(
        self,
        latitude: float,
        longitude: float,
        radius: float = 5.0,
        limit: int = 20
    ) -> List[Dict]:
        """دریافت نقاط حادثه‌خیز نزدیک"""
        return self.hotspot_repo.get_nearby_hotspots(
            latitude, longitude, radius, limit
        )

    def create_hotspot(self, data: Dict) -> Hotspot:
        """ایجاد نقطه حادثه‌خیز جدید"""
        hotspot = self.hotspot_repo.create(**data)
        logger.info(f"🚨 نقطه حادثه‌خیز جدید: {hotspot.title} (ID: {hotspot.id})")
        return hotspot

    def update_hotspot(self, hotspot_id: int, data: Dict) -> Optional[Hotspot]:
        """به‌روزرسانی نقطه حادثه‌خیز"""
        hotspot = self.hotspot_repo.get_by_id(hotspot_id)
        if not hotspot:
            raise NotFoundException(f"نقطه حادثه‌خیز با شناسه {hotspot_id} یافت نشد")

        updated = self.hotspot_repo.update(hotspot_id, **data)
        logger.info(f"🔄 نقطه حادثه‌خیز به‌روزرسانی شد: {updated.title}")
        return updated

    def resolve_hotspot(self, hotspot_id: int) -> Optional[Hotspot]:
        """حل کردن نقطه حادثه‌خیز"""
        hotspot = self.hotspot_repo.get_by_id(hotspot_id)
        if not hotspot:
            raise NotFoundException(f"نقطه حادثه‌خیز با شناسه {hotspot_id} یافت نشد")

        hotspot.status = "resolved"
        hotspot.resolved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(hotspot)

        logger.info(f"✅ نقطه حادثه‌خیز حل شد: {hotspot.title}")
        return hotspot

    def delete_hotspot(self, hotspot_id: int) -> bool:
        """حذف نقطه حادثه‌خیز"""
        hotspot = self.hotspot_repo.get_by_id(hotspot_id)
        if not hotspot:
            raise NotFoundException(f"نقطه حادثه‌خیز با شناسه {hotspot_id} یافت نشد")

        self.hotspot_repo.delete(hotspot_id)
        logger.info(f"🗑️ نقطه حادثه‌خیز حذف شد: {hotspot.title}")
        return True

    def get_hotspot_summary(self) -> Dict:
        """خلاصه اطلاعات نقاط حادثه‌خیز"""
        return self.hotspot_repo.get_hotspots_summary()

    def get_hotspots_by_severity(self, severity: str) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز بر اساس شدت"""
        return self.hotspot_repo.get_by_severity(severity)
