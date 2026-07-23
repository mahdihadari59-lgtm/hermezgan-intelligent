# ============================================================
# chat.py - Router چت‌بات
# ============================================================
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
import time

router = APIRouter(prefix="/chat", tags=["Chat"])


# ============================================================
# Schemas
# ============================================================
class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="متن پیام")
    user_id: str = Field(..., description="شناسه کاربر")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="عرض جغرافیایی")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="طول جغرافیایی")
    session_id: Optional[str] = Field(None, description="شناسه جلسه")


class ChatMessageResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    suggestions: List[str] = []
    processing_time: float
    from_cache: bool = False
    location: Optional[dict] = None
    session_id: str


class ConversationResponse(BaseModel):
    session_id: str
    messages: List[dict] = []


# ============================================================
# Endpoints
# ============================================================
@router.post("/message", response_model=ChatMessageResponse)
async def send_message(data: ChatMessageRequest):
    """
    ارسال پیام به چت‌بات
    """
    try:
        start_time = time.time()
        
        # تولید session_id اگر وجود نداشته باشد
        session_id = data.session_id or str(uuid.uuid4())
        
        # تشخیص ساده نیت
        intent = "general"
        confidence = 0.5
        suggestions = []
        response_text = ""
        
        message = data.message.lower()
        
        # تشخیص نیت بر اساس کلمات کلیدی
        if any(word in message for word in ["بیمارستان", "بیمار", "درمان", "داکتر", "پزشک"]):
            intent = "hospital"
            confidence = 0.9
            if data.latitude and data.longitude:
                response_text = "نزدیک‌ترین بیمارستان: بیمارستان امام خمینی - ۲.۵ کیلومتر"
                suggestions = ["📞 تماس", "🧭 مسیریابی", "دیگر بیمارستان‌ها"]
            else:
                response_text = "لطفاً موقعیت خود را به اشتراک بگذارید تا بیمارستان‌های نزدیک را پیدا کنم."
                suggestions = ["📍 اشتراک موقعیت"]
                
        elif any(word in message for word in ["رستوران", "غذا", "کباب", "شام", "ناهار"]):
            intent = "restaurant"
            confidence = 0.9
            if data.latitude and data.longitude:
                response_text = "رستوران تالار خلیج برای شما پیشنهاد می‌شود - ۱.۲ کیلومتر"
                suggestions = ["🍽️ صفحه رستوران", "⭐ نظرات", "📞 تماس"]
            else:
                response_text = "لطفاً موقعیت خود را به اشتراک بگذارید تا رستوران‌های نزدیک را پیدا کنم."
                suggestions = ["📍 اشتراک موقعیت"]
                
        elif any(word in message for word in ["تاکسی", "خودرو", "رفتن", "حمل"]):
            intent = "taxi"
            confidence = 0.9
            response_text = "تاکسی برای شما فراخوانده شد. راننده ۲ دقیقه دیگر می‌رسد"
            suggestions = ["⏱️ زمان باقی‌مانده", "📞 تماس راننده", "❌ لغو"]
            
        elif any(word in message for word in ["سلام", "درود", "هی", "خوبی", "چطوری"]):
            intent = "greeting"
            confidence = 0.95
            response_text = "سلام! 🌊 من دستیار هوشمند هرمزگان هستم. چطور می‌تونم کمکتون کنم؟"
            suggestions = ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
            
        else:
            intent = "general"
            confidence = 0.3
            response_text = "چطور می‌تونم کمکتون کنم؟ می‌تونم اطلاعات خدمات، بیمارستان‌ها یا رستوران‌ها را برای شما جستجو کنم."
            suggestions = ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
        
        processing_time = time.time() - start_time
        
        return ChatMessageResponse(
            response=response_text,
            intent=intent,
            confidence=confidence,
            suggestions=suggestions,
            processing_time=processing_time,
            from_cache=False,
            location={"lat": data.latitude, "lng": data.longitude} if data.latitude and data.longitude else None,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در پردازش پیام: {str(e)}"
        )


@router.get("/history/{user_id}", response_model=ConversationResponse)
async def get_chat_history(user_id: str, limit: int = 50):
    """
    دریافت تاریخچه چت کاربر
    """
    return ConversationResponse(
        session_id=f"session_{user_id}",
        messages=[]
    )


@router.get("/stats")
async def get_chat_stats():
    """
    دریافت آمار چت‌بات
    """
    return {
        "total_messages": 0,
        "avg_processing_time": 0,
        "intents": []
    }
