from typing import List, Dict, Any
from src.core.intent_router import Intent

class Synthesizer:
    def synthesize(self, query: str, intent: Intent, retrieved: List[Dict], ai_answer: str) -> str:
        if ai_answer:
            return ai_answer
        return self.fallback(query, retrieved)

    def fallback(self, query: str, retrieved: List[Dict]) -> str:
        if not retrieved:
            return "متأسفانه اطلاعاتی در پایگاه داده پیدا نشد. لطفاً سؤال را واضح‌تر بپرسید."
        lines = ["🔍 نتایج جستجو:"]
        for i, item in enumerate(retrieved[:5], 1):
            name = item.get("name_fa") or item.get("name") or "نامشخص"
            desc = item.get("description_fa") or item.get("description", "")
            city = item.get("city", "")
            lines.append(f"{i}. {name} ({city}) — {desc[:80]}...")
        return "\n".join(lines)
