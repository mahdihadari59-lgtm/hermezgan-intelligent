from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """ایجاد پیام چت"""
    message: str = Field(..., description="متن پیام کاربر")
    user_id: str = Field(..., description="شناسه کاربر")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="عرض جغرافیایی")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="طول جغرافیایی")
    session_id: Optional[str] = Field(None, description="شناسه جلسه")


class ChatMessageResponse(BaseModel):
    """پاسخ پیام چت"""
    response: str = Field(..., description="پاسخ چت‌بات")
    intent: str = Field(..., description="نیت تشخیص داده شده")
    confidence: float = Field(..., ge=0, le=1, description="دقت تشخیص")
    suggestions: List[str] = Field(default=[], description="پیشنهادات")
    location: Optional[Dict] = Field(None, description="اطلاعات موقعیت")
    processing_time: float = Field(..., description="زمان پردازش")
    from_cache: bool = Field(False, description="آیا از کش دریافت شده")
    message_id: Optional[int] = Field(None, description="شناسه پیام")


class ChatMessageHistory(BaseModel):
    """تاریخچه پیام چت"""
    id: int
    user: str
    bot: str
    intent: str
    confidence: float
    processing_time: float
    timestamp: str


class ChatConversationResponse(BaseModel):
    """پاسخ مکالمه چت"""
    session_id: str = Field(..., description="شناسه جلسه")
    messages: List[ChatMessageHistory] = Field(default=[], description="پیام‌ها")
    total: int = Field(0, description="تعداد کل پیام‌ها")


class ChatIntentCreate(BaseModel):
    """ایجاد نیت جدید"""
    name: str = Field(..., max_length=50, description="نام نیت")
    keywords: List[str] = Field(..., description="کلمات کلیدی")
    response_template: str = Field(..., description="الگوی پاسخ")
    entity_type: Optional[str] = Field(None, max_length=50, description="نوع موجودیت")


class ChatEntityCreate(BaseModel):
    """ایجاد موجودیت جدید"""
    name: str = Field(..., max_length=255, description="نام موجودیت")
    entity_type: str = Field(..., max_length=50, description="نوع موجودیت")
    synonyms: List[str] = Field(default=[], description="مترادف‌ها")
    service_id: Optional[int] = Field(None, description="شناسه سرویس مرتبط")


class ChatStatsResponse(BaseModel):
    """آمار چت‌بات"""
    total_messages: int
    avg_processing_time: float
    helpful_rate: float
    intents: List[Dict]


class RatingRequest(BaseModel):
    """درخواست امتیازدهی"""
    message_id: int = Field(..., description="شناسه پیام")
    helpful: bool = Field(..., description="آیا پاسخ مفید بود")
