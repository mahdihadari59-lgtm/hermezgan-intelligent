import httpx
from typing import List, Dict, Any
from src.utils.config import LOCAL_LLM_URL, LOCAL_LLM_MODEL

class LocalLlmTool:
    def __init__(self):
        self.url = LOCAL_LLM_URL
        self.model = LOCAL_LLM_MODEL
        self.available = False

    async def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        context_text = "\n".join([str(c) for c in context[:3]])
        payload = {
            "model": self.model,
            "prompt": f"سؤال: {query}\nاطلاعات: {context_text}\nپاسخ:",
            "stream": False
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(self.url, json=payload)
                data = r.json()
                return data.get("response", "")
        except Exception:
            return ""
