from __future__ import annotations

import math
import os
import re
import sqlite3
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_DB = "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"

TEXT_COL_HINTS = (
    "title", "name", "question", "heading", "topic", "label",
    "content", "body", "text", "description", "answer", "summary",
    "excerpt", "chunk_text", "passage", "note", "details", "message",
)

class DBIntelligenceService:
    """
    Stage 7:
    - uses the real /data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db
    - introspects tables / columns
    - table-aware retrieval with generic ranking
    """

    def __init__(self, db_path: Optional[str] = None, max_per_table: int = 5) -> None:
        self.db_path = db_path or os.getenv("HDP_RAG_DB_PATH") or DEFAULT_DB
        self.max_per_table = max_per_table
        self._schema_cache: Dict[str, List[str]] = {}

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _table_exists(self, conn: sqlite3.Connection, table: str) -> bool:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name=?",
            (table,),
        ).fetchone()
        return row is not None

    def _tables(self, conn: sqlite3.Connection) -> List[str]:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
        ).fetchall()
        return [r["name"] for r in rows]

    def _columns(self, conn: sqlite3.Connection, table: str) -> List[str]:
        if table in self._schema_cache:
            return self._schema_cache[table]
        if not self._table_exists(conn, table):
            return []
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        cols = [r["name"] for r in rows]
        self._schema_cache[table] = cols
        return cols

    def _pick_cols(self, cols: Sequence[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        lower = {c.lower(): c for c in cols}
        title = next((lower[x] for x in ("title", "name", "question", "heading", "topic", "label") if x in lower), None)
        content = next((lower[x] for x in ("content", "body", "text", "description", "answer", "summary", "excerpt", "chunk_text", "passage", "note", "details", "message") if x in lower), None)
        cat = next((lower[x] for x in ("category", "type", "section", "group", "kind", "intent") if x in lower), None)
        return title, content, cat

    def _tokens(self, query: str) -> List[str]:
        out: List[str] = []
        seen = set()
        for raw in re.split(r"[\s،,;:]+", query or ""):
            t = raw.strip().lower()
            if len(t) >= 2 and t not in seen:
                out.append(t)
                seen.add(t)
        return out

    def _row(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {k: row[k] for k in row.keys()}

    def _simplify(self, table: str, rec: Dict[str, Any], score: float, note: str = "") -> Dict[str, Any]:
        title = rec.get("title") or rec.get("name") or rec.get("question") or rec.get("heading") or rec.get("topic") or rec.get("label") or ""
        content = rec.get("content") or rec.get("body") or rec.get("text") or rec.get("description") or rec.get("answer") or rec.get("summary") or rec.get("excerpt") or rec.get("chunk_text") or rec.get("passage") or ""
        return {
            "table": table,
            "id": rec.get("id") or rec.get("rowid") or rec.get("knowledge_id") or rec.get("doc_id") or rec.get("source_id") or rec.get("target_id"),
            "title": str(title),
            "content": str(content),
            "category": rec.get("category") or rec.get("type") or rec.get("section"),
            "source": rec.get("source") or rec.get("origin") or rec.get("doc_source"),
            "score": float(score),
            "note": note,
            "raw": rec,
        }

    def _token_overlap(self, query: str, text: str) -> float:
        tokens = self._tokens(query)
        if not tokens:
            return 0.0
        hay = (text or "").lower()
        hits = sum(1 for t in tokens if t in hay)
        return hits / max(len(tokens), 1)

    def _like_frag(self, s: str) -> str:
        return "%" + s.replace("%", r"\%").replace("_", r"\_") + "%"

    def _generic_table_search(self, conn: sqlite3.Connection, table: str, query: str, limit: int) -> List[Dict[str, Any]]:
        cols = self._columns(conn, table)
        if not cols:
            return []
        title_col, content_col, cat_col = self._pick_cols(cols)
        if not title_col and not content_col and not cat_col:
            return []

        tokens = self._tokens(query)[:5] or [query.strip()]
        clauses = []
        params: List[Any] = []
        for tok in tokens:
            frag = self._like_frag(tok)
            if title_col:
                clauses.append(f"lower({title_col}) LIKE lower(?) ESCAPE '\\'")
                params.append(frag)
            if content_col:
                clauses.append(f"lower({content_col}) LIKE lower(?) ESCAPE '\\'")
                params.append(frag)
            if cat_col:
                clauses.append(f"lower({cat_col}) LIKE lower(?) ESCAPE '\\'")
                params.append(frag)

        if not clauses:
            return []

        sql = f"SELECT rowid AS id, * FROM {table} WHERE {' OR '.join(clauses)} LIMIT ?"
        params.append(limit)
        try:
            rows = conn.execute(sql, tuple(params)).fetchall()
        except sqlite3.Error:
            return []

        results = []
        for row in rows:
            rec = self._row(row)
            text_blob = f"{rec.get(title_col or 'title', '')} {rec.get(content_col or 'content', '')} {rec.get(cat_col or 'category', '')}"
            overlap = self._token_overlap(query, text_blob)
            score = 0.42 + (overlap * 0.45)
            results.append(self._simplify(table, rec, score))
        return results

    def _fts_search(self, conn: sqlite3.Connection, query: str, limit: int) -> List[Dict[str, Any]]:
        if not self._table_exists(conn, "knowledge_fts"):
            return []

        safe_query = query.replace('"', '""').strip()
        if not safe_query:
            return []
        words = safe_query.split()
        fts_query = " AND ".join(f'"{w}"' for w in words if len(w) > 1)
        if not fts_query:
            fts_query = f'"{safe_query}"'

        try:
            rows = conn.execute(
                "SELECT rowid AS id, * FROM knowledge_fts WHERE knowledge_fts MATCH ? LIMIT ?",
                (fts_query, limit),
            ).fetchall()
        except sqlite3.Error as e:
            logging.getLogger("hdp.db_intelligence").warning(f"FTS MATCH error: {e}, falling back to LIKE")
            try:
                pattern = f"%{query}%"
                rows = conn.execute(
                    "SELECT rowid AS id, * FROM knowledge WHERE title LIKE ? OR content LIKE ? LIMIT ?",
                    (pattern, pattern, limit),
                ).fetchall()
            except sqlite3.Error:
                return []

        results = []
        for row in rows:
            rec = self._row(row)
            results.append(self._simplify("knowledge_fts", rec, 0.97, "fts5"))
        return results

    def _embedding_search(self, conn: sqlite3.Connection, query: str, limit: int) -> List[Dict[str, Any]]:
        if not self._table_exists(conn, "knowledge_embeddings"):
            return []
        try:
            rows = conn.execute(
                "SELECT rowid AS id, * FROM knowledge_embeddings LIMIT ?",
                (max(limit * 8, 24),),
            ).fetchall()
        except sqlite3.Error:
            return []

        tokens = self._tokens(query)
        results = []
        for row in rows:
            rec = self._row(row)
            text_blob = " ".join(str(rec.get(k, "")) for k in ("title", "name", "content", "text", "chunk_text", "passage", "excerpt", "description", "answer"))
            overlap = self._token_overlap(query, text_blob)
            score = 0.36 + (overlap * 0.54)
            if tokens:
                results.append(self._simplify("knowledge_embeddings", rec, score, "semantic"))
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _graph_search(self, conn: sqlite3.Connection, query: str, limit: int, table: str) -> List[Dict[str, Any]]:
        if not self._table_exists(conn, table):
            return []
        cols = self._columns(conn, table)
        if not cols:
            return []
        try:
            rows = conn.execute(f"SELECT rowid AS id, * FROM {table} LIMIT ?", (max(limit * 5, 20),)).fetchall()
        except sqlite3.Error:
            return []

        results = []
        for row in rows:
            rec = self._row(row)
            text_blob = " ".join(str(rec.get(c, "")) for c in cols)
            overlap = self._token_overlap(query, text_blob)
            if overlap <= 0:
                continue
            results.append(self._simplify(table, rec, 0.3 + (overlap * 0.6), "graph"))
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _unified_search(self, conn: sqlite3.Connection, query: str, limit: int) -> List[Dict[str, Any]]:
        candidates = []
        for table in ("unified_search", "search_index", "search_all", "knowledge_search", "search_keywords"):
            if self._table_exists(conn, table):
                candidates.extend(self._generic_table_search(conn, table, query, limit))
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:limit]

    def _table_candidates(self, plan: Dict[str, Any]) -> List[str]:
        targets = list(plan.get("table_targets") or [])
        defaults = [
            "knowledge", "knowledge_fts", "knowledge_embeddings",
            "knowledge_graph", "knowledge_nodes", "knowledge_edges",
            "graph_nodes", "graph_edges", "semantic_relations", "unified_search",
            "search_index", "query_routes", "intent_mapping", "expert_mapping",
            "response_templates", "conversation_context", "conversation_memory",
            "knowledge_links", "knowledge_relations", "knowledge_search",
            "traffic_cameras", "traffic_blackspots", "traffic_accidents",
            "hospitals", "clinics", "pharmacies", "hotels", "restaurants",
            "places", "businesses", "attractions", "fuel_stations",
            "police_stations", "police_services",
        ]
        for t in defaults:
            if t not in targets:
                targets.append(t)
        return targets

    def search(self, query: str, plan: Optional[Dict[str, Any]] = None, limit: int = 8) -> Dict[str, Any]:
        plan = plan or {}
        conn = self._connect()
        try:
            tables = self._table_candidates(plan)
            results: List[Dict[str, Any]] = []
            counts: Dict[str, int] = {}

            # Stage-specific searches first
            if plan.get("needs_fts", True):
                fts = self._fts_search(conn, query, limit=max(limit * 2, 10))
                results.extend(fts)
                counts["fts"] = len(fts)

            if plan.get("needs_embedding", True):
                emb = self._embedding_search(conn, query, limit=max(limit * 2, 10))
                results.extend(emb)
                counts["embedding"] = len(emb)

            # Unified / generic tables
            unified = self._unified_search(conn, query, limit=max(limit * 2, 10))
            results.extend(unified)
            counts["unified"] = len(unified)

            # Table-aware searches
            for table in tables:
                if table in ("knowledge_fts", "knowledge_embeddings"):
                    continue
                if not self._table_exists(conn, table):
                    continue
                items = self._generic_table_search(conn, table, query, self.max_per_table)
                if table in ("knowledge_graph", "knowledge_nodes", "knowledge_edges", "graph_nodes", "graph_edges", "semantic_relations", "knowledge_relations"):
                    items += self._graph_search(conn, query, self.max_per_table, table)
                if items:
                    results.extend(items)
                    counts[table] = len(items)

            # normalize / rank / dedupe
            dedup: Dict[str, Dict[str, Any]] = {}
            for item in results:
                key = f"{item.get('table')}::{item.get('title')}::{item.get('content')}".lower().strip()
                prev = dedup.get(key)
                if not prev or float(item.get("score", 0)) > float(prev.get("score", 0)):
                    dedup[key] = item

            ranked = sorted(dedup.values(), key=lambda x: float(x.get("score", 0)), reverse=True)
            top = ranked[:limit]

            return {
                "items": top,
                "tables_scanned": tables,
                "table_hits": counts,
                "db_path": self.db_path,
            }
        finally:
            conn.close()

    def health(self) -> Dict[str, Any]:
        try:
            conn = self._connect()
            try:
                tables = self._tables(conn)
                return {
                    "ok": True,
                    "db_path": self.db_path,
                    "db_exists": Path(self.db_path).exists(),
                    "tables": len(tables),
                }
            finally:
                conn.close()
        except Exception as e:
            return {
                "ok": False,
                "db_path": self.db_path,
                "error": str(e),
            }
