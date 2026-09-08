"""Service Contract Definitions for HDP API

Canonical request/response schemas for all HDP microservices.
Ensures consistent API contracts across Frontend, Backend, and External Services.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


# ============================================================
# Common/Base Contracts
# ============================================================

class RequestMetadata(BaseModel):
    """Standard request metadata"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="v1")
    language: str = Field(default="fa")
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ResponseMetadata(BaseModel):
    """Standard response metadata"""
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="v1")
    processing_time_ms: float = 0.0


class StandardResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    request_id: str
    timestamp: datetime
    version: str = "v1"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0


# ============================================================
# Chat Service Contracts
# ============================================================

class ChatMessageRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    success: bool
    request_id: str
    timestamp: datetime
    message_id: str
    response: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    processing_time_ms: float


# ============================================================
# Routing Service Contracts
# ============================================================

class LocationPoint(BaseModel):
    """Geographic location"""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    name: Optional[str] = None


class RoutingRequest(BaseModel):
    """Route calculation request"""
    origin: LocationPoint
    destination: LocationPoint
    alternatives: bool = Field(default=True)
    consider_traffic: bool = Field(default=True)
    avoid_highways: bool = Field(default=False)
    user_preferences: Optional[Dict[str, Any]] = None


class RouteSegment(BaseModel):
    """Route segment details"""
    distance_km: float
    duration_minutes: float
    polyline: str
    instructions: List[str]
    traffic_status: str = "normal"


class RoutingResponse(BaseModel):
    """Route calculation response"""
    success: bool
    request_id: str
    timestamp: datetime
    primary_route: RouteSegment
    alternative_routes: Optional[List[RouteSegment]] = None
    eta: Optional[str] = None
    eta_minutes: Optional[float] = None
    warnings: Optional[List[str]] = None
    processing_time_ms: float


# ============================================================
# Search Service Contracts
# ============================================================

class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1, max_length=1000)
    search_type: str = Field(default="hybrid")
    top_k: int = Field(default=10, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = None
    location: Optional[LocationPoint] = None


class SearchResult(BaseModel):
    """Individual search result"""
    id: str
    title: str
    description: Optional[str]
    relevance_score: float = Field(ge=0.0, le=1.0)
    source: str
    location: Optional[LocationPoint] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Search response"""
    success: bool
    request_id: str
    timestamp: datetime
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time_ms: float


# ============================================================
# Traffic Service Contracts
# ============================================================

class TrafficIncident(BaseModel):
    """Traffic incident/congestion report"""
    incident_id: str
    location: LocationPoint
    incident_type: str
    severity: str = "normal"
    description: Optional[str] = None
    timestamp: datetime
    affected_duration_minutes: Optional[float] = None


class TrafficStatusRequest(BaseModel):
    """Traffic status request"""
    location: LocationPoint
    radius_km: float = Field(default=5.0, ge=0.1, le=50.0)


class TrafficStatusResponse(BaseModel):
    """Traffic status response"""
    success: bool
    request_id: str
    timestamp: datetime
    location: LocationPoint
    overall_status: str
    incidents: List[TrafficIncident]
    camera_feeds: Optional[List[str]] = None
    processing_time_ms: float


# ============================================================
# Voice Service Contracts
# ============================================================

class VoiceTranscribeRequest(BaseModel):
    """Voice transcription request"""
    audio_base64: str = Field(..., min_length=1)
    language: str = Field(default="fa")
    dialect: Optional[str] = None


class VoiceTranscribeResponse(BaseModel):
    """Voice transcription response"""
    success: bool
    request_id: str
    timestamp: datetime
    text: str
    language: str
    detected_dialect: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time_ms: float


class VoiceSynthesisRequest(BaseModel):
    """Text-to-speech request"""
    text: str = Field(..., min_length=1, max_length=5000)
    language: str = Field(default="fa")
    voice_id: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class VoiceSynthesisResponse(BaseModel):
    """Text-to-speech response"""
    success: bool
    request_id: str
    timestamp: datetime
    audio_base64: str
    audio_format: str = "wav"
    duration_seconds: float
    processing_time_ms: float


# ============================================================
# Analytics Service Contracts
# ============================================================

class AnalyticsEventRequest(BaseModel):
    """Analytics event tracking request"""
    event_name: str
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsEventResponse(BaseModel):
    """Analytics event response"""
    success: bool
    request_id: str
    timestamp: datetime
    event_id: str


# ============================================================
# Health/Status Contracts
# ============================================================

class HealthCheckResponse(BaseModel):
    """Service health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float
    components: Optional[Dict[str, str]] = None
