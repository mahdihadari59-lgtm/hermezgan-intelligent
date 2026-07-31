from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, Optional

from . import BaseProvider


class BandariProvider(BaseProvider):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
            return json.loads(resp.read().decode("utf-8"))

    async def intent(self, text: str) -> Dict[str, Any]:
        return self._post("/intent", {"text": text})

    async def detect(self, text: str) -> Dict[str, Any]:
        return self._post("/detect", {"text": text})

    async def translate(self, text: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"text": text}
        if session_id:
            payload["sessionId"] = session_id
        return self._post("/translate", payload)
