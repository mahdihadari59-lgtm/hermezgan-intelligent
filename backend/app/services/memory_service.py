from __future__ import annotations
import json, os, sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DEFAULT_DB = "/data/data/com.termux/files/home/hermezgan-intelligent-backup-20260729/backend/hdp_v2.db"

class MemoryService:
    def __init__(self, db_path: Optional[str] = None, table: str = "hdp_orchestrator_memory") -> None:
        self.db_path = db_path or os.getenv("HDP_RAG_DB_PATH") or DEFAULT_DB
        self.table = table
        self._ram: Dict[str, List[Dict[str, Any]]] = {}

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                conversation_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()

    def load(self, conversation_id: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        fallback = fallback or {}
        try:
            conn = self._connect()
            try:
                self._ensure(conn)
                row = conn.execute(f"SELECT payload FROM {self.table} WHERE conversation_id=?", (conversation_id,)).fetchone()
                if row:
                    data = json.loads(row["payload"])
                    if isinstance(data, dict):
                        return data
            finally:
                conn.close()
        except Exception:
            pass
        return {"history": self._ram.get(conversation_id, []), **fallback}

    def save(self, conversation_id: str, payload: Dict[str, Any]) -> None:
        try:
            conn = self._connect()
            try:
                self._ensure(conn)
                conn.execute(
                    f"""INSERT INTO {self.table} (conversation_id, payload, updated_at)
                        VALUES (?, ?, ?)
                        ON CONFLICT(conversation_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
                    (conversation_id, json.dumps(payload, ensure_ascii=False), datetime.now(timezone.utc).isoformat()),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            self._ram[conversation_id] = payload.get("history", [])

    def append_turn(self, conversation_id: str, turn: Dict[str, Any], limit: int = 24) -> List[Dict[str, Any]]:
        current = self.load(conversation_id, {"history": []})
        history = list(current.get("history") or [])
        history.append(turn)
        history = history[-limit:]
        current["history"] = history
        self.save(conversation_id, current)
        return history
