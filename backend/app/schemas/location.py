from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ServiceBase(BaseModel):
    """کلاس پایه سرویس"""
    name: str = Field(..., max_length=255, description="نام سرویس")
    type: str = Field(..., max_length=50, description="نوع سرویس")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    address: Optional[str] = Field(None, max_length=500, description="آدرس")
    phone: Optional[str] = Field(None, max_length=20, description="تلفن")
    rating: float = Field(0, ge=0, le=5, description="امتیاز")
    description: Optional[str] = Field(None, description="توضیحات")


class ServiceCreate(ServiceBase):
    """ایجاد سرویس جدید"""
    pass


class ServiceUpdate(BaseModel):
    """به‌روزرسانی سرویس"""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    rating: Optional[float] = Field(None, ge=0, le=5)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class ServiceResponse(ServiceBase):
    """پاسخ سرویس"""
    id: int
    status: str = "active"
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceWithDistance(ServiceResponse):
    """سرویس با فاصله"""
    distance: float = Field(..., description="فاصله بر حسب کیلومتر")


class LocationSearchResponse(BaseModel):
    """پاسخ جستجوی مکان"""
    results: List[ServiceWithDistance]
    total: int


class NearbyServicesResponse(BaseModel):
    """پاسخ خدمات نزدیک"""
    services: List[ServiceWithDistance]
    total: int


class RouteRequest(BaseModel):
    """درخواست مسیریابی"""
    start_lat: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی مبدا")
    start_lng: float = Field(..., ge=-180, le=180, description="طول جغرافیایی مبدا")
    end_lat: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی مقصد")
    end_lng: float = Field(..., ge=-180, le=180, description="طول جغرافیایی مقصد")


class RouteResponse(BaseModel):
    """پاسخ مسیریابی"""
    distance: float = Field(..., description="فاصله بر حسب کیلومتر")
    duration: int = Field(..., description="زمان تقریبی بر حسب دقیقه")
    start: dict = Field(..., description="مبدا")
    end: dict = Field(..., description="مقصد")
