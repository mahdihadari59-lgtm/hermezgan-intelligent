from enum import Enum, IntEnum


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class ServiceType(str, Enum):
    HOSPITAL = "hospital"
    RESTAURANT = "restaurant"
    TAXI = "taxi"
    PHARMACY = "pharmacy"
    SCHOOL = "school"
    MOSQUE = "mosque"
    PARK = "park"
    MALL = "mall"
    BANK = "bank"
    POLICE = "police"


class CameraStatus(str, Enum):
    ACTIVE = "active"
    INSTALLING = "installing"
    PENDING = "pending"
    INACTIVE = "inactive"


class CameraType(str, Enum):
    TRAFFIC_LIGHT = "traffic-light"
    SPEED = "speed"
    PLATE = "plate"
    NIGHT_IR = "night-ir"
    SURVEILLANCE = "surveillance"
    FACE_RECOGNITION = "face-recognition"


class HotspotType(str, Enum):
    ACCIDENT = "accident"
    TRAFFIC = "traffic"
    DANGER = "danger"
    CONSTRUCTION = "construction"
    FLOOD = "flood"
    FIRE = "fire"


class HotspotSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HotspotStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SEARCH = "search"
    CHAT = "chat"
    ERROR = "error"
    LOGIN = "login"
    LOGOUT = "logout"
