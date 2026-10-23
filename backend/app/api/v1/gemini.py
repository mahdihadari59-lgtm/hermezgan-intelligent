# ============================================================
# gemini.py - سرویس هوش مصنوعی عمومی (provider-agnostic)
# ============================================================
import os
import logging
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

logger = logging.getLogger(__name__)
router = APIRouter()

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_API_URL = os.getenv("AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")
AI_PROVIDER = os.getenv("AI_PROVIDER", "generic")


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    temperature: Optional[float] = 0.7


@router.post("/chat")
async def chat(payload: ChatRequest):
    """چت با سرویس هوش مصنوعی عمومی"""
    try:
        if not AI_API_KEY:
            raise HTTPException(status_code=503, detail="AI_API_KEY تنظیم نشده")

        url = f"{AI_API_URL}/models/{AI_MODEL}:generateContent?key={AI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"role": "user", "parts": [{"text": payload.message}]}],
            "generationConfig": {"temperature": payload.temperature}
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            logger.error(f"AI connection error: {e}")
            return {
                "success": False,
                "error": "خطا در اتصال به سرویس هوش مصنوعی",
                "provider": AI_PROVIDER,
                "model": AI_MODEL,
            }

        if response.status_code != 200:
            logger.error(f"AI HTTP {response.status_code}: {response.text[:200]}")
            return {
                "success": False,
                "error": f"AI API HTTP {response.status_code}",
                "provider": AI_PROVIDER,
                "model": AI_MODEL,
            }

        try:
            result = response.json()
        except ValueError:
            logger.error(f"AI returned non-JSON response: {response.text[:200]}")
            return {
                "success": False,
                "error": "پاسخ نامعتبر از سرویس هوش مصنوعی",
                "provider": AI_PROVIDER,
                "model": AI_MODEL,
            }

        if "candidates" in result and result["candidates"]:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "success": True,
                "response": text,
                "provider": AI_PROVIDER,
                "model": AI_MODEL,
            }

        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "provider": AI_PROVIDER,
            "model": AI_MODEL,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def ai_status():
    """وضعیت سرویس هوش مصنوعی"""
    return {
        "status": "active",
        "service": "ai_service",
        "provider": AI_PROVIDER,
        "api_key_configured": bool(AI_API_KEY),
        "model": AI_MODEL,
    }
