from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketHub:
    def __init__(self):
        self._clients: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients[session_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        async with self._lock:
            clients = self._clients.get(session_id)
            if not clients:
                return
            clients.discard(websocket)
            if not clients:
                self._clients.pop(session_id, None)

    async def broadcast(
        self,
        session_id: str,
        event_type: str,
        data: Any,
    ) -> None:
        async with self._lock:
            clients = list(self._clients.get(session_id, set()))

        dead: list[WebSocket] = []

        for websocket in clients:
            try:
                await websocket.send_json(
                    {
                        "type": event_type,
                        "data": data,
                    }
                )
            except Exception:
                dead.append(websocket)

        for websocket in dead:
            await self.disconnect(websocket, session_id)


ws_hub = WebSocketHub()
