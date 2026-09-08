from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from app.services.driver_assistant.models import DriverSession

logger = logging.getLogger(__name__)


class SessionStore:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, DriverSession] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def get(self, session_id: str) -> Optional[DriverSession]:
        async with self._lock:
            session = self._sessions.get(session_id)

            if session is None:
                return None

            if time.time() - session.updated_at > self.ttl_seconds:
                del self._sessions[session_id]
                logger.info("Driver session expired: %s", session_id)
                return None

            session.updated_at = time.time()
            return session

    async def create(self, session: DriverSession) -> DriverSession:
        async with self._lock:
            self._sessions[session.session_id] = session
            return session

    async def update(self, session: DriverSession) -> DriverSession:
        async with self._lock:
            if session.session_id not in self._sessions:
                raise ValueError("جلسه راننده پیدا نشد")

            session.updated_at = time.time()
            self._sessions[session.session_id] = session
            return session

    async def delete(self, session_id: str) -> bool:
        async with self._lock:
            return self._sessions.pop(session_id, None) is not None

    async def all(self) -> list[DriverSession]:
        async with self._lock:
            return list(self._sessions.values())

    async def cleanup(self) -> int:
        async with self._lock:
            now = time.time()

            expired = [
                sid
                for sid, session in self._sessions.items()
                if now - session.updated_at > self.ttl_seconds
            ]

            for sid in expired:
                del self._sessions[sid]

            if expired:
                logger.info(
                    "Driver session cleanup removed %d sessions",
                    len(expired),
                )

            return len(expired)

    async def _cleanup_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(300)
                await self.cleanup()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Driver session cleanup failed")

    async def stop(self) -> None:
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._lock:
            self._sessions.clear()
