from __future__ import annotations

from typing import Any, Dict


class TransportExpert:
    name = "transport"

    async def answer(self, query: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"expert": self.name, "query": query, "data": data}
