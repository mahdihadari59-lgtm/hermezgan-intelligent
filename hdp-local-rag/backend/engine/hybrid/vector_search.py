#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/vector_search.py
-------------------------------------------------------
موتور جستجوی برداری مستقل HDP.

ترکیب دو روش کلاسیک:
    1) BM25
    2) TF-IDF cosine similarity (سبک و self-contained)

نتایج دو روش با Reciprocal Rank Fusion (RRF) ترکیب می‌شوند.

این نسخه به storage خارجی وابسته نیست و روی SQLite داخلی
پروژه کار می‌کند.
-------------------------------------------------------
"""

from __future__ import annotations

import math
import sqlite3
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from engine.hybrid.config import HybridConfig
from engine.hybrid.graph_builder import normalize_persian

RRF_K = HybridConfig.RRF_K


class VectorSearchEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or HybridConfig.DB_PATH
        HybridConfig.ensure_data_dir()
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS term_frequencies (
                    node_id INTEGER NOT NULL,
                    term TEXT NOT NULL,
                    tf INTEGER NOT NULL,
                    PRIMARY KEY (node_id, term)
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tf_term ON term_frequencies(term)")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS doc_length (
                    node_id INTEGER PRIMARY KEY,
                    length INTEGER NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS corpus_stats (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [t for t in normalize_persian(text).split(" ") if t]

    def build_index(self, domains: Optional[List[str]] = None) -> Dict[str, Any]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("BEGIN")

            if domains:
                placeholders = ",".join("?" for _ in domains)
                sql = f"""
                    SELECT
                        g.id AS node_id,
                        g.title AS title,
                        g.node_type AS node_type,
                        k.content AS content,
                        k.category AS category,
                        k.topic AS topic,
                        k.keywords AS keywords,
                        k.tags AS tags,
                        k.subcategory AS subcategory,
                        k.city AS city,
                        k.source AS source
                    FROM graph_nodes g
                    JOIN knowledge k ON k.id = g.knowledge_id
                    WHERE k.is_deleted = 0
                      AND (
                          k.category IN ({placeholders})
                          OR k.topic IN ({placeholders})
                          OR k.subcategory IN ({placeholders})
                      )
                """
                params = list(domains) + list(domains) + list(domains)
                cur.execute(sql, params)
            else:
                cur.execute(
                    """
                    SELECT
                        g.id AS node_id,
                        g.title AS title,
                        g.node_type AS node_type,
                        k.content AS content,
                        k.category AS category,
                        k.topic AS topic,
                        k.keywords AS keywords,
                        k.tags AS tags,
                        k.subcategory AS subcategory,
                        k.city AS city,
                        k.source AS source
                    FROM graph_nodes g
                    JOIN knowledge k ON k.id = g.knowledge_id
                    WHERE k.is_deleted = 0
                    """
                )

            rows = cur.fetchall()

            cur.execute("DELETE FROM term_frequencies")
            cur.execute("DELETE FROM doc_length")
            cur.execute("DELETE FROM corpus_stats")

            doc_freq: Counter[str] = Counter()
            doc_term_counts: Dict[int, Counter[str]] = {}
            total_length = 0

            for row in rows:
                node_id = int(row["node_id"])
                text = " ".join(
                    str(part or "")
                    for part in (
                        row["title"],
                        row["content"],
                        row["category"],
                        row["topic"],
                        row["keywords"],
                        row["tags"],
                        row["subcategory"],
                        row["city"],
                        row["source"],
                        row["node_type"],
                    )
                )
                tokens = self._tokenize(text)
                counts = Counter(tokens)
                doc_term_counts[node_id] = counts
                total_length += len(tokens)

                cur.executemany(
                    "INSERT INTO term_frequencies (node_id, term, tf) VALUES (?, ?, ?)",
                    [(node_id, term, tf) for term, tf in counts.items()],
                )
                cur.execute(
                    "INSERT INTO doc_length (node_id, length) VALUES (?, ?)",
                    (node_id, len(tokens)),
                )

                for term in counts:
                    doc_freq[term] += 1

            n_docs = len(rows)
            avgdl = (total_length / n_docs) if n_docs else 0.0

            cur.execute("INSERT INTO corpus_stats (key, value) VALUES (?, ?)", ("n_docs", str(n_docs)))
            cur.execute("INSERT INTO corpus_stats (key, value) VALUES (?, ?)", ("avgdl", str(avgdl)))

            conn.commit()
            return {"n_docs": n_docs, "n_terms": len(doc_freq), "avgdl": round(avgdl, 2)}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _load_corpus_stats(self, cur: sqlite3.Cursor) -> Tuple[int, float]:
        cur.execute("SELECT value FROM corpus_stats WHERE key='n_docs'")
        row = cur.fetchone()
        n_docs = int(row["value"]) if row and row["value"] else 0

        cur.execute("SELECT value FROM corpus_stats WHERE key='avgdl'")
        row = cur.fetchone()
        avgdl = float(row["value"]) if row and row["value"] else 1.0

        return n_docs, avgdl

    def _candidate_ids(self, terms: List[str], domains: Optional[List[str]] = None) -> List[int]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            term_placeholders = ",".join("?" for _ in terms)

            if domains:
                domain_placeholders = ",".join("?" for _ in domains)
                cur.execute(
                    f"""
                    SELECT DISTINCT tf.node_id
                    FROM term_frequencies tf
                    JOIN graph_nodes g ON g.id = tf.node_id
                    JOIN knowledge k ON k.id = g.knowledge_id
                    WHERE tf.term IN ({term_placeholders})
                      AND k.is_deleted = 0
                      AND (
                          k.category IN ({domain_placeholders})
                          OR k.topic IN ({domain_placeholders})
                          OR k.subcategory IN ({domain_placeholders})
                      )
                    LIMIT 1000
                    """,
                    terms + domains + domains + domains,
                )
            else:
                cur.execute(
                    f"""
                    SELECT DISTINCT tf.node_id
                    FROM term_frequencies tf
                    JOIN graph_nodes g ON g.id = tf.node_id
                    JOIN knowledge k ON k.id = g.knowledge_id
                    WHERE tf.term IN ({term_placeholders})
                      AND k.is_deleted = 0
                    LIMIT 1000
                    """,
                    terms,
                )

            return [int(r["node_id"]) for r in cur.fetchall()]
        finally:
            conn.close()

    def _bm25_scores(
        self,
        terms: List[str],
        candidate_ids: List[int],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> Dict[int, float]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            n_docs, avgdl = self._load_corpus_stats(cur)

            if not n_docs or not candidate_ids or not terms:
                return {}

            placeholders = ",".join("?" for _ in candidate_ids)
            term_placeholders = ",".join("?" for _ in terms)

            cur.execute(
                f"SELECT node_id, length FROM doc_length WHERE node_id IN ({placeholders})",
                candidate_ids,
            )
            doc_lengths = {int(r["node_id"]): int(r["length"]) for r in cur.fetchall()}

            cur.execute(
                f"""
                SELECT node_id, term, tf
                FROM term_frequencies
                WHERE node_id IN ({placeholders})
                  AND term IN ({term_placeholders})
                """,
                candidate_ids + terms,
            )

            tf_map: Dict[int, Dict[str, int]] = {}
            for r in cur.fetchall():
                tf_map.setdefault(int(r["node_id"]), {})[str(r["term"])] = int(r["tf"])

            cur.execute(
                f"""
                SELECT term, COUNT(DISTINCT node_id) AS df
                FROM term_frequencies
                WHERE term IN ({term_placeholders})
                GROUP BY term
                """,
                terms,
            )
            df_map = {str(r["term"]): int(r["df"]) for r in cur.fetchall()}

            scores: Dict[int, float] = {}
            for node_id in candidate_ids:
                doc_len = doc_lengths.get(node_id, 1) or 1
                score = 0.0

                for term in terms:
                    tf = tf_map.get(node_id, {}).get(term, 0)
                    if not tf:
                        continue

                    df = df_map.get(term, 0)
                    idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
                    denom = tf + k1 * (1.0 - b + b * doc_len / max(avgdl, 1e-9))
                    score += idf * ((tf * (k1 + 1.0)) / denom)

                if score > 0:
                    scores[node_id] = score

            return scores
        finally:
            conn.close()

    def _tfidf_cosine_scores(self, terms: List[str], candidate_ids: List[int]) -> Dict[int, float]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            n_docs, _avgdl = self._load_corpus_stats(cur)

            if not n_docs or not candidate_ids or not terms:
                return {}

            placeholders = ",".join("?" for _ in candidate_ids)
            cur.execute(
                f"""
                SELECT node_id, term, tf
                FROM term_frequencies
                WHERE node_id IN ({placeholders})
                """,
                candidate_ids,
            )

            doc_term_counts: Dict[int, Dict[str, int]] = {}
            all_doc_terms: List[str] = []
            for r in cur.fetchall():
                node_id = int(r["node_id"])
                term = str(r["term"])
                tf = int(r["tf"])
                doc_term_counts.setdefault(node_id, {})[term] = tf
                all_doc_terms.append(term)

            unique_terms = sorted(set(terms + all_doc_terms))
            if not unique_terms:
                return {}

            unique_placeholders = ",".join("?" for _ in unique_terms)
            cur.execute(
                f"""
                SELECT term, COUNT(DISTINCT node_id) AS df
                FROM term_frequencies
                WHERE term IN ({unique_placeholders})
                GROUP BY term
                """,
                unique_terms,
            )
            df_map = {str(r["term"]): int(r["df"]) for r in cur.fetchall()}

            def idf(term: str) -> float:
                df = df_map.get(term, 0)
                return math.log((1 + n_docs) / (1 + df)) + 1.0

            query_vec = {term: 1.0 * idf(term) for term in terms}
            qnorm = math.sqrt(sum(weight * weight for weight in query_vec.values()))
            if qnorm == 0:
                return {}

            scores: Dict[int, float] = {}
            for node_id, counts in doc_term_counts.items():
                dot = 0.0
                doc_norm_sq = 0.0

                for term, tf in counts.items():
                    weight = tf * idf(term)
                    doc_norm_sq += weight * weight
                    if term in query_vec:
                        dot += query_vec[term] * weight

                doc_norm = math.sqrt(doc_norm_sq)
                if doc_norm > 0 and dot > 0:
                    scores[node_id] = dot / (qnorm * doc_norm)

            return scores
        finally:
            conn.close()

    @staticmethod
    def _rrf(ranked_lists: List[List[Tuple[int, float]]], k: int = RRF_K) -> Dict[int, float]:
        fused: Dict[int, float] = {}
        for ranked in ranked_lists:
            for rank, (node_id, _score) in enumerate(ranked, start=1):
                fused[node_id] = fused.get(node_id, 0.0) + 1.0 / (k + rank)
        return fused

    def _materialize(self, node_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not node_ids:
            return {}

        conn = self._connect()
        try:
            cur = conn.cursor()
            placeholders = ",".join("?" for _ in node_ids)
            cur.execute(
                f"""
                SELECT
                    g.id AS id,
                    g.title AS title,
                    g.node_type AS node_type,
                    g.knowledge_id AS knowledge_id,
                    k.category AS category,
                    k.topic AS topic,
                    k.keywords AS keywords,
                    k.tags AS tags,
                    k.subcategory AS subcategory,
                    k.city AS city,
                    k.source AS source,
                    substr(k.content, 1, 240) AS content_excerpt
                FROM graph_nodes g
                JOIN knowledge k ON k.id = g.knowledge_id
                WHERE g.id IN ({placeholders})
                """,
                node_ids,
            )
            out: Dict[int, Dict[str, Any]] = {}
            for r in cur.fetchall():
                row = dict(r)
                out[int(row["id"])] = row
            return out
        finally:
            conn.close()

    def search(self, query: str, top_k: int = 10, domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        normalized = normalize_persian(query)
        terms = [t for t in normalized.split(" ") if t]
        if not terms:
            return []

        candidate_ids = self._candidate_ids(terms, domains=domains)
        if not candidate_ids:
            return []

        bm25_scores = self._bm25_scores(terms, candidate_ids)
        cosine_scores = self._tfidf_cosine_scores(terms, candidate_ids)

        bm25_ranked = sorted(bm25_scores.items(), key=lambda kv: kv[1], reverse=True)
        cosine_ranked = sorted(cosine_scores.items(), key=lambda kv: kv[1], reverse=True)
        fused_scores = self._rrf([bm25_ranked, cosine_ranked])

        ordered = sorted(fused_scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        meta = self._materialize([node_id for node_id, _score in ordered])

        results: List[Dict[str, Any]] = []
        for node_id, fused_score in ordered:
            info = meta.get(node_id, {})
            results.append(
                {
                    "id": node_id,
                    "score": round(fused_score, 4),
                    "bm25": round(bm25_scores.get(node_id, 0.0), 4),
                    "cosine": round(cosine_scores.get(node_id, 0.0), 4),
                    "title": info.get("title"),
                    "category": info.get("category"),
                    "topic": info.get("topic"),
                    "keywords": info.get("keywords"),
                    "tags": info.get("tags"),
                    "content": info.get("content_excerpt"),
                }
            )
        return results


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="HDP Standalone Vector Search")
    parser.add_argument("--db", default=None, help="پیش‌فرض: مسیر تعریف‌شده در config.py")
    parser.add_argument("--build-index", action="store_true")
    parser.add_argument("--query", default=None)
    parser.add_argument("--top_k", type=int, default=10)
    args = parser.parse_args()

    engine = VectorSearchEngine(args.db)
    if args.build_index:
        stats = engine.build_index()
        print(json.dumps({"index_built": stats}, ensure_ascii=False, indent=2))
    if args.query:
        results = engine.search(args.query, top_k=args.top_k)
        print(json.dumps(results, ensure_ascii=False, indent=2))
