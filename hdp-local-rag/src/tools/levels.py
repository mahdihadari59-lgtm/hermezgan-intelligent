import httpx
from typing import List, Dict, Any
from src.utils.config import LEVELS_API_KEY, LEVELS_BASE_URL

class LevelsTool:
    def __init__(self):
        self.api_key = LEVELS_API_KEY
        self.base_url = LEVELS_BASE_URL
        self.available = bool(self.api_key)

    async def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        if not self.available:
            return ""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"query": query, "context": context}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(f"{self.base_url}/chat", json=payload, headers=headers)
                return r.json().get("answer", "")
        except Exception:
            return ""
