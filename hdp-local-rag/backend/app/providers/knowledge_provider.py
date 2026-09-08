from __future__ import annotations

import asyncio
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import BaseProvider


class KnowledgeProvider(BaseProvider):
    TABLE_CANDIDATES = (
        "knowledge",
        "knowledge_search",
        "master_knowledge",
        "unified_search",
        "v_knowledge_unified",
        "search_all",
        "knowledge_library",
        "knowledge_nodes",
    )

    TEXT_COLUMNS = (
        "title",
        "content",
        "question",
        "answer",
        "keywords",
        "tags",
        "topic",
        "subtopic",
        "subcategory",
        "category",
        "category_fa",
        "intent",
        "main_intent",
        "sub_intent",
        "expert_name",
        "city",
        "graph_path",
        "source",
        "atlas",
        "status",
        "quality",
    )

    ORDER_COLUMNS = ("priority", "confidence", "updated_at", "created_at")

    STOPWORDS = {
        "کجاست",
        "چیست",
        "چیه",
        "چی",
        "است",
        "هست",
        "را",
        "برای",
        "در",
        "از",
        "به",
        "که",
        "می",
        "کن",
        "کند",
        "شد",
        "شود",
        "های",
        "ها",
        "هایش",
        "این",
        "آن",
        "یک",
        "چند",
        "کدام",
        "کدامند",
        "کجا",
        "چه",
        "چگونه",
    }

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = str(Path(db_path).expanduser().resolve())
        self._table_name: Optional[str] = None
        self._columns: List[str] = []
        self._schema_loaded = False

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _quote(self, name: str) -> str:
        return '"' + name.replace('"', '""') + '"'

    def _normalize_query(self, query: str) -> str:
        q = (query or "").strip()
        q = q.replace("ي", "ی").replace("ك", "ک")
        q = re.sub(r"[؟?!،,:؛\"'(){}\[\]\-_/\\|]+", " ", q)
        q = re.sub(r"\s+", " ", q).strip()

        words = [
            w for w in q.split()
            if len(w) > 1 and w not in self.STOPWORDS
        ]
        return " ".join(words)

    def _load_schema(self) -> None:
        if self._schema_loaded:
            return

        with self._connect() as conn:
            tables = {
                str(row[0])
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
                ).fetchall()
            }

            for table in self.TABLE_CANDIDATES:
                if table in tables:
                    self._table_name = table
                    self._columns = [
                        str(r[1])
                        for r in conn.execute(
                            f"PRAGMA table_info({self._quote(table)})"
                        ).fetchall()
                    ]
                    break

            if self._table_name is None and tables:
                for table in sorted(tables):
                    cols = [
                        str(r[1])
                        for r in conn.execute(
                            f"PRAGMA table_info({self._quote(table)})"
                        ).fetchall()
                    ]
                    if any(c in cols for c in ("title", "content", "question", "answer")):
                        self._table_name = table
                        self._columns = cols
                        break

        self._schema_loaded = True

    def _pick_text_cols(self) -> List[str]:
        cols = [c for c in self.TEXT_COLUMNS if c in self._columns]
        if cols:
            return cols
        return [c for c in ("title", "content", "question", "answer", "keywords", "tags") if c in self._columns]

    def _pick_order_sql(self) -> str:
        parts: list[str] = []
        for col in self.ORDER_COLUMNS:
            if col in self._columns:
                if col in ("priority", "confidence"):
                    parts.append(f"COALESCE(CAST({self._quote(col)} AS REAL), 0) DESC")
                else:
                    parts.append(f"COALESCE({self._quote(col)}, '') DESC")
        return (" ORDER BY " + ", ".join(parts)) if parts else ""

    def _pick_filter_sql(self, category: Optional[str], intent: Optional[str]) -> tuple[str, list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        if category:
            category_cols = [c for c in ("category", "category_fa", "atlas") if c in self._columns]
            if category_cols:
                category_clause = " OR ".join([f"{self._quote(c)} = ?" for c in category_cols])
                clauses.append(f"({category_clause})")
                params.extend([category] * len(category_cols))

        if intent:
            intent_cols = [c for c in ("intent", "main_intent", "sub_intent") if c in self._columns]
            if intent_cols:
                intent_clause = " OR ".join([f"{self._quote(c)} = ?" for c in intent_cols])
                clauses.append(f"({intent_clause})")
                params.extend([intent] * len(intent_cols))

        where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        return where_sql, params

    def _fts_search_sync(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = self._normalize_query(query)
        if not query:
            return []

        self._load_schema()
        if self._table_name != "knowledge":
            return self._fallback_like_sync(query, limit, category, intent)

        try:
            with self._connect() as conn:
                where_sql, params = self._pick_filter_sql(category, intent)
                sql = f"""
                    SELECT
                        k.*,
                        bm25(knowledge_fts) AS score,
                        snippet(knowledge_fts, 2, '[', ']', '…', 24) AS snippet
                    FROM knowledge_fts
                    JOIN knowledge k ON k.id = knowledge_fts.rowid
                    WHERE knowledge_fts MATCH ?
                    {where_sql}
                    ORDER BY score ASC,
                             COALESCE(CAST(k.priority AS REAL), 0) DESC,
                             COALESCE(CAST(k.confidence AS REAL), 0) DESC,
                             COALESCE(k.updated_at, k.created_at, '') DESC
                    LIMIT ?
                """
                rows = conn.execute(sql, [query, *params, limit]).fetchall()
                return [dict(row) for row in rows]
        except Exception:
            return self._fallback_like_sync(query, limit, category, intent)

    def _fallback_like_sync(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = self._normalize_query(query)
        if not query:
            return []

        self._load_schema()
        if not self._table_name:
            return []

        text_cols = self._pick_text_cols()
        if not text_cols:
            return []

        words = [w for w in query.split() if len(w) > 1]
        if not words:
            words = [query]

        where_parts: list[str] = []
        params: list[Any] = []

        for word in words:
            like_or: list[str] = []
            for col in text_cols:
                like_or.append(f"COALESCE(CAST({self._quote(col)} AS TEXT), '') LIKE ?")
                params.append(f"%{word}%")
            where_parts.append("(" + " OR ".join(like_or) + ")")

        filter_sql, filter_params = self._pick_filter_sql(category, intent)
        full_where = " WHERE " + " AND ".join(where_parts)
        if filter_sql:
            full_where += " AND " + filter_sql[7:]

        sql = f"""
            SELECT *
            FROM {self._quote(self._table_name)}
            {full_where}
            {self._pick_order_sql()}
            LIMIT ?
        """

        with self._connect() as conn:
            rows = conn.execute(sql, [*params, *filter_params, limit]).fetchall()
            return [dict(row) for row in rows]

    async def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(
            self._fts_search_sync,
            query,
            limit,
            category,
            intent,
        )

    async def get_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        def _sync() -> Optional[Dict[str, Any]]:
            self._load_schema()
            if not self._table_name:
                return None

            with self._connect() as conn:
                if "id" in self._columns:
                    row = conn.execute(
                        f"SELECT * FROM {self._quote(self._table_name)} WHERE id = ?",
                        (doc_id,),
                    ).fetchone()
                else:
                    row = conn.execute(
                        f"SELECT rowid AS id, * FROM {self._quote(self._table_name)} WHERE rowid = ?",
                        (doc_id,),
                    ).fetchone()
                return dict(row) if row else None

        return await asyncio.to_thread(_sync)

    async def stats(self) -> Dict[str, Any]:
        def _sync() -> Dict[str, Any]:
            self._load_schema()
            if not self._table_name:
                return {"total": 0, "categories": 0, "intents": 0, "table": None}

            with self._connect() as conn:
                total_sql = f"SELECT COUNT(*) FROM {self._quote(self._table_name)}"
                if "is_deleted" in self._columns:
                    total_sql += " WHERE COALESCE(is_deleted, 0) = 0"
                total = conn.execute(total_sql).fetchone()[0]

                cats = 0
                if "category" in self._columns:
                    cats = conn.execute(
                        f"SELECT COUNT(DISTINCT category) FROM {self._quote(self._table_name)}"
                    ).fetchone()[0]

                intents = 0
                if "intent" in self._columns:
                    intents = conn.execute(
                        f"SELECT COUNT(DISTINCT intent) FROM {self._quote(self._table_name)}"
                    ).fetchone()[0]

                return {
                    "total": total,
                    "categories": cats,
                    "intents": intents,
                    "table": self._table_name,
                }

        return await asyncio.to_thread(_sync)
