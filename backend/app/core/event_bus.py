from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable, DefaultDict, List

Handler = Callable[[dict], Awaitable[None]]

class EventBus:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[Handler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, event_name: str, handler: Handler) -> None:
        async with self._lock:
            self._subs[event_name].append(handler)

    async def publish(self, event_name: str, payload: dict) -> None:
        handlers = list(self._subs.get(event_name, []))
        if not handlers:
            return
        await asyncio.gather(*(h(payload) for h in handlers), return_exceptions=True)

    async def emit(self, event_name: str, payload: dict) -> None:
        await self.publish(event_name, payload)
