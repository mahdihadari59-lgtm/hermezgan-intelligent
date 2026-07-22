from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel, TimestampMixin


class Service(BaseModel, TimestampMixin):
    __tablename__ = "services"

    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    
    rating = Column(Float, default=0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    
    open_hours = Column(JSON, nullable=True)
    
    status = Column(String(20), default='active', nullable=False, index=True)
    
    features = Column(JSON, nullable=True)
    
    hotspots = relationship("Hotspot", back_populates="service")

    __table_args__ = (
        Index('idx_service_type_status', 'type', 'status'),
        Index('idx_service_location', 'latitude', 'longitude'),
    )


class Location(BaseModel, TimestampMixin):
    __tablename__ = "locations"

    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=True)
    region = Column(String(100), nullable=True, index=True)
    parent_id = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index('idx_location_region_type', 'region', 'type'),
        Index('idx_location_parent', 'parent_id'),
    )
