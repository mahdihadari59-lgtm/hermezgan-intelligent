from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
from app.models.hotspot import Hotspot
from app.repositories.base_repository import BaseRepository
import math


class HotspotRepository(BaseRepository[Hotspot]):
    """Repository برای مدیریت نقاط حادثه‌خیز"""

    def __init__(self, db: Session):
        super().__init__(Hotspot, db)

    def get_by_type(self, hotspot_type: str) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز بر اساس نوع"""
        return self.db.query(Hotspot).filter(Hotspot.type == hotspot_type).all()

    def get_by_severity(self, severity: str) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز بر اساس شدت"""
        return self.db.query(Hotspot).filter(Hotspot.severity == severity).all()

    def get_active_hotspots(self) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز فعال"""
        return self.db.query(Hotspot).filter(Hotspot.status == 'active').all()

    def get_nearby_hotspots(
        self,
        latitude: float,
        longitude: float,
        radius: float = 5.0,
        limit: int = 20
    ) -> List[Dict]:
        """دریافت نقاط حادثه‌خیز نزدیک"""
        hotspots = self.db.query(Hotspot).filter(Hotspot.status == 'active').all()

        results = []
        for hotspot in hotspots:
            distance = self._calculate_distance(
                latitude, longitude,
                float(hotspot.latitude), float(hotspot.longitude)
            )

            if distance <= radius:
                results.append({
                    "id": hotspot.id,
                    "type": hotspot.type,
                    "latitude": float(hotspot.latitude),
                    "longitude": float(hotspot.longitude),
                    "title": hotspot.title,
                    "description": hotspot.description,
                    "severity": hotspot.severity,
                    "status": hotspot.status,
                    "reported_at": hotspot.reported_at.isoformat() if hotspot.reported_at else None,
                    "distance": round(distance, 2)
                })

        return sorted(results, key=lambda x: x['distance'])[:limit]

    def get_hotspots_summary(self) -> Dict:
        """خلاصه اطلاعات نقاط حادثه‌خیز"""
        types = self.db.query(
            Hotspot.type,
            func.count(Hotspot.id).label('count')
        ).filter(Hotspot.status == 'active').group_by(Hotspot.type).all()

        severities = self.db.query(
            Hotspot.severity,
            func.count(Hotspot.id).label('count')
        ).filter(Hotspot.status == 'active').group_by(Hotspot.severity).all()

        return {
            "total": self.db.query(Hotspot).filter(Hotspot.status == 'active').count(),
            "by_type": [{"type": t[0], "count": t[1]} for t in types],
            "by_severity": [{"severity": s[0], "count": s[1]} for s in severities],
            "recent": self.db.query(Hotspot).filter(
                Hotspot.status == 'active'
            ).order_by(Hotspot.reported_at.desc()).limit(10).all()
        }

    def resolve_hotspot(self, hotspot_id: int) -> Optional[Hotspot]:
        """حل کردن نقطه حادثه‌خیز (تغییر وضعیت به resolved)"""
        return self.update(hotspot_id, status='resolved', updated_at=datetime.utcnow())

    def get_critical_hotspots(self) -> List[Hotspot]:
        """دریافت نقاط حادثه‌خیز بحرانی (شدت بالا)"""
        return self.db.query(Hotspot).filter(
            and_(
                Hotspot.status == 'active',
                Hotspot.severity == 'high'
            )
        ).order_by(Hotspot.reported_at.desc()).all()

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """محاسبه فاصله دو نقطه (Haversine)"""
        lon1, lat1, lon2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        km = 6371 * c
        return km
