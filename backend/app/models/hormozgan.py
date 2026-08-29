from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from app.core.database import Base

class Market(Base):
    __tablename__ = "markets"
    
    id = Column(Integer, primary_key=True)
    osm_id = Column(Integer, unique=True)
    name = Column(String)
    name_fa = Column(String)
    shop_type = Column(String)
    brand = Column(String)
    opening_hours = Column(String)
    phone = Column(String)
    website = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    city = Column(String)
    district = Column(String)
    collected_at = Column(DateTime)

    __table_args__ = (
        Index('idx_markets_city', 'city'),
        Index('idx_markets_type', 'shop_type'),
        Index('idx_markets_coords', 'lat', 'lon'),
    )

class Healthcare(Base):
    __tablename__ = "healthcare"
    
    id = Column(Integer, primary_key=True)
    name_fa = Column(String)
    healthcare_type = Column(String)
    city = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    phone = Column(String)
    address = Column(String)

class Education(Base):
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True)
    name_fa = Column(String)
    edu_type = Column(String)
    city = Column(String)
    lat = Column(Float)
    lon = Column(Float)

class Road(Base):
    __tablename__ = "roads"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_fa = Column(String)
    road_type = Column(String)
    city = Column(String)
    geometry = Column(Text)  # برای ذخیره GeoJSON

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_fa = Column(String)
    city_type = Column(String)
    population = Column(Integer)
    lat = Column(Float)
    lon = Column(Float)
