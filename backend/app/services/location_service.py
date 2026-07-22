from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import math
import logging

from app.repositories.service_repository import ServiceRepository
from app.models.location import Service
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class LocationService:
    """سرویس مکان‌یابی و خدمات"""

    def __init__(self, db: Session):
        self.db = db
        self.service_repo = ServiceRepository(db)

    def find_nearby_services(
        self,
        service_type: str,
        latitude: Optional[float],
        longitude: Optional[float],
        radius: float = 5.0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        یافتن خدمات نزدیک

        Args:
            service_type: نوع سرویس
            latitude: عرض جغرافیایی
            longitude: طول جغرافیایی
            radius: شعاع جستجو (کیلومتر)
            limit: تعداد نتایج

        Returns:
            Dict: پاسخ شامل خدمات و پیشنهادات
        """
        if not latitude or not longitude:
            return {
                "response": "📍 لطفاً موقعیت خود را به اشتراک بگذارید تا بتوانم نزدیک‌ترین خدمات را پیدا کنم.",
                "suggestions": ["📍 اشتراک موقعیت", "🏥 جستجوی دستی"],
                "services": []
            }

        services = self.service_repo.get_nearby_services(
            latitude=latitude,
            longitude=longitude,
            service_type=service_type,
            radius=radius,
            limit=limit
        )

        if not services:
            service_name = self._get_service_name(service_type)
            return {
                "response": f"❌ هیچ {service_name} در شعاع {radius} کیلومتری یافت نشد.",
                "suggestions": ["🔄 افزایش شعاع جستجو", "📍 تغییر موقعیت", "🔍 جستجوی دستی"],
                "services": []
            }

        # تولید پاسخ
        service_name = self._get_service_name(service_type)
        response_text = f"📍 نزدیک‌ترین {service_name}‌ها در شعاع {radius} کیلومتر:\n\n"

        suggestions = []
        result_services = []

        for i, service in enumerate(services[:5], 1):
            response_text += f"{i}. {service['name']} - {service['distance']:.2f} کیلومتر\n"
            response_text += f"   ⭐ {service['rating']}/۵\n"
            response_text += f"   📞 {service.get('phone', 'نامشخص')}\n\n"

            suggestions.append(f"🧭 مسیریابی به {service['name']}")
            result_services.append(service)

        return {
            "response": response_text,
            "suggestions": suggestions[:3],
            "services": result_services
        }

    def search_services(
        self,
        query: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        limit: int = 20
    ) -> List[Dict]:
        """جستجوی خدمات"""
        return self.service_repo.search_services(query, latitude, longitude, limit)

    def get_service_details(self, service_id: int) -> Optional[Service]:
        """دریافت جزئیات سرویس"""
        return self.service_repo.get_by_id(service_id)

    def get_service_types(self) -> List[Dict]:
        """دریافت انواع خدمات با تعداد"""
        return self.service_repo.get_service_types()

    def get_top_rated(self, limit: int = 10) -> List[Service]:
        """دریافت خدمات با بالاترین امتیاز"""
        return self.service_repo.get_top_rated(limit)

    def calculate_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """محاسبه فاصله دو نقطه (Haversine)"""
        lon1, lat1, lon2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        km = 6371 * c
        return round(km, 2)

    def _get_service_name(self, service_type: str) -> str:
        """دریافت نام فارسی سرویس"""
        from app.core.constants import SERVICE_TYPES
        for st in SERVICE_TYPES:
            if st['id'] == service_type:
                return st['name']
        return service_type

    def get_route(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> Dict:
        """محاسبه مسیر بین دو نقطه"""
        distance = self.calculate_distance(start_lat, start_lng, end_lat, end_lng)
        duration = int(distance * 3)  # تقریب: 3 دقیقه به ازای هر کیلومتر

        return {
            "distance": distance,
            "duration": duration,
            "start": {"lat": start_lat, "lng": start_lng},
            "end": {"lat": end_lat, "lng": end_lng}
        }
