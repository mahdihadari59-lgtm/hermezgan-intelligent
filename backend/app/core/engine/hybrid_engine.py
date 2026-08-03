#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import aiosqlite
from typing import List, Dict


class HybridEngine:

    def __init__(self, db_path):
        self.db_path = db_path

    async def search(
        self,
        query,
        intent="general",
        dialect="standard",
        limit=5,
    ) -> List[Dict]:
        sql = """
        SELECT id, title, content, category
        FROM knowledge
        WHERE knowledge MATCH ?
        LIMIT ?
        """
        docs = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, (query, limit)) as cursor:
                rows = await cursor.fetchall()

        for row in rows:
            docs.append({
                "id": row["id"],
                "title": row["title"],
                "text": row["content"],
                "source": row["category"],
                "score": 1.0,
            })
        return docs
