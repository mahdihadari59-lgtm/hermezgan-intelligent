from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from . import BaseProvider


class GraphProvider(BaseProvider):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = str(Path(db_path).expanduser().resolve())

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    async def neighbors(self, node_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        def _sync() -> List[Dict[str, Any]]:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT
                        e.*,
                        n2.title AS target_title,
                        n2.category AS target_category
                    FROM knowledge_edges e
                    LEFT JOIN knowledge_nodes n2 ON n2.id = e.target_id
                    WHERE e.source_id = ?
                    ORDER BY COALESCE(e.weight, 0) DESC
                    LIMIT ?
                    """,
                    (node_id, limit),
                ).fetchall()
                return [dict(r) for r in rows]

        return await asyncio.to_thread(_sync)
