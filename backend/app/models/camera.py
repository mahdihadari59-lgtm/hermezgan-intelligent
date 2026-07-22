from sqlalchemy import Column, Integer, String, Float, JSON, Date, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import date

from app.models.base import BaseModel, TimestampMixin


class Camera(BaseModel, TimestampMixin):
    __tablename__ = "cameras"

    camera_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    region = Column(String(100), nullable=True, index=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    types = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    priority = Column(String(20), nullable=True)
    
    installed_date = Column(Date, nullable=True)
    
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    resolution = Column(String(50), nullable=True)
    is_military = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    
    violation_count = Column(Integer, default=0, nullable=False)
    last_maintenance = Column(Date, nullable=True)
    next_maintenance = Column(Date, nullable=True)

    __table_args__ = (
        Index('idx_camera_region_status', 'region', 'status'),
        Index('idx_camera_priority', 'priority'),
        Index('idx_camera_types', 'types', postgresql_using='gin'),
    )

    def to_dict(self) -> dict:
        data = super().to_dict()
        if data.get('installed_date') and isinstance(data['installed_date'], date):
            data['installed_date'] = data['installed_date'].isoformat()
        return data
