from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CameraBase(BaseModel):
    camera_id: str = Field(..., max_length=100, description="شناسه دوربین")
    name: str = Field(..., max_length=255, description="نام دوربین")
    region: str = Field(..., max_length=100, description="منطقه")
    lat: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    lng: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    types: List[str] = Field(..., description="انواع دوربین")
    status: str = Field(..., description="وضعیت")

    model_config = ConfigDict(from_attributes=True)


class CameraCreate(CameraBase):
    installed_date: Optional[str] = None
    priority: Optional[str] = None
    military: bool = False
    count: Optional[int] = None


class CameraResponse(CameraBase):
    id: int
    installed_date: Optional[str] = None
    priority: Optional[str] = None
    military: bool = False
    count: Optional[int] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CameraFilterParams(BaseModel):
    region: Optional[str] = Field(None, description="منطقه")
    status: Optional[str] = Field(None, description="وضعیت")
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius: float = Field(5, ge=0.5, le=50)

    model_config = ConfigDict(from_attributes=True)
