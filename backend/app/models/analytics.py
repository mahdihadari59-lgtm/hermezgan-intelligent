from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date

from app.models.base import BaseModel, TimestampMixin


class AnalyticsEvent(BaseModel, TimestampMixin):
    __tablename__ = "analytics_events"

    user_id = Column(Integer, nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_name = Column(String(100), nullable=True)
    event_data = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    referrer = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)

    __table_args__ = (
        Index('idx_event_type_created', 'event_type', 'created_at'),
        Index('idx_event_user_created', 'user_id', 'created_at'),
        Index('idx_event_session', 'session_id'),
    )


class DailyStat(BaseModel, TimestampMixin):
    __tablename__ = "daily_stats"

    stat_date = Column(Date, unique=True, nullable=False, index=True)
    
    total_users = Column(Integer, default=0, nullable=False)
    new_users = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    
    chat_messages = Column(Integer, default=0, nullable=False)
    chat_sessions = Column(Integer, default=0, nullable=False)
    avg_response_time = Column(Float, default=0, nullable=False)
    
    service_searches = Column(Integer, default=0, nullable=False)
    location_requests = Column(Integer, default=0, nullable=False)
    route_requests = Column(Integer, default=0, nullable=False)
    
    camera_views = Column(Integer, default=0, nullable=False)
    camera_reports = Column(Integer, default=0, nullable=False)
    
    hotspot_views = Column(Integer, default=0, nullable=False)
    hotspot_reports = Column(Integer, default=0, nullable=False)
    
    page_views = Column(Integer, default=0, nullable=False)
    total_requests = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    
    summary = Column(JSON, nullable=True)

    @classmethod
    def get_today(cls):
        today = date.today()
        return cls.query.filter_by(stat_date=today).first()
