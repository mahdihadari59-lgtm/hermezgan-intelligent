from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.camera import Camera
from app.repositories.base_repository import BaseRepository


class CameraRepository(BaseRepository[Camera]):
    """Repository برای مدیریت دوربین‌ها"""

    def __init__(self, db: Session):
        super().__init__(Camera, db)

    def get_by_region(self, region: str) -> List[Camera]:
        """دریافت دوربین‌های یک منطقه"""
        return self.db.query(Camera).filter(Camera.region == region).all()

    def get_by_status(self, status: str) -> List[Camera]:
        """دریافت دوربین‌ها بر اساس وضعیت"""
        return self.db.query(Camera).filter(Camera.status == status).all()

    def get_by_camera_id(self, camera_id: str) -> Optional[Camera]:
        """دریافت دوربین بر اساس شناسه دوربین"""
        return self.db.query(Camera).filter(Camera.camera_id == camera_id).first()

    def get_active_cameras(self) -> List[Camera]:
        """دریافت دوربین‌های فعال"""
        return self.db.query(Camera).filter(Camera.status == 'active').all()

    def get_cameras_with_priority(self, priority: str) -> List[Camera]:
        """دریافت دوربین‌های با اولویت مشخص"""
        return self.db.query(Camera).filter(Camera.priority == priority).all()

    def get_cameras_by_type(self, camera_type: str) -> List[Camera]:
        """دریافت دوربین‌ها بر اساس نوع"""
        from sqlalchemy import text
        return self.db.query(Camera).filter(
            text(f"'{camera_type}' = ANY(types)")
        ).all()

    def get_cameras_summary(self) -> Dict:
        """خلاصه اطلاعات دوربین‌ها"""
        regions = self.db.query(
            Camera.region,
            func.count(Camera.id).label('total'),
            func.sum(func.case((Camera.status == 'active', 1), else_=0)).label('active'),
            func.sum(func.case((Camera.status == 'installing', 1), else_=0)).label('installing'),
            func.sum(func.case((Camera.status == 'pending', 1), else_=0)).label('pending')
        ).group_by(Camera.region).all()

        return {
            "total": self.count(),
            "active": self.db.query(Camera).filter(Camera.status == 'active').count(),
            "installing": self.db.query(Camera).filter(Camera.status == 'installing').count(),
            "pending": self.db.query(Camera).filter(Camera.status == 'pending').count(),
            "regions": [
                {
                    "region": r[0],
                    "total": r[1],
                    "active": r[2] or 0,
                    "installing": r[3] or 0,
                    "pending": r[4] or 0
                } for r in regions
            ]
        }

    def update_status(self, camera_id: str, status: str) -> Optional[Camera]:
        """به‌روزرسانی وضعیت دوربین"""
        camera = self.get_by_camera_id(camera_id)
        if camera:
            camera.status = status
            self.db.commit()
            self.db.refresh(camera)
        return camera

    def report_issue(self, camera_id: str, issue: str) -> bool:
        """ثبت گزارش مشکل برای دوربین"""
        camera = self.get_by_camera_id(camera_id)
        if camera:
            return True
        return False
