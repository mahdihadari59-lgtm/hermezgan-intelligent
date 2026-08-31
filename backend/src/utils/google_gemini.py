import httpx
from typing import List, Dict, Any
from src.utils.config import GOOGLE_GEMINI_API_KEY, GOOGLE_GEMINI_MODEL

class GoogleGeminiTool:
    def __init__(self):
        self.api_key = GOOGLE_GEMINI_API_KEY
        self.model = GOOGLE_GEMINI_MODEL
        self.available = bool(self.api_key)

    async def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        if not self.available:
            return ""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        context_text = "\n".join([str(c) for c in context[:3]])
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"سؤال کاربر: {query}\n\nاطلاعات پایگاه داده:\n{context_text}\n\nلطفاً به فارسی پاسخ بده."
                }]
            }]
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            data = r.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
