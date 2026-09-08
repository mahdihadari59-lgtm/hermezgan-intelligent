from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    lng: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")

    model_config = ConfigDict(from_attributes=True)


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="نام سرویس")
    type: str = Field(..., description="نوع سرویس")
    description: Optional[str] = Field(None, max_length=500, description="توضیحات")
    address: str = Field(..., max_length=500, description="آدرس")
    phone: str = Field(..., description="تلفن")
    rating: float = Field(0, ge=0, le=5, description="امتیاز")
    open_hours: Optional[str] = Field(None, description="ساعات کاری")
    status: str = Field("active", description="وضعیت")

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ServiceCreate(ServiceBase):
    lat: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    lng: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")


class ServiceResponse(ServiceBase):
    id: int
    lat: float
    lng: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceSearchParams(BaseModel):
    query: Optional[str] = Field(None, description="متن جستجو")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="عرض جغرافیایی")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="طول جغرافیایی")
    radius: float = Field(5, ge=0.5, le=50, description="شعاع جستجو (کیلومتر)")
    service_type: Optional[str] = Field(None, description="نوع سرویس")
    limit: int = Field(20, ge=1, le=100, description="تعداد نتایج")

    model_config = ConfigDict(from_attributes=True)
