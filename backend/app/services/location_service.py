# ============================================================
# location_service.py - سرویس مدیریت موقعیت و خدمات مکانی
# ============================================================
import math
import json
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

logger = logging.getLogger(__name__)


# ============================================================
# مدل‌های داده
# ============================================================

@dataclass
class Coordinates:
    """مختصات جغرافیایی"""
    lat: float
    lng: float

    def to_dict(self) -> Dict[str, float]:
        return {"lat": self.lat, "lng": self.lng}

    def distance_to(self, other: 'Coordinates') -> float:
        """محاسبه فاصله تا نقطه دیگر (به کیلومتر)"""
        return haversine_distance(self.lat, self.lng, other.lat, other.lng)


@dataclass
class ServiceLocation:
    """اطلاعات یک سرویس (بیمارستان، رستوران و ...)"""
    id: int
    name: str
    type: str
    coordinates: Coordinates
    address: str
    phone: str
    rating: float = 0.0
    distance: float = 0.0  # فاصله از موقعیت کاربر
    open_hours: str = "۲۴/۷"
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CameraLocation:
    """اطلاعات دوربین نظارتی"""
    id: str
    name: str
    region: str
    coordinates: Coordinates
    types: List[str]  # ['traffic-light', 'speed', 'plate', 'surveillance']
    status: str  # 'active', 'installing', 'pending'
    installed_date: Optional[str] = None
    priority: Optional[str] = None
    military: bool = False
    count: Optional[int] = None


@dataclass
class HotspotLocation:
    """اطلاعات نقطه حادثه‌خیز"""
    id: int
    type: str  # 'accident', 'traffic', 'danger', 'construction'
    coordinates: Coordinates
    title: str
    description: str
    severity: str  # 'high', 'medium', 'low'
    status: str  # 'active', 'resolved'
    reported_at: str
    reported_by: str


@dataclass
class RouteInfo:
    """اطلاعات مسیریابی"""
    distance: float  # کیلومتر
    duration: int  # دقیقه
    start: Coordinates
    end: Coordinates
    waypoints: List[Coordinates] = field(default_factory=list)


