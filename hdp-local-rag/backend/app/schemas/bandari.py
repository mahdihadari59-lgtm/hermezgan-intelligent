from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class BandariDetectRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

class BandariDetectResponse(BaseModel):
    success: bool
    data: dict[str, Any]

class BandariTranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    source: str = "persian"
    target: str = "ban"
    session_id: Optional[str] = None

class BandariTranslateResponse(BaseModel):
    success: bool
    data: dict[str, Any]

class BandariStatsResponse(BaseModel):
    success: bool
    data: dict[str, Any]
