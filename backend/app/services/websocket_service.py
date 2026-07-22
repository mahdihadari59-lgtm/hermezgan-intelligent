import json
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class WebSocketService:
    """سرویس مدیریت WebSocket"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_groups: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, group: str = "default"):
        """اتصال WebSocket"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

        if group not in self.connection_groups:
            self.connection_groups[group] = set()
        self.connection_groups[group].add(user_id)

        logger.info(f"🔗 WebSocket متصل: user_id={user_id}, group={group}")

    def disconnect(self, user_id: str, group: str = "default"):
        """قطع اتصال WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        if group in self.connection_groups and user_id in self.connection_groups[group]:
            self.connection_groups[group].remove(user_id)

        logger.info(f"🔌 WebSocket قطع: user_id={user_id}")

    async def send_to_user(self, user_id: str, message: Any) -> bool:
        """ارسال پیام به کاربر خاص"""
        if user_id in self.active_connections:
            try:
                if isinstance(message, dict):
                    await self.active_connections[user_id].send_json(message)
                else:
                    await self.active_connections[user_id].send_text(str(message))
                return True
            except Exception as e:
                logger.error(f"❌ خطا در ارسال به {user_id}: {e}")
                return False
        return False

    async def send_to_group(self, group: str, message: Any, exclude: Optional[str] = None):
        """ارسال پیام به گروه"""
        if group not in self.connection_groups:
            return

        for user_id in self.connection_groups[group]:
            if user_id != exclude:
                await self.send_to_user(user_id, message)

    async def broadcast(self, message: Any, exclude: Optional[str] = None):
        """ارسال پیام به همه"""
        for user_id in self.active_connections:
            if user_id != exclude:
                await self.send_to_user(user_id, message)

    def get_connection_count(self) -> int:
        """تعداد اتصالات فعال"""
        return len(self.active_connections)

    def get_group_members(self, group: str) -> Set[str]:
        """دریافت اعضای گروه"""
        return self.connection_groups.get(group, set())