# ============================================================
# توابع کمکی
# ============================================================

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    محاسبه فاصله بین دو نقطه با فرمول هاورسین
    Returns: فاصله به کیلومتر
    """
    R = 6371  # شعاع زمین به کیلومتر

    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return round(R * c, 2)


def calculate_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """محاسبه جهت (bearing) بین دو نقطه"""
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlon = lng2 - lng1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360


def get_direction_text(bearing: float) -> str:
    """تبدیل جهت به متن"""
    directions = [
        (0, "شمال"), (45, "شمال شرق"), (90, "شرق"),
        (135, "جنوب شرق"), (180, "جنوب"), (225, "جنوب غرب"),
        (270, "غرب"), (315, "شمال غرب")
    ]
    for angle, direction in directions:
        if abs(bearing - angle) < 22.5 or abs(bearing - angle - 360) < 22.5:
            return direction
    return "نامشخص"


# ============================================================
# سرویس اصلی
# ============================================================

class LocationService:
    """
    سرویس مدیریت موقعیت و خدمات مکانی
    شامل: جستجو، فیلتر، محاسبه فاصله، مسیریابی
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self._cache = {}

    # ============================================================
    # داده‌های نمونه (Mock Data)
    # ============================================================

    @staticmethod
    def get_mock_services() -> List[Dict[str, Any]]:
        """دریافت داده‌های نمونه برای خدمات"""
        return [
            {
                "id": 1,
                "name": "بیمارستان فوق‌تخصصی کودکان",
                "type": "hospital",
                "lat": 27.2158,
                "lng": 56.2808,
                "rating": 4.8,
                "address": "خیابان شهید رجایی، بندرعباس",
                "phone": "۰۷۶-۳۴۰۰۱۲۳",
                "open_hours": "۲۴/۷",
                "status": "active"
            },
            {
                "id": 2,
                "name": "رستوران تالار خلیج",
                "type": "restaurant",
                "lat": 27.2200,
                "lng": 56.2900,
                "rating": 4.5,
                "address": "خیابان ولیعصر، بندرعباس",
                "phone": "۰۷۶-۳۲۲۲۲۲۲",
                "open_hours": "۱۲:۰۰ - ۲۳:۰۰",
                "status": "active"
            },
            {
                "id": 3,
                "name": "تاکسی آنلاین الفردوس",
                "type": "taxi",
                "lat": 27.2300,
                "lng": 56.2700,
                "rating": 4.6,
                "address": "ایستگاه تاکسی مرکزی، بندرعباس",
                "phone": "۰۷۶-۹۱۱۱۱۱۱۱",
                "open_hours": "۲۴/۷",
                "status": "active"
            },
            {
                "id": 4,
                "name": "داروخانه شفابخش",
                "type": "pharmacy",
                "lat": 27.2100,
                "lng": 56.2750,
                "rating": 4.3,
                "address": "خیابان تجریش، بندرعباس",
                "phone": "۰۷۶-۳۱۱۱۱۱۱",
                "open_hours": "۸:۰۰ - ۲۲:۰۰",
                "status": "active"
            },
            {
                "id": 5,
                "name": "مدرسه فرزانگاه",
                "type": "school",
                "lat": 27.2250,
                "lng": 56.2850,
                "rating": 4.7,
                "address": "خیابان دانشگاه، بندرعباس",
                "phone": "۰۷۶-۳۳۳۳۳۳۳",
                "open_hours": "۷:۳۰ - ۱۴:۰۰",
                "status": "active"
            },
            {
                "id": 6,
                "name": "بیمارستان شهید محمدی",
                "type": "hospital",
                "lat": 27.2180,
                "lng": 56.2750,
                "rating": 4.4,
                "address": "بلوار امام خمینی، بندرعباس",
                "phone": "۰۷۶-۳۴۰۰۵۶۷",
                "open_hours": "۲۴/۷",
                "status": "active"
            },
            {
                "id": 7,
                "name": "رستوران ساحل آبی",
                "type": "restaurant",
                "lat": 27.2150,
                "lng": 56.2950,
                "rating": 4.2,
                "address": "بلوار ساحلی، بندرعباس",
                "phone": "۰۷۶-۳۴۴۴۴۴۴",
                "open_hours": "۱۰:۰۰ - ۲۲:۰۰",
                "status": "active"
            }
        ]

    @staticmethod
    def get_mock_cameras() -> List[Dict[str, Any]]:
        """دریافت داده‌های نمونه برای دوربین‌ها"""
        return [
            {
                "id": "ba-001",
                "name": "چهارراه غزی",
                "region": "bandar-abbas",
                "lat": 27.2158,
                "lng": 56.2808,
                "types": ["traffic-light", "speed"],
                "status": "active",
                "installed_date": "۱۴۰۳/۰۶/۱۵"
            },
            {
                "id": "ba-002",
                "name": "میدان سپاه (فلکه امام حسین)",
                "region": "bandar-abbas",
                "lat": 27.2200,
                "lng": 56.2850,
                "types": ["traffic-light"],
                "status": "active",
                "installed_date": "۱۴۰۳/۰۶/۱۰"
            },
            {
                "id": "ba-003",
                "name": "بلوار امام خمینی (بیمارستان محمدی)",
                "region": "bandar-abbas",
                "lat": 27.2180,
                "lng": 56.2750,
                "types": ["speed"],
                "status": "active",
                "installed_date": "۱۴۰۳/۰۷/۰۱"
            },
            {
                "id": "ba-004",
                "name": "پل خواجو",
                "region": "bandar-abbas",
                "lat": 27.2250,
                "lng": 56.2900,
                "types": ["speed", "plate"],
                "status": "installing",
                "installed_date": "۱۴۰۵/۰۶/۰۵"
            },
            {
                "id": "ba-005",
                "name": "بلوار هرمز (سربالایی هدیش)",
                "region": "bandar-abbas",
                "lat": 27.2100,
                "lng": 56.2700,
                "types": ["speed", "night-ir"],
                "status": "pending",
                "priority": "urgent"
            },
            {
                "id": "kish-001",
                "name": "بلوار ساحلی کیش (۵ نقطه)",
                "region": "kish",
                "lat": 26.5200,
                "lng": 53.9800,
                "types": ["speed"],
                "status": "active",
                "installed_date": "۱۴۰۲/۱۲/۱۰",
                "count": 5
            },
            {
                "id": "qeshm-001",
                "name": "بلوار ساحلی قشم",
                "region": "qeshm",
                "lat": 26.9500,
                "lng": 55.4700,
                "types": ["speed"],
                "status": "active",
                "installed_date": "۱۴۰۳/۰۸/۱۵"
            }
        ]

    @staticmethod
    def get_mock_hotspots() -> List[Dict[str, Any]]:
        """دریافت داده‌های نمونه برای نقاط حادثه‌خیز"""
        return [
            {
                "id": 101,
                "type": "accident",
                "lat": 27.2200,
                "lng": 56.2850,
                "title": "تصادف در تقاطع خیابان شهید رجایی",
                "description": "تصادف بین دو خودرو - ترافیک سنگین",
                "severity": "high",
                "status": "active",
                "reported_at": "۱۵ دقیقه پیش",
                "reported_by": "کاربران"
            },
            {
                "id": 102,
                "type": "traffic",
                "lat": 27.2180,
                "lng": 56.2750,
                "title": "ترافیک سنگین خیابان ولیعصر",
                "description": "ترافیک بسیار سنگین - از جمهوری تا شهید رجایی",
                "severity": "medium",
                "status": "active",
                "reported_at": "۲۰ دقیقه پیش",
                "reported_by": "سیستم ترافیکی"
            },
            {
                "id": 103,
                "type": "danger",
                "lat": 27.2250,
                "lng": 56.2900,
                "title": "مناطق خطرناک - عدم رعایت علائم راهنمایی",
                "description": "منطقه‌ای که رانندگان سرعت را رعایت نمی‌کنند",
                "severity": "high",
                "status": "active",
                "reported_at": "۳۰ دقیقه پیش",
                "reported_by": "پلیس راهور"
            },
            {
                "id": 104,
                "type": "construction",
                "lat": 27.2100,
                "lng": 56.2800,
                "title": "ساخت و ساز خیابان تجریش",
                "description": "ساخت و ساز جاده - دو خط مسدود",
                "severity": "low",
                "status": "active",
                "reported_at": "۲ ساعت پیش",
                "reported_by": "شهرداری"
            }
        ]

    # ============================================================
    # متدهای اصلی جستجو
    # ============================================================

    def find_nearby_services(
        self,
        lat: float,
        lng: float,
        service_type: Optional[str] = None,
        radius: float = 5.0,
        limit: int = 20
    ) -> List[ServiceLocation]:
        """
        جستجوی خدمات نزدیک به موقعیت کاربر
        """
        services = self.get_mock_services()

        # فیلتر بر اساس نوع
        if service_type:
            services = [s for s in services if s['type'] == service_type]

        # محاسبه فاصله و فیلتر بر اساس شعاع
        results = []
        for service in services:
            distance = haversine_distance(lat, lng, service['lat'], service['lng'])
            if distance <= radius:
                results.append({
                    **service,
                    "distance": distance
                })

        # مرتب‌سازی بر اساس فاصله
        results = sorted(results, key=lambda x: x['distance'])

        # محدودیت تعداد
        results = results[:limit]

        return [
            ServiceLocation(
                id=s['id'],
                name=s['name'],
                type=s['type'],
                coordinates=Coordinates(s['lat'], s['lng']),
                address=s['address'],
                phone=s['phone'],
                rating=s.get('rating', 0),
                distance=s['distance'],
                open_hours=s.get('open_hours', '۲۴/۷'),
                status=s.get('status', 'active')
            )
            for s in results
        ]

    def search_services(
        self,
        query: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        limit: int = 20
    ) -> List[ServiceLocation]:
        """
        جستجوی خدمات بر اساس نام یا آدرس
        """
        services = self.get_mock_services()
        query_lower = query.lower()

        # فیلتر بر اساس جستجو
        results = []
        for service in services:
            if query_lower in service['name'].lower() or query_lower in service['address'].lower():
                distance = 0
                if lat and lng:
                    distance = haversine_distance(lat, lng, service['lat'], service['lng'])
                results.append({
                    **service,
                    "distance": distance
                })

        # مرتب‌سازی بر اساس فاصله (اگر موقعیت وجود داشته باشد)
        if lat and lng:
            results = sorted(results, key=lambda x: x['distance'])

        results = results[:limit]

        return [
            ServiceLocation(
                id=s['id'],
                name=s['name'],
                type=s['type'],
                coordinates=Coordinates(s['lat'], s['lng']),
                address=s['address'],
                phone=s['phone'],
                rating=s.get('rating', 0),
                distance=s['distance'],
                open_hours=s.get('open_hours', '۲۴/۷'),
                status=s.get('status', 'active')
            )
            for s in results
        ]

    def get_service_details(self, service_id: int) -> Optional[ServiceLocation]:
        """دریافت جزئیات یک سرویس خاص"""
        services = self.get_mock_services()
        for service in services:
            if service['id'] == service_id:
                return ServiceLocation(
                    id=service['id'],
                    name=service['name'],
                    type=service['type'],
                    coordinates=Coordinates(service['lat'], service['lng']),
                    address=service['address'],
                    phone=service['phone'],
                    rating=service.get('rating', 0),
                    distance=0,
                    open_hours=service.get('open_hours', '۲۴/۷'),
                    status=service.get('status', 'active')
                )
        return None

    # ============================================================
    # متدهای دوربین‌ها
    # ============================================================

    def get_cameras(
        self,
        region: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[CameraLocation]:
        """
        دریافت لیست دوربین‌ها با فیلترهای اختیاری
        """
        cameras = self.get_mock_cameras()

        if region:
            cameras = [c for c in cameras if c['region'] == region]

        if status:
            cameras = [c for c in cameras if c['status'] == status]

        return [
            CameraLocation(
                id=c['id'],
                name=c['name'],
                region=c['region'],
                coordinates=Coordinates(c['lat'], c['lng']),
                types=c.get('types', []),
                status=c['status'],
                installed_date=c.get('installed_date'),
                priority=c.get('priority'),
                military=c.get('military', False),
                count=c.get('count')
            )
            for c in cameras
        ]

    def get_cameras_nearby(
        self,
        lat: float,
        lng: float,
        radius: float = 5.0
    ) -> List[CameraLocation]:
        """
        دریافت دوربین‌های نزدیک به موقعیت کاربر
        """
        cameras = self.get_mock_cameras()
        results = []

        for camera in cameras:
            distance = haversine_distance(lat, lng, camera['lat'], camera['lng'])
            if distance <= radius:
                results.append({
                    **camera,
                    "distance": distance
                })

        results = sorted(results, key=lambda x: x['distance'])

        return [
            CameraLocation(
                id=c['id'],
                name=c['name'],
                region=c['region'],
                coordinates=Coordinates(c['lat'], c['lng']),
                types=c.get('types', []),
                status=c['status'],
                installed_date=c.get('installed_date'),
                priority=c.get('priority'),
                military=c.get('military', False),
                count=c.get('count')
            )
            for c in results
        ]

    # ============================================================
    # متدهای نقاط حادثه‌خیز
    # ============================================================

    def get_hotspots(
        self,
        hotspot_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[HotspotLocation]:
        """
        دریافت لیست نقاط حادثه‌خیز با فیلترهای اختیاری
        """
        hotspots = self.get_mock_hotspots()

        if hotspot_type:
            hotspots = [h for h in hotspots if h['type'] == hotspot_type]

        if status:
            hotspots = [h for h in hotspots if h['status'] == status]

        return [
            HotspotLocation(
                id=h['id'],
                type=h['type'],
                coordinates=Coordinates(h['lat'], h['lng']),
                title=h['title'],
                description=h['description'],
                severity=h['severity'],
                status=h['status'],
                reported_at=h['reported_at'],
                reported_by=h['reported_by']
            )
            for h in hotspots
        ]

    def get_hotspots_nearby(
        self,
        lat: float,
        lng: float,
        radius: float = 5.0
    ) -> List[HotspotLocation]:
        """
        دریافت نقاط حادثه‌خیز نزدیک
        """
        hotspots = self.get_mock_hotspots()
        results = []

        for hotspot in hotspots:
            distance = haversine_distance(lat, lng, hotspot['lat'], hotspot['lng'])
            if distance <= radius:
                results.append({
                    **hotspot,
                    "distance": distance
                })

        results = sorted(results, key=lambda x: x['distance'])

        return [
            HotspotLocation(
                id=h['id'],
                type=h['type'],
                coordinates=Coordinates(h['lat'], h['lng']),
                title=h['title'],
                description=h['description'],
                severity=h['severity'],
                status=h['status'],
                reported_at=h['reported_at'],
                reported_by=h['reported_by']
            )
            for h in results
        ]

    # ============================================================
    # متدهای مسیریابی
    # ============================================================

    def calculate_route(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> RouteInfo:
        """
        محاسبه مسیر بین دو نقطه
        """
        distance = haversine_distance(start_lat, start_lng, end_lat, end_lng)

        # تخمین زمان بر اساس نوع مسیر
        # فرض: میانگین سرعت ۴۰ کیلومتر بر ساعت در شهر
        speed_kmh = 40
        duration_minutes = int((distance / speed_kmh) * 60)

        # اگر فاصله کم باشد، زمان کمتری برآورد می‌شود
        if distance < 1:
            duration_minutes = max(2, duration_minutes)

        # مسیرهای میانی (برای نمایش بهتر)
        mid_lat = (start_lat + end_lat) / 2
        mid_lng = (start_lng + end_lng) / 2

        return RouteInfo(
            distance=distance,
            duration=duration_minutes,
            start=Coordinates(start_lat, start_lng),
            end=Coordinates(end_lat, end_lng),
            waypoints=[
                Coordinates(start_lat, start_lng),
                Coordinates(mid_lat, mid_lng),
                Coordinates(end_lat, end_lng)
            ]
        )

    def get_nearby_regions(
        self,
        lat: float,
        lng: float,
        radius: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        دریافت مناطق نزدیک به موقعیت کاربر
        """
        regions = [
            {"name": "بندرعباس", "lat": 27.2158, "lng": 56.2808},
            {"name": "قشم", "lat": 26.9500, "lng": 55.4700},
            {"name": "کیش", "lat": 26.5200, "lng": 53.9800},
            {"name": "هرمز", "lat": 27.0800, "lng": 56.4500},
            {"name": "میناب", "lat": 27.3700, "lng": 56.9200},
            {"name": "بندرلنگه", "lat": 26.5500, "lng": 54.3600},
            {"name": "جاسک", "lat": 26.6000, "lng": 57.7800},
        ]

        results = []
        for region in regions:
            distance = haversine_distance(lat, lng, region['lat'], region['lng'])
            if distance <= radius:
                results.append({
                    "name": region['name'],
                    "distance": distance,
                    "coordinates": Coordinates(region['lat'], region['lng'])
                })

        return sorted(results, key=lambda x: x['distance'])

    # ============================================================
    # متدهای کش
    # ============================================================

    def _get_cache_key(self, *args, **kwargs) -> str:
        """تولید کلید کش بر اساس پارامترها"""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()

    def clear_cache(self):
        """پاک کردن کش"""
        self._cache.clear()
        logger.info("کش سرویس موقعیت پاک شد")

    # ============================================================
    # متدهای آماری
    # ============================================================

    def get_service_stats(self) -> Dict[str, Any]:
        """
        دریافت آمار کلی خدمات
        """
        services = self.get_mock_services()
        services_by_type = {}

        for service in services:
            service_type = service['type']
            if service_type not in services_by_type:
                services_by_type[service_type] = 0
            services_by_type[service_type] += 1

        return {
            "total_services": len(services),
            "services_by_type": services_by_type,
            "active_services": len([s for s in services if s.get('status') == 'active'])
        }

    def get_camera_stats(self) -> Dict[str, Any]:
        """
        دریافت آمار دوربین‌ها
        """
        cameras = self.get_mock_cameras()
        cameras_by_status = {}
        cameras_by_region = {}

        for camera in cameras:
            # بر اساس وضعیت
            status = camera['status']
            if status not in cameras_by_status:
                cameras_by_status[status] = 0
            cameras_by_status[status] += 1

            # بر اساس منطقه
            region = camera['region']
            if region not in cameras_by_region:
                cameras_by_region[region] = 0
            cameras_by_region[region] += 1

        return {
            "total_cameras": len(cameras),
            "cameras_by_status": cameras_by_status,
            "cameras_by_region": cameras_by_region,
            "active_cameras": len([c for c in cameras if c['status'] == 'active'])
        }

    def get_hotspot_stats(self) -> Dict[str, Any]:
        """
        دریافت آمار نقاط حادثه‌خیز
        """
        hotspots = self.get_mock_hotspots()
        hotspots_by_type = {}
        hotspots_by_severity = {}

        for hotspot in hotspots:
            # بر اساس نوع
            h_type = hotspot['type']
            if h_type not in hotspots_by_type:
                hotspots_by_type[h_type] = 0
            hotspots_by_type[h_type] += 1

            # بر اساس شدت
            severity = hotspot['severity']
            if severity not in hotspots_by_severity:
                hotspots_by_severity[severity] = 0
            hotspots_by_severity[severity] += 1

        return {
            "total_hotspots": len(hotspots),
            "hotspots_by_type": hotspots_by_type,
            "hotspots_by_severity": hotspots_by_severity,
            "active_hotspots": len([h for h in hotspots if h['status'] == 'active'])
        }


# ============================================================
# نمونه Singleton
# ============================================================

_location_service_instance = None


def get_location_service(db_session: Optional[Session] = None) -> LocationService:
    """دریافت نمونه از سرویس موقعیت"""
    global _location_service_instance
    if _location_service_instance is None:
        _location_service_instance = LocationService(db_session)
    return _location_service_instance


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    service = get_location_service()

    print("=" * 60)
    print("📍 تست سرویس موقعیت")
    print("=" * 60)

    # تست جستجوی خدمات نزدیک
    print("\n🏥 خدمات نزدیک به بندرعباس:")
    nearby = service.find_nearby_services(27.2158, 56.2808, radius=10, limit=10)
    for s in nearby:
        print(f"  - {s.name} ({s.type}) - {s.distance}km ⭐{s.rating}")

    # تست جستجوی خدمات
    print("\n🔍 جستجوی 'بیمارستان':")
    search_results = service.search_services("بیمارستان", 27.2158, 56.2808)
    for s in search_results:
        print(f"  - {s.name} ({s.type}) - {s.distance}km")

    # تست دوربین‌ها
    print("\n📹 دوربین‌های فعال:")
    cameras = service.get_cameras(status="active")
    for c in cameras:
        print(f"  - {c.name} ({c.region}) - {', '.join(c.types)}")

    # تست نقاط حادثه‌خیز
    print("\n🚨 نقاط حادثه‌خیز:")
    hotspots = service.get_hotspots()
    for h in hotspots:
        print(f"  - {h.title} [{h.severity}] - {h.status}")

    # تست مسیریابی
    print("\n🧭 مسیریابی:")
    route = service.calculate_route(27.2158, 56.2808, 27.2200, 56.2900)
    print(f"  فاصله: {route.distance}km")
    print(f"  زمان: {route.duration} دقیقه")

    # تست آمار
    print("\n📊 آمار:")
    stats = service.get_service_stats()
    print(f"  کل خدمات: {stats['total_services']}")
    print(f"  خدمات فعال: {stats['active_services']}")
    print(f"  توزیع: {stats['services_by_type']}")

    print("\n✅ تست سرویس موقعیت با موفقیت انجام شد!")
