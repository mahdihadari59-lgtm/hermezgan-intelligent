from __future__ import annotations

from typing import Any, Dict


class TourismExpert:
    name = "tourism"

    async def answer(self, query: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"expert": self.name, "query": query, "data": data}
