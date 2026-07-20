#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/vector_search.py
-------------------------------------------------------
موتور جستجوی برداری مستقل HDP (بدون هیچ وابستگی خارجی).

ترکیب دو روش کلاسیک:
    1) BM25 (k1=1.5, b=0.75) — بر پایه فراوانی کلمه و طول سند
    2) TF-IDF cosine similarity — بر پایه بردار وزن‌دار کلمات

نتایج دو روش با Reciprocal Rank Fusion (RRF) ترکیب می‌شوند:
    score(doc) = Σ 1 / (k + rank_i(doc))   با k=60 (مقدار استاندارد رایج)

این فایل عمداً مستقل از hybrid_engine.py است تا هم به‌تنهایی
قابل تست/استفاده باشد، هم بعداً به‌عنوان vector_search_fn به
HybridEngine تزریق شود.

ایندکس (تعداد تکرار کلمه در هر سند، طول سند) در SQLite ذخیره
می‌شود تا نیازی به بازسازی کامل در هر بار اجرا نباشد.
-------------------------------------------------------
"""

import sqlite3
import math
from typing import Optional, List, Dict, Tuple
from collections import Counter

from engine.hybrid.graph_builder import normalize_persian
from engine.hybrid.embedding_storage import EmbeddingStorage
from engine.hybrid.config import HybridConfig

RRF_K = HybridConfig.RRF_K


class VectorSearchEngine:
    def __init__(self, db_path: Optional[str] = None, embedding_storage: Optional[EmbeddingStorage] = None):
        self.db_path = db_path or HybridConfig.DB_PATH
        HybridConfig.ensure_data_dir()
        self.storage = embedding_storage or EmbeddingStorage(self.db_path)
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

    # -----------------------------------------------------
    # ساخت ایندکس (باید بعد از هر تغییر بزرگ در graph_nodes اجرا شود)
    # -----------------------------------------------------
    def build_index(self, domains: Optional[List[str]] = None) -> Dict[str, int]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            if domains:
                placeholders = ",".join("?" for _ in domains)
                cur.execute(
                    f"SELECT id, title, content FROM graph_nodes WHERE domain IN ({placeholders})",
                    domains,
                )
            else:
                cur.execute("SELECT id, title, content FROM graph_nodes")
            nodes = cur.fetchall()

            cur.execute("DELETE FROM term_frequencies")
            cur.execute("DELETE FROM doc_length")

            doc_freq: Counter = Counter()  # تعداد سندهایی که هر term حداقل یک‌بار داخلشونه
            total_length = 0
            tfidf_vectors: Dict[int, Dict[str, float]] = {}
            doc_term_counts: Dict[int, Counter] = {}

            for node in nodes:
                text = f"{node['title'] or ''} {node['content'] or ''}"
                tokens = normalize_persian(text).split(" ")
                tokens = [t for t in tokens if t]
                counts = Counter(tokens)
                doc_term_counts[node["id"]] = counts
                total_length += len(tokens)

                cur.executemany(
                    "INSERT INTO term_frequencies (node_id, term, tf) VALUES (?, ?, ?)",
                    [(node["id"], term, tf) for term, tf in counts.items()],
                )
                cur.execute(
                    "INSERT INTO doc_length (node_id, length) VALUES (?, ?)",
                    (node["id"], len(tokens)),
                )
                for term in counts:
                    doc_freq[term] += 1

            n_docs = len(nodes)
            avgdl = (total_length / n_docs) if n_docs else 0.0

            cur.execute(
                "INSERT INTO corpus_stats (key, value) VALUES ('n_docs', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(n_docs),),
            )
            cur.execute(
                "INSERT INTO corpus_stats (key, value) VALUES ('avgdl', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(avgdl),),
            )
            conn.commit()

            # ساخت بردار TF-IDF برای هر سند و ذخیره در embedding_storage
            for node_id, counts in doc_term_counts.items():
                vec = {}
                for term, tf in counts.items():
                    idf = math.log((1 + n_docs) / (1 + doc_freq[term])) + 1
                    vec[term] = tf * idf
                tfidf_vectors[node_id] = vec

            self.storage.save_many(tfidf_vectors, model_name=HybridConfig.EMBEDDING_MODEL_DEFAULT)

            return {"n_docs": n_docs, "n_terms": len(doc_freq), "avgdl": round(avgdl, 2)}
        finally:
            conn.close()

    # -----------------------------------------------------
    # BM25
    # -----------------------------------------------------
    def _bm25_scores(self, terms: List[str], candidate_ids: List[int], k1=1.5, b=0.75) -> Dict[int, float]:
        conn = self._connect()
        try:
            cur = conn.cursor()

            cur.execute("SELECT value FROM corpus_stats WHERE key='n_docs'")
            row = cur.fetchone()
            n_docs = int(row["value"]) if row else 0
            cur.execute("SELECT value FROM corpus_stats WHERE key='avgdl'")
            row = cur.fetchone()
            avgdl = float(row["value"]) if row and row["value"] else 1.0

            if n_docs == 0 or not candidate_ids:
                return {}

            placeholders = ",".join("?" for _ in candidate_ids)
            term_placeholders = ",".join("?" for _ in terms)

            cur.execute(
                f"SELECT node_id, length FROM doc_length WHERE node_id IN ({placeholders})",
                candidate_ids,
            )
            doc_lengths = {r["node_id"]: r["length"] for r in cur.fetchall()}

            cur.execute(
                f"SELECT node_id, term, tf FROM term_frequencies "
                f"WHERE node_id IN ({placeholders}) AND term IN ({term_placeholders})",
                candidate_ids + terms,
            )
            tf_map: Dict[int, Dict[str, int]] = {}
            for r in cur.fetchall():
                tf_map.setdefault(r["node_id"], {})[r["term"]] = r["tf"]

            # document frequency هر term (برای idf)
            df_map: Dict[str, int] = {}
            for term in terms:
                cur.execute(
                    "SELECT COUNT(DISTINCT node_id) AS df FROM term_frequencies WHERE term=?", (term,)
                )
                df_map[term] = cur.fetchone()["df"]

            scores: Dict[int, float] = {}
            for node_id in candidate_ids:
                doc_len = doc_lengths.get(node_id, 0) or 1
                score = 0.0
                for term in terms:
                    tf = tf_map.get(node_id, {}).get(term, 0)
                    if tf == 0:
                        continue
                    df = df_map.get(term, 0)
                    idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)
                    denom = tf + k1 * (1 - b + b * doc_len / avgdl)
                    score += idf * (tf * (k1 + 1)) / denom
                if score > 0:
                    scores[node_id] = score

            return scores
        finally:
            conn.close()

    # -----------------------------------------------------
    # جستجوی نهایی: BM25 + TF-IDF cosine → ترکیب با RRF
    # -----------------------------------------------------
    def search(self, query: str, top_k: int = 10, domains: Optional[List[str]] = None) -> List[Dict]:
        normalized = normalize_persian(query)
        terms = [t for t in normalized.split(" ") if t]
        if not terms:
            return []

        conn = self._connect()
        try:
            cur = conn.cursor()
            term_placeholders = ",".join("?" for _ in terms)
            if domains:
                domain_placeholders = ",".join("?" for _ in domains)
                cur.execute(
                    f"SELECT DISTINCT tf.node_id FROM term_frequencies tf "
                    f"JOIN graph_nodes gn ON gn.id = tf.node_id "
                    f"WHERE tf.term IN ({term_placeholders}) AND gn.domain IN ({domain_placeholders})",
                    terms + domains,
                )
            else:
                cur.execute(
                    f"SELECT DISTINCT node_id FROM term_frequencies WHERE term IN ({term_placeholders})",
                    terms,
                )
            candidate_ids = [r["node_id"] for r in cur.fetchall()]
        finally:
            conn.close()

        if not candidate_ids:
            return []

        bm25_scores = self._bm25_scores(terms, candidate_ids)
        bm25_ranked = sorted(bm25_scores.items(), key=lambda kv: kv[1], reverse=True)

        query_vec: Dict[str, float] = {t: 1.0 for t in terms}
        cosine_scores = {}
        for node_id in candidate_ids:
            doc_vec = self.storage.get(node_id, model_name=HybridConfig.EMBEDDING_MODEL_DEFAULT)
            if doc_vec:
                sim = EmbeddingStorage.cosine_similarity(query_vec, doc_vec)
                if sim > 0:
                    cosine_scores[node_id] = sim
        cosine_ranked = sorted(cosine_scores.items(), key=lambda kv: kv[1], reverse=True)

        rrf_scores = self._reciprocal_rank_fusion([bm25_ranked, cosine_ranked])

        results = []
        for node_id, score in sorted(rrf_scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]:
            results.append(
                {
                    "id": node_id,
                    "score": round(score, 4),
                    "bm25": round(bm25_scores.get(node_id, 0.0), 4),
                    "cosine": round(cosine_scores.get(node_id, 0.0), 4),
                }
            )
        return results

    @staticmethod
    def _reciprocal_rank_fusion(ranked_lists: List[List[Tuple[int, float]]], k: int = RRF_K) -> Dict[int, float]:
        fused: Dict[int, float] = {}
        for ranked in ranked_lists:
            for rank, (node_id, _score) in enumerate(ranked, start=1):
                fused[node_id] = fused.get(node_id, 0.0) + 1.0 / (k + rank)
        return fused


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
