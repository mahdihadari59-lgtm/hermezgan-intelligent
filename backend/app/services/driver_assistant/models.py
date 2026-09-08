from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DriverIntent(str, Enum):
    """نیت‌های اصلی دستیار راننده"""

    UNKNOWN = "unknown"

    # قرارداد جدید Driver Assistant
    START_NAVIGATION = "start_navigation"
    ROUTE = "route"
    CHANGE_ROUTE = "change_route"
    CANCEL_DESTINATION = "cancel_destination"
    FIND_NEAREST_POI = "find_nearest_poi"
    ETA_QUERY = "eta_query"
    GENERAL_CHAT = "general_chat"

    # سازگاری با intentهای قبلی سیستم
    NAVIGATION = "navigation"
    DESTINATION = "destination"
    TRAFFIC = "traffic"
    WEATHER = "weather"
    POI = "poi"
    STOP = "stop"
    CONTINUE = "continue"
    HELP = "help"
    STATUS = "status"
    CONFIRM = "confirm"
    CANCEL = "cancel"


class NavigationStatus(str, Enum):
    """وضعیت ناوبری"""

    IDLE = "idle"
    ROUTING = "routing"
    REROUTING = "rerouting"
    NAVIGATING = "navigating"
    ARRIVED = "arrived"
    STOPPED = "stopped"
    CANCELLED = "cancelled"
    ERROR = "error"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Location:
    """موقعیت جغرافیایی راننده"""

    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy,
            "heading": self.heading,
            "speed": self.speed,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.as_dict()


@dataclass
class POICandidate:
    """مکان کاندید از poi_unified"""

    name: str
    latitude: float
    longitude: float

    address: Optional[str] = None
    place_id: Optional[str] = None
    distance: Optional[float] = None
    rating: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    score: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def location(self) -> Location:
        return Location(
            latitude=self.latitude,
            longitude=self.longitude,
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "place_id": self.place_id,
            "distance": self.distance,
            "rating": self.rating,
            "category": self.category,
            "subcategory": self.subcategory,
            "score": self.score,
            "metadata": self.metadata,
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.as_dict()


@dataclass
class NavigationState:
    """وضعیت اجرایی ناوبری و مسیر فعال"""

    status: NavigationStatus = NavigationStatus.IDLE

    current_location: Optional[Location] = None

    # مقصد خام برای سازگاری با NavigationEngine
    destination: Optional[Location] = None

    # POI کامل مقصد
    destination_poi: Optional[POICandidate] = None

    destination_name: Optional[str] = None

    # پاسخ کامل OSRM
    active_route: Optional[Dict[str, Any]] = None

    distance_remaining_m: float = 0.0
    duration_remaining_s: float = 0.0

    eta_timestamp: Optional[float] = None

    instructions: List[Dict[str, Any]] = field(default_factory=list)
    next_instruction_index: int = 0

    off_route: bool = False
    last_reroute_timestamp: Optional[float] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value
            if isinstance(self.status, NavigationStatus)
            else str(self.status),

            "current_location": (
                self.current_location.as_dict()
                if self.current_location
                else None
            ),

            "destination": (
                self.destination.as_dict()
                if self.destination
                else None
            ),

            "destination_poi": (
                self.destination_poi.as_dict()
                if self.destination_poi
                else None
            ),

            "destination_name": self.destination_name,
            "active_route": self.active_route,

            "distance_remaining_m": self.distance_remaining_m,
            "duration_remaining_s": self.duration_remaining_s,
            "eta_timestamp": self.eta_timestamp,

            "instructions": self.instructions,
            "next_instruction_index": self.next_instruction_index,

            "off_route": self.off_route,
            "last_reroute_timestamp": self.last_reroute_timestamp,

            "metadata": self.metadata,
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.as_dict()


@dataclass
class DriverSession:
    """جلسه پایدار منطقی دستیار راننده"""

    session_id: str
    user_id: str

    # پروفایل OSRM
    profile: str = "driving"

    # وضعیت اصلی ناوبری
    navigation: NavigationState = field(
        default_factory=NavigationState
    )

    # وضعیت فعال بودن Session
    active: bool = True

    # آخرین intent تشخیص داده‌شده
    intent: DriverIntent = DriverIntent.UNKNOWN

    # زمان‌ها
    created_at: Any = field(default_factory=datetime.now)
    updated_at: Any = field(default_factory=datetime.now)

    # Context متعلق به Kernel / Driver Assistant
    context: Dict[str, Any] = field(default_factory=dict)

    # metadata برای سازگاری و telemetry
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        intent = (
            self.intent.value
            if isinstance(self.intent, DriverIntent)
            else str(self.intent)
        )

        def serialize_time(value: Any) -> Any:
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "profile": self.profile,
            "active": self.active,
            "intent": intent,
            "created_at": serialize_time(self.created_at),
            "updated_at": serialize_time(self.updated_at),
            "context": self.context,
            "metadata": self.metadata,
            "navigation": self.navigation.as_dict(),
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.as_dict()


@dataclass
class DriverResponse:
    """پاسخ استاندارد دستیار راننده"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    intent: Optional[DriverIntent] = None
    error: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "intent": (
                self.intent.value
                if isinstance(self.intent, DriverIntent)
                else self.intent
            ),
            "error": self.error,
        }


@dataclass
class RouteInfo:
    """اطلاعات مسیر"""

    distance: float
    duration: float
    polyline: Optional[str] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    traffic_delay: Optional[float] = None
