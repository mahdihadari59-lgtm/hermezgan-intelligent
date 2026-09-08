from __future__ import annotations

from typing import Any, Dict


class MedicalExpert:
    name = "medical"

    async def answer(self, query: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "expert": self.name,
            "warning": "این پاسخ جایگزین مشاوره پزشکی نیست.",
            "query": query,
            "data": data,
        }
