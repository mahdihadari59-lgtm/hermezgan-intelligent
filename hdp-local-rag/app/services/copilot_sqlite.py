from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_DB = "/data/data/com.termux/files/home/hermezgan-intelligent/backend/data/hdp_v2.db"

class SQLiteCopilotSearch:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or os.getenv("HDP_RAG_DB_PATH") or DEFAULT_DB

    def connect(self) -> sqlite3.Connection:
        if not self.db_path:
            raise RuntimeError("DB_PATH_NOT_SET")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _table_exists(self, conn: sqlite3.Connection, table: str) -> bool:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name = ?",
            (table,),
        ).fetchone()
        return row is not None

    def _columns(self, conn: sqlite3.Connection, table: str) -> List[str]:
        if not self._table_exists(conn, table):
            return []
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return [r["name"] for r in rows]

    def _pick(self, cols: Sequence[str], names: Sequence[str]) -> Optional[str]:
        lower = {c.lower(): c for c in cols}
        for n in names:
            if n.lower() in lower:
                return lower[n.lower()]
        return None

    def _tokens(self, q: str) -> List[str]:
        tokens = []
        seen = set()
        for raw in str(q).replace("،", " ").replace(",", " ").split():
            t = raw.strip().lower()
            if len(t) >= 2 and t not in seen:
                tokens.append(t)
                seen.add(t)
        return tokens

    def _row(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {k: row[k] for k in row.keys()}

    def _simplify(self, rec: Dict[str, Any], table: str, score: float = 0.0) -> Dict[str, Any]:
        return {
            "table": table,
            "id": rec.get("id") or rec.get("rowid") or rec.get("knowledge_id") or rec.get("doc_id"),
            "title": rec.get("title") or rec.get("name") or rec.get("question") or rec.get("heading") or rec.get("topic") or "",
            "content": rec.get("content") or rec.get("body") or rec.get("text") or rec.get("description") or rec.get("answer") or rec.get("chunk_text") or rec.get("passage") or rec.get("excerpt") or "",
            "category": rec.get("category") or rec.get("section") or rec.get("type"),
            "source": rec.get("source") or rec.get("origin") or rec.get("doc_source"),
            "score": float(score),
            "raw": rec,
        }

    def search_fts(self, q: str, limit: int = 8) -> List[Dict[str, Any]]:
        conn = self.connect()
        try:
            if not self._table_exists(conn, "knowledge_fts"):
                return []
            try:
                rows = conn.execute(
                    "SELECT rowid AS id, * FROM knowledge_fts WHERE knowledge_fts MATCH ? LIMIT ?",
                    (q, limit),
                ).fetchall()
                return [self._simplify(self._row(r), "knowledge_fts", 0.95) for r in rows]
            except sqlite3.Error:
                return []
        finally:
            conn.close()

    def search_like(self, q: str, limit: int = 8) -> List[Dict[str, Any]]:
        conn = self.connect()
        try:
            if not self._table_exists(conn, "knowledge"):
                return []
            cols = self._columns(conn, "knowledge")
            title_col = self._pick(cols, ["title", "name", "question", "heading", "topic"])
            content_col = self._pick(cols, ["content", "body", "text", "description", "answer", "summary"])
            category_col = self._pick(cols, ["category", "section", "type"])
            if not title_col and not content_col and not category_col:
                return []
            tokens = self._tokens(q)[:5] or [str(q).strip()]
            clauses = []
            params: List[Any] = []
            for token in tokens:
                frag = "%" + token.replace("%", r"\%").replace("_", r"\_") + "%"
                if title_col:
                    clauses.append(f"lower({title_col}) LIKE lower(?) ESCAPE '\\\\'")
                    params.append(frag)
                if content_col:
                    clauses.append(f"lower({content_col}) LIKE lower(?) ESCAPE '\\\\'")
                    params.append(frag)
                if category_col:
                    clauses.append(f"lower({category_col}) LIKE lower(?) ESCAPE '\\\\'")
                    params.append(frag)
            sql = f"SELECT rowid AS id, * FROM knowledge WHERE {' OR '.join(clauses)} LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [self._simplify(self._row(r), "knowledge", 0.62) for r in rows]
        except sqlite3.Error:
            return []
        finally:
            conn.close()

    def search_embeddings(self, q: str, limit: int = 16) -> List[Dict[str, Any]]:
        conn = self.connect()
        try:
            if not self._table_exists(conn, "knowledge_embeddings"):
                return []
            rows = conn.execute("SELECT rowid AS id, * FROM knowledge_embeddings LIMIT ?", (limit,)).fetchall()
            tokens = self._tokens(q)
            items = []
            for r in rows:
                rec = self._row(r)
                text = f"{rec.get('title','')} {rec.get('content','')} {rec.get('text','')} {rec.get('chunk_text','')}".lower()
                overlap = sum(1 for t in tokens if t in text) / max(len(tokens), 1) if tokens else 0.0
                score = 0.35 + overlap * 0.55
                items.append(self._simplify(rec, "knowledge_embeddings", score))
            return sorted(items, key=lambda x: x["score"], reverse=True)[:limit]
        finally:
            conn.close()

    def search_relations(self, ids: Sequence[Any], limit: int = 8) -> List[Dict[str, Any]]:
        conn = self.connect()
        try:
            if not self._table_exists(conn, "knowledge_relations") or not ids:
                return []
            cols = self._columns(conn, "knowledge_relations")
            s_col = self._pick(cols, ["source_id", "from_id", "parent_id", "knowledge_id", "src_id"])
            t_col = self._pick(cols, ["target_id", "to_id", "child_id", "dst_id"])
            rel_col = self._pick(cols, ["relation", "type", "label", "predicate", "edge_type"])
            conds = []
            params: List[Any] = []
            if s_col:
                conds.append(f"{s_col} IN ({','.join(['?'] * len(ids))})")
                params.extend(ids)
            if t_col:
                conds.append(f"{t_col} IN ({','.join(['?'] * len(ids))})")
                params.extend(ids)
            if not conds:
                return []
            sql = f"SELECT rowid AS id, * FROM knowledge_relations WHERE {' OR '.join(conds)} LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, tuple(params)).fetchall()
            out = []
            for r in rows:
                rec = self._row(r)
                out.append({
                    "table": "knowledge_relations",
                    "id": rec.get("id"),
                    "source_id": rec.get(s_col) if s_col else None,
                    "target_id": rec.get(t_col) if t_col else None,
                    "relation": rec.get(rel_col) if rel_col else None,
                    "raw": rec,
                    "score": 0.5,
                    "title": rec.get(rel_col) or "relation",
                    "content": "",
                    "category": "graph",
                })
            return out
        finally:
            conn.close()

    def search(self, q: str, limit: int = 5) -> Dict[str, Any]:
        fts = self.search_fts(q, limit=max(limit * 3, 8))
        emb = self.search_embeddings(q, limit=max(limit * 3, 8))
        like = self.search_like(q, limit=max(limit * 3, 8))
        all_items = fts + emb + like

        seen = set()
        unique = []
        for item in all_items:
            key = f"{item.get('table')}::{item.get('title')}::{item.get('content')}".lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)

        tokens = self._tokens(q)
        def rank(item: Dict[str, Any]) -> float:
            base = float(item.get("score", 0.0))
            text = f"{item.get('title','')} {item.get('content','')}".lower()
            overlap = sum(1 for t in tokens if t in text) / max(len(tokens), 1) if tokens else 0.0
            return base * 0.6 + overlap * 0.4

        ranked = sorted(unique, key=rank, reverse=True)
        top = ranked[:limit]
        ids = [x.get("id") for x in top if x.get("id") is not None]
        rels = self.search_relations(ids, limit=8) if ids else []

        return {
            "items": top,
            "relations": rels,
            "debug": {"counts": {"fts": len(fts), "embedding": len(emb), "like": len(like), "relations": len(rels)}},
        }
