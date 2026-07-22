from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import date
import logging

from app.repositories.camera_repository import CameraRepository
from app.models.camera import Camera
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class CameraService:
    """سرویس مدیریت دوربین‌ها"""

    def __init__(self, db: Session):
        self.db = db
        self.camera_repo = CameraRepository(db)

    def get_cameras(
        self,
        region: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Camera]:
        """دریافت دوربین‌ها با فیلتر"""
        if region and status:
            return self.camera_repo.get_all_by_field('region', region) or []

        if region:
            return self.camera_repo.get_by_region(region)

        if status:
            return self.camera_repo.get_by_status(status)

        return self.camera_repo.get_all(skip, limit)

    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """دریافت دوربین بر اساس شناسه"""
        return self.camera_repo.get_by_camera_id(camera_id)

    def get_active_cameras(self) -> List[Camera]:
        """دریافت دوربین‌های فعال"""
        return self.camera_repo.get_active_cameras()

    def get_cameras_by_type(self, camera_type: str) -> List[Camera]:
        """دریافت دوربین‌ها بر اساس نوع"""
        return self.camera_repo.get_cameras_by_type(camera_type)

    def create_camera(self, data: Dict) -> Camera:
        """ایجاد دوربین جدید"""
        camera = self.camera_repo.create(**data)
        logger.info(f"📹 دوربین جدید ایجاد شد: {camera.name} (ID: {camera.camera_id})")
        return camera

    def update_camera(self, camera_id: str, data: Dict) -> Optional[Camera]:
        """به‌روزرسانی دوربین"""
        camera = self.camera_repo.get_by_camera_id(camera_id)
        if not camera:
            raise NotFoundException(f"دوربین با شناسه {camera_id} یافت نشد")

        updated = self.camera_repo.update(camera.id, **data)
        logger.info(f"📹 دوربین به‌روزرسانی شد: {updated.name}")
        return updated

    def update_camera_status(self, camera_id: str, status: str) -> Optional[Camera]:
        """به‌روزرسانی وضعیت دوربین"""
        camera = self.camera_repo.get_by_camera_id(camera_id)
        if not camera:
            raise NotFoundException(f"دوربین با شناسه {camera_id} یافت نشد")

        camera.status = status
        self.db.commit()
        self.db.refresh(camera)
        logger.info(f"📹 وضعیت دوربین تغییر کرد: {camera.name} -> {status}")
        return camera

    def delete_camera(self, camera_id: str) -> bool:
        """حذف دوربین"""
        camera = self.camera_repo.get_by_camera_id(camera_id)
        if not camera:
            raise NotFoundException(f"دوربین با شناسه {camera_id} یافت نشد")

        self.camera_repo.delete(camera.id)
        logger.info(f"🗑️ دوربین حذف شد: {camera.name}")
        return True

    def get_camera_summary(self) -> Dict:
        """خلاصه اطلاعات دوربین‌ها"""
        return self.camera_repo.get_cameras_summary()

    def report_issue(self, camera_id: str, issue: str) -> bool:
        """گزارش مشکل دوربین"""
        camera = self.camera_repo.get_by_camera_id(camera_id)
        if not camera:
            raise NotFoundException(f"دوربین با شناسه {camera_id} یافت نشد")

        # در صورت نیاز می‌توان جدول جداگانه برای گزارش‌ها ایجاد کرد
        logger.info(f"🐛 گزارش مشکل برای دوربین {camera.name}: {issue}")
        return True

    def get_nearby_cameras(
        self,
        latitude: float,
        longitude: float,
        radius: float = 5.0
    ) -> List[Dict]:
        """دریافت دوربین‌های نزدیک"""
        cameras = self.camera_repo.get_active_cameras()

        from app.services.location_service import LocationService
        loc_service = LocationService(self.db)

        results = []
        for camera in cameras:
            distance = loc_service.calculate_distance(
                latitude, longitude,
                camera.latitude, camera.longitude
            )

            if distance <= radius:
                results.append({
                    "id": camera.id,
                    "camera_id": camera.camera_id,
                    "name": camera.name,
                    "region": camera.region,
                    "latitude": camera.latitude,
                    "longitude": camera.longitude,
                    "types": camera.types,
                    "status": camera.status,
                    "distance": round(distance, 2)
                })

        return sorted(results, key=lambda x: x['distance'])
