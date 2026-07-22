from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HotspotBase(BaseModel):
    """کلاس پایه نقطه حادثه‌خیز"""
    type: str = Field(..., max_length=50, description="نوع حادثه")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    title: str = Field(..., max_length=255, description="عنوان")
    description: Optional[str] = Field(None, description="توضیحات")
    severity: str = Field(..., max_length=20, description="شدت")
    reported_by: Optional[str] = Field(None, max_length=255, description="گزارش‌دهنده")


class HotspotCreate(HotspotBase):
    """ایجاد نقطه حادثه‌خیز جدید"""
    pass


class HotspotUpdate(BaseModel):
    """به‌روزرسانی نقطه حادثه‌خیز"""
    type: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    severity: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    reported_by: Optional[str] = Field(None, max_length=255)


class HotspotResponse(HotspotBase):
    """پاسخ نقطه حادثه‌خیز"""
    id: int
    status: str = "active"
    reported_at: datetime
    updated_at: Optional[datetime] = None
    distance: Optional[float] = Field(None, description="فاصله بر حسب کیلومتر")

    class Config:
        from_attributes = True


class HotspotSummary(BaseModel):
    """خلاصه نقاط حادثه‌خیز"""
    total: int
    by_type: List[dict]
    by_severity: List[dict]
    recent: List[HotspotResponse]


class HotspotFilter(BaseModel):
    """فیلتر نقاط حادثه‌خیز"""
    type: Optional[str] = Field(None, description="نوع حادثه")
    severity: Optional[str] = Field(None, description="شدت")
    status: Optional[str] = Field(None, description="وضعیت")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="عرض جغرافیایی")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="طول جغرافیایی")
    radius: float = Field(5.0, ge=0, le=50, description="شعاع جستجو بر حسب کیلومتر")
