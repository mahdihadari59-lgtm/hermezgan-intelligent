# app/api/v1/endpoints/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    suggestions: List[str] = []

@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """ارسال پیام به چت‌بات"""
    message = req.message.lower()
    
    # تشخیص ساده نیت
    intents = {
        "hospital": ["بیمارستان", "بیمار", "درمان", "داکتر", "دکتر"],
        "restaurant": ["رستوران", "غذا", "کباب", "شام", "ناهار"],
        "taxi": ["تاکسی", "خودرو", "رفتن", "حمل", "مسیر"],
        "traffic": ["ترافیک", "شلوغ", "راه", "بسته", "گرفت"],
        "hotel": ["هتل", "اقامت", "خواب", "مسافرخانه"],
    }
    
    detected_intent = "general"
    for intent, keywords in intents.items():
        if any(k in message for k in keywords):
            detected_intent = intent
            break
    
    # پاسخ‌ها
    responses = {
        "hospital": {
            "response": "🏥 نزدیک‌ترین بیمارستان: بیمارستان شهید محمدی - بلوار امام خمینی\n📞 تلفن: ۰۷۶-۳۳۳۳۲۰۰۰",
            "suggestions": ["🧭 مسیریابی", "📞 تماس", "بیمارستان کودکان"]
        },
        "restaurant": {
            "response": "🍽️ رستوران‌های خوب بندرعباس:\n1. گوهرشاد - ساحل غدیر\n2. صیاد - بلوار ساحلی\n3. سنتی بندر - بازار قدیم",
            "suggestions": ["📍 مسیریابی", "⭐ نظرات", "📞 رزرو"]
        },
        "taxi": {
            "response": "🚗 تاکسی برای شما فراخوانده شد. راننده ۳ دقیقه دیگر می‌رسد.\nشماره تماس راننده: ۰۹۱۷-XXX-XXXX",
            "suggestions": ["⏱️ زمان باقی‌مانده", "📞 تماس راننده", "❌ لغو"]
        },
        "traffic": {
            "response": "🚦 وضعیت ترافیک لحظه‌ای:\n• چهارراه غزی: 🔴 سنگین\n• میدان سپاه: 🔴 سنگین\n• سه‌راه ایسین: 🟡 نیمه سنگین\n• بلوار سرباز: 🟢 روان",
            "suggestions": ["🔄 به‌روزرسانی", "🗺️ مسیر جایگزین", "📊 جزئیات بیشتر"]
        },
        "general": {
            "response": "🌊 سلام! من دستیار هرمزگان هوشمند هستم.\nچطور می‌تونم کمکتون کنم؟\n\n🔹 برای بیمارستان بپرسید\n🔹 برای رستوران بپرسید\n🔹 برای تاکسی بپرسید\n🔹 برای ترافیک بپرسید",
            "suggestions": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی", "🚦 ترافیک"]
        }
    }
    
    response = responses.get(detected_intent, responses["general"])
    
    return ChatResponse(
        response=response["response"],
        intent=detected_intent,
        confidence=0.92,
        suggestions=response["suggestions"]
    )

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50):
    """دریافت تاریخچه چت"""
    return {
        "user_id": user_id,
        "messages": [
            {"role": "user", "content": "سلام", "timestamp": "۱۴۰۴/۰۵/۱۶ ۱۰:۰۰"},
            {"role": "bot", "content": "سلام! چطور می‌تونم کمکتون کنم؟", "timestamp": "۱۴۰۴/۰۵/۱۶ ۱۰:۰۰"}
        ],
        "total": 2
    }
