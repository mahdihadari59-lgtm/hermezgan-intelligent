from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class CameraBase(BaseModel):
    """کلاس پایه دوربین"""
    camera_id: str = Field(..., max_length=100, description="شناسه دوربین")
    name: str = Field(..., max_length=255, description="نام دوربین")
    region: Optional[str] = Field(None, max_length=100, description="منطقه")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    types: List[str] = Field(default=[], description="انواع دوربین")
    status: str = Field(..., max_length=20, description="وضعیت")
    installed_date: Optional[date] = Field(None, description="تاریخ نصب")
    priority: Optional[str] = Field(None, max_length=20, description="اولویت")
    military: bool = Field(False, description="نظامی")


class CameraCreate(CameraBase):
    """ایجاد دوربین جدید"""
    pass


class CameraUpdate(BaseModel):
    """به‌روزرسانی دوربین"""
    name: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    types: Optional[List[str]] = None
    status: Optional[str] = Field(None, max_length=20)
    installed_date: Optional[date] = None
    priority: Optional[str] = Field(None, max_length=20)
    military: Optional[bool] = None


class CameraResponse(CameraBase):
    """پاسخ دوربین"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CameraSummary(BaseModel):
    """خلاصه دوربین‌ها"""
    total: int
    active: int
    installing: int
    pending: int
    regions: List[dict]


class CameraReportRequest(BaseModel):
    """گزارش مشکل دوربین"""
    issue: str = Field(..., description="شرح مشکل")
