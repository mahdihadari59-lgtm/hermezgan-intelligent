from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HotspotBase(BaseModel):
    type: str = Field(..., description="نوع حادثه")
    lat: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    lng: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    title: str = Field(..., min_length=3, max_length=255, description="عنوان")
    description: str = Field(..., min_length=5, max_length=500, description="توضیحات")
    severity: str = Field(..., description="شدت")

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class HotspotCreate(HotspotBase):
    reported_by: str = Field("کاربر", description="گزارش‌دهنده")


class HotspotResponse(HotspotBase):
    id: int
    status: str
    reported_by: str
    reported_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HotspotFilterParams(BaseModel):
    type: Optional[str] = Field(None, description="نوع حادثه")
    severity: Optional[str] = Field(None, description="شدت")
    status: Optional[str] = Field(None, description="وضعیت")
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius: float = Field(5, ge=0.5, le=50)

    model_config = ConfigDict(from_attributes=True)
