from sqlalchemy import JSON, Column, Integer, String, Text, Float, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel, TimestampMixin


class Hotspot(BaseModel, TimestampMixin):
    __tablename__ = "hotspots"

    type = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default='active', nullable=False, index=True)
    
    reported_by = Column(String(255), nullable=True)
    reported_at = Column(DateTime, server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    images = Column(JSON, nullable=True)
    
    extra_metadata = Column("metadata", JSON, nullable=True)
    
    service_id = Column(Integer, ForeignKey('services.id'), nullable=True)
    service = relationship("Service", back_populates="hotspots")

    __table_args__ = (
        Index('idx_hotspot_type_severity', 'type', 'severity'),
        Index('idx_hotspot_status', 'status'),
        Index('idx_hotspot_location', 'latitude', 'longitude', postgresql_using='gist'),
    )
