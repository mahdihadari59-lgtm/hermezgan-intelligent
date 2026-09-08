from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.location import Service
from app.repositories.base_repository import BaseRepository
import math


class ServiceRepository(BaseRepository[Service]):
    """Repository برای مدیریت خدمات"""

    def __init__(self, db: Session):
        super().__init__(Service, db)

    def get_by_type(self, service_type: str, skip: int = 0, limit: int = 100) -> List[Service]:
        """دریافت خدمات بر اساس نوع"""
        return self.db.query(Service).filter(
            Service.type == service_type,
            Service.status == 'active'
        ).offset(skip).limit(limit).all()

    def get_nearby_services(
        self,
        latitude: float,
        longitude: float,
        service_type: Optional[str] = None,
        radius: float = 5.0,
        limit: int = 20
    ) -> List[Dict]:
        """دریافت خدمات نزدیک"""
        query = self.db.query(Service).filter(Service.status == 'active')

        if service_type:
            query = query.filter(Service.type == service_type)

        services = query.all()

        results = []
        for service in services:
            distance = self._calculate_distance(
                latitude, longitude,
                float(service.latitude), float(service.longitude)
            )

            if distance <= radius:
                results.append({
                    "id": service.id,
                    "name": service.name,
                    "type": service.type,
                    "latitude": float(service.latitude),
                    "longitude": float(service.longitude),
                    "address": service.address,
                    "phone": service.phone,
                    "rating": service.rating,
                    "distance": round(distance, 2)
                })

        return sorted(results, key=lambda x: x['distance'])[:limit]

    def search_services(self, query: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> List[Dict]:
        """جستجوی خدمات"""
        search_query = self.db.query(Service).filter(
            and_(
                Service.status == 'active',
                or_(
                    Service.name.ilike(f"%{query}%"),
                    Service.address.ilike(f"%{query}%"),
                    Service.type.ilike(f"%{query}%"),
                    Service.description.ilike(f"%{query}%")
                )
            )
        )

        results = []
        for service in search_query.all():
            item = {
                "id": service.id,
                "name": service.name,
                "type": service.type,
                "latitude": float(service.latitude),
                "longitude": float(service.longitude),
                "address": service.address,
                "phone": service.phone,
                "rating": service.rating
            }

            if latitude and longitude:
                item["distance"] = round(self._calculate_distance(
                    latitude, longitude,
                    float(service.latitude), float(service.longitude)
                ), 2)

            results.append(item)

        if latitude and longitude:
            return sorted(results, key=lambda x: x.get('distance', float('inf')))
        return results

    def get_top_rated(self, limit: int = 10) -> List[Service]:
        """دریافت خدمات با بالاترین امتیاز"""
        return self.db.query(Service).filter(
            Service.status == 'active'
        ).order_by(Service.rating.desc()).limit(limit).all()

    def get_service_types(self) -> List[Dict]:
        """دریافت انواع خدمات با تعداد"""
        types = self.db.query(
            Service.type,
            func.count(Service.id).label('count')
        ).filter(Service.status == 'active').group_by(Service.type).all()

        return [{"type": t[0], "count": t[1]} for t in types]

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """محاسبه فاصله دو نقطه (Haversine)"""
        lon1, lat1, lon2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        km = 6371 * c
        return km
