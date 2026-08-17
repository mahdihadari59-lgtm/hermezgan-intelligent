"""Event Contract Definitions for HDP Event Bus

Standardizes event schemas across all HDP services for consistent pub/sub messaging.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class EventType(str, Enum):
    """Standard event types"""
    # Auth Events
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    
    # User Events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Trip Events
    TRIP_STARTED = "trip.started"
    TRIP_UPDATED = "trip.updated"
    TRIP_COMPLETED = "trip.completed"
    TRIP_CANCELLED = "trip.cancelled"
    
    # Location Events
    LOCATION_UPDATED = "location.updated"
    LOCATION_TRACKED = "location.tracked"
    
    # Traffic Events
    TRAFFIC_INCIDENT = "traffic.incident"
    TRAFFIC_CONGESTION = "traffic.congestion"
    TRAFFIC_CLEARED = "traffic.cleared"
    
    # Route Events
    ROUTE_CALCULATED = "route.calculated"
    ROUTE_OPTIMIZED = "route.optimized"
    
    # Copilot Events
    COPILOT_QUERY = "copilot.query"
    COPILOT_RESPONSE = "copilot.response"
    COPILOT_LEARNED = "copilot.learned"
    
    # Voice Events
    VOICE_TRANSCRIBED = "voice.transcribed"
    VOICE_SYNTHESIZED = "voice.synthesized"
    
    # Emergency Events
    EMERGENCY_ALERT = "emergency.alert"
    EMERGENCY_RESOLVED = "emergency.resolved"
    
    # Notification Events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_READ = "notification.read"
    
    # System Events
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class HdpEvent(BaseModel):
    """Standard HDP Event"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0")
    correlation_id: Optional[str] = None
    
    # Event payload
    payload: Dict[str, Any]
    
    # Metadata
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = Field(default=0, ge=0, le=3)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


# ============================================================
# Specific Event Payloads
# ============================================================

class AuthLoginPayload(BaseModel):
    """Auth login event payload"""
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    login_method: str
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


class TripStartedPayload(BaseModel):
    """Trip started event payload"""
    trip_id: str
    user_id: str
    driver_id: Optional[str] = None
    origin: Dict[str, float]
    destination: Dict[str, float]
    estimated_duration_minutes: float
    vehicle_id: Optional[str] = None


class TrafficIncidentPayload(BaseModel):
    """Traffic incident event payload"""
    incident_id: str
    location: Dict[str, float]
    incident_type: str
    severity: str
    description: Optional[str] = None
    affected_routes: Optional[list] = None
    duration_minutes: Optional[float] = None


class CopilotQueryPayload(BaseModel):
    """Copilot query event payload"""
    query_id: str
    user_id: Optional[str] = None
    query_text: str
    query_type: str
    detected_intent: Optional[str] = None
    detected_dialect: Optional[str] = None


class LocationUpdatedPayload(BaseModel):
    """Location updated event payload"""
    user_id: str
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    heading: Optional[float] = None
    speed_kmh: Optional[float] = None
    is_trip_active: bool = False


class NotificationSentPayload(BaseModel):
    """Notification sent event payload"""
    notification_id: str
    user_id: str
    notification_type: str
    title: str
    body: str
    channel: str
    delivery_status: str


class SystemHealthPayload(BaseModel):
    """System health event payload"""
    service_name: str
    status: str
    uptime_seconds: float
    metrics: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, str]] = None


class SystemErrorPayload(BaseModel):
    """System error event payload"""
    error_id: str
    service_name: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    affected_users: Optional[int] = None
    resolution_status: str = "pending"
