# ============================================================
# gemini.py - سرویس Gemini AI
# ============================================================
import os
import json
import logging
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

logger = logging.getLogger(__name__)
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta")


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    temperature: Optional[float] = 0.7


@router.post("/chat")
async def chat(payload: ChatRequest):
    """چت با Gemini AI"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=503, detail="GEMINI_API_KEY تنظیم نشده")

        url = f"{GEMINI_API_URL}/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"role": "user", "parts": [{"text": payload.message}]}],
            "generationConfig": {"temperature": payload.temperature}
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini connection error: {e}")
            return {
                "success": False,
                "error": "خطا در اتصال به Gemini (مشکل شبکه)",
                "provider": "gemini"
            }

        if response.status_code != 200:
            logger.error(f"Gemini HTTP {response.status_code}: {response.text[:200]}")
            return {
                "success": False,
                "error": f"Gemini API HTTP {response.status_code}",
                "provider": "gemini"
            }

        try:
            result = response.json()
        except ValueError:
            logger.error(f"Gemini returned non-JSON response: {response.text[:200]}")
            return {
                "success": False,
                "error": "پاسخ نامعتبر از Gemini (احتمالاً مشکل شبکه/اتصال به Google)",
                "provider": "gemini"
            }

        if "candidates" in result and result["candidates"]:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "success": True,
                "response": text,
                "provider": "gemini",
                "model": "gemini-flash-latest"
            }

        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "provider": "gemini"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def ai_status():
    """وضعیت سرویس Gemini AI"""
    return {
        "status": "active",
        "service": "gemini_ai",
        "provider": "google",
        "api_key_configured": bool(GEMINI_API_KEY),
        "model": "gemini-flash-latest"
    }
