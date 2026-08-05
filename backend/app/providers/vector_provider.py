from __future__ import annotations

import asyncio
import json
import math
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from . import BaseProvider


class VectorProvider(BaseProvider):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = str(Path(db_path).expanduser().resolve())

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _parse_vector(self, value: Any) -> Optional[List[float]]:
        if value is None:
            return None
        if isinstance(value, list):
            try:
                return [float(x) for x in value]
            except Exception:
                return None
        if isinstance(value, tuple):
            try:
                return [float(x) for x in value]
            except Exception:
                return None
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except Exception:
                return None
        if isinstance(value, str):
            s = value.strip()
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [float(x) for x in parsed]
            except Exception:
                pass
            try:
                return [float(x) for x in s.split(",") if x.strip()]
            except Exception:
                return None
        return None

    def _cosine(self, a: Sequence[float], b: Sequence[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    async def search(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        def _sync() -> List[Dict[str, Any]]:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT doc_id, vector
                    FROM knowledge_embeddings
                    LIMIT 5000
                    """
                ).fetchall()

                scored = []
                for row in rows:
                    vec = self._parse_vector(row["vector"])
                    if not vec:
                        continue
                    score = self._cosine(query_vector, vec)
                    scored.append({"doc_id": row["doc_id"], "score": score})

                scored.sort(key=lambda x: x["score"], reverse=True)
                return scored[:limit]

        return await asyncio.to_thread(_sync)
