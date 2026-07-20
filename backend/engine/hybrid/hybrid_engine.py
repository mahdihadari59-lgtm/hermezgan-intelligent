#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/hybrid_engine.py  (v2 — یکپارچه‌شده)
-------------------------------------------------------
هسته اصلی جستجوی Hybrid برای HDP.

این نسخه، بر خلاف نسخه اول، منطق ترکیب امتیاز و جستجوی برداری
را داخل خودش هارد-کد نمی‌کند؛ بلکه از کامپوننت‌های مستقل زیر
استفاده می‌کند (Composition به‌جای God-Class):

    - graph_builder.normalize_persian   → نرمال‌سازی متن
    - vector_search.VectorSearchEngine  → BM25 + TF-IDF + RRF
    - hybrid_ranker.HybridRanker        → ترکیب امتیاز چند منبع
    - fallback_engine.FallbackEngine    → حالت عدم‌تطابق/اعتماد پایین

جریان:
    query
      → keyword search (baseline داخلی، سریع)
      → graph propagation (از graph_edges)
      → vector search (VectorSearchEngine؛ قابل جایگزینی با تزریق)
      → HybridRanker.rank(...)
      → اگر نتیجه‌ای نبود یا امتیاز پایین بود → FallbackEngine

همه کامپوننت‌ها تزریق‌پذیرند (برای تست/جایگزینی آسان).
-------------------------------------------------------
"""

import sqlite3
import time
from typing import Optional, List, Dict, Any, Callable

from engine.hybrid.graph_builder import normalize_persian, GraphBuilder
from engine.hybrid.vector_search import VectorSearchEngine
from engine.hybrid.hybrid_ranker import HybridRanker
from engine.hybrid.fallback_engine import FallbackEngine
from engine.hybrid.config import HybridConfig
from engine.hybrid.constants import EXPERT_DOMAIN_MAP


RerankFn = Callable[[List[Dict[str, Any]], Dict[str, Any]], List[Dict[str, Any]]]


class HybridEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        expert_domain_map: Optional[Dict[str, List[str]]] = None,
        vector_search_engine: Optional[VectorSearchEngine] = None,
        ranker: Optional[HybridRanker] = None,
        fallback_engine: Optional[FallbackEngine] = None,
        rerank_fn: Optional[RerankFn] = None,
        use_vector_search: bool = True,
        graph_depth: Optional[int] = None,
        graph_decay: Optional[float] = None,
        low_confidence_threshold: Optional[float] = None,
    ):
        self.db_path = db_path or HybridConfig.DB_PATH
        self.expert_domain_map = expert_domain_map or dict(EXPERT_DOMAIN_MAP)

        # ensure schema (نوشتن گراف مسئولیت GraphBuilder است، نه اینجا)
        GraphBuilder(self.db_path, seed_default_rules=False)

        self.vector_search_engine = vector_search_engine or (
            VectorSearchEngine(self.db_path) if use_vector_search else None
        )
        self.ranker = ranker or HybridRanker(weights=dict(HybridConfig.HYBRID_WEIGHTS))
        self.fallback_engine = fallback_engine or FallbackEngine(self.db_path)
        self.rerank_fn = rerank_fn

        self.graph_depth = graph_depth if graph_depth is not None else HybridConfig.GRAPH_DEPTH
        self.graph_decay = graph_decay if graph_decay is not None else HybridConfig.GRAPH_DECAY
        self.low_confidence_threshold = (
            low_confidence_threshold
            if low_confidence_threshold is not None
            else HybridConfig.LOW_CONFIDENCE_THRESHOLD
        )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _domains_for_expert(self, expert: Optional[str]) -> List[str]:
        if not expert:
            return []
        return self.expert_domain_map.get(expert, [])

    # -----------------------------------------------------
    # جستجوی اصلی
    # -----------------------------------------------------
    def search(
        self,
        query: str,
        expert: Optional[str] = None,
        top_k: int = 10,
        use_graph_expansion: bool = True,
        intent_alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        started_at = time.time()
        normalized_query = normalize_persian(query)
        terms = [t for t in normalized_query.split(" ") if t]

        if not terms:
            return self._empty_result(query, expert, started_at)

        domains = self._domains_for_expert(expert)

        conn = self._connect()
        try:
            keyword_scores = self._keyword_search(conn, terms, domains)
            graph_scores = (
                self._expand_via_graph(conn, keyword_scores) if use_graph_expansion else {}
            )
        finally:
            conn.close()

        vector_scores: Dict[int, float] = {}
        vector_error = None
        if self.vector_search_engine:
            try:
                vector_hits = self.vector_search_engine.search(query, top_k=50, domains=domains or None)
                vector_scores = {hit["id"]: hit["score"] for hit in vector_hits}
            except Exception as exc:  # noqa: BLE001
                vector_error = f"vector search error: {exc}"

        sources = {"keyword": keyword_scores, "graph": graph_scores, "vector": vector_scores}
        ranked = self.ranker.rank(sources, method="weighted", top_k=top_k)
        results = self._materialize(ranked)

        rerank_error = None
        if results and self.rerank_fn:
            try:
                results = self.rerank_fn(results, {"query": query, "expert": expert})
            except Exception as exc:  # noqa: BLE001
                rerank_error = f"rerank_fn error: {exc}"

        top_score = results[0]["score"] if results else 0.0
        low_confidence = (not results) or top_score < self.low_confidence_threshold

        fallback = None
        if low_confidence:
            fallback = self.fallback_engine.get_fallback(
                query,
                expert=expert,
                domain=domains[0] if domains else "",
                intent_alternatives=intent_alternatives,
            )

        return {
            "query": query,
            "expert": expert,
            "count": len(results),
            "results": results,
            "low_confidence": low_confidence,
            "fallback": fallback,
            "sources_used": {
                "keyword": True,
                "graph": use_graph_expansion,
                "vector": bool(self.vector_search_engine),
                "rerank": bool(self.rerank_fn),
            },
            "error": vector_error or rerank_error,
            "elapsed_ms": round((time.time() - started_at) * 1000, 1),
        }

    def _empty_result(self, query: str, expert: Optional[str], started_at: float) -> Dict[str, Any]:
        return {
            "query": query,
            "expert": expert,
            "count": 0,
            "results": [],
            "low_confidence": True,
            "fallback": self.fallback_engine.get_fallback(query, expert=expert),
            "sources_used": {"keyword": False, "graph": False, "vector": False, "rerank": False},
            "error": None,
            "elapsed_ms": round((time.time() - started_at) * 1000, 1),
        }

    # -----------------------------------------------------
    # جستجوی کلیدواژه‌ای (baseline سریع، مستقل از VectorSearchEngine)
    # -----------------------------------------------------
    def _keyword_search(self, conn: sqlite3.Connection, terms: List[str], domains: List[str]) -> Dict[int, float]:
        cur = conn.cursor()
        if domains:
            placeholders = ",".join("?" for _ in domains)
            cur.execute(
                f"""
SELECT
    g.id,
    g.title,
    k.content
FROM graph_nodes g
JOIN knowledge k
ON k.id = g.knowledge_id
WHERE k.category IN ({placeholders})
""", domains
            )
        else:
            cur.execute("""
SELECT
    g.id,
    g.title,
    k.content
FROM graph_nodes g
JOIN knowledge k
ON k.id = g.knowledge_id
""")

        scores: Dict[int, float] = {}
        for row in cur.fetchall():
            title_tokens = set(normalize_persian(row["title"] or "").split(" "))
            content_norm = normalize_persian(row["content"] or "")
            content_tokens = set(content_norm.split(" "))

            score = 0.0
            for term in terms:
                if term in title_tokens:
                    score += 2.0
                elif term in content_tokens:
                    score += 1.0
                elif term in content_norm:
                    score += 0.4
            if score > 0:
                scores[row["id"]] = min(1.0, score / (len(terms) * 2.0))
        return scores

    # -----------------------------------------------------
    # انتشار امتیاز روی گراف
    # -----------------------------------------------------
    def _expand_via_graph(self, conn: sqlite3.Connection, keyword_scores: Dict[int, float], top_seed: int = 5) -> Dict[int, float]:
        seeds = sorted(keyword_scores.items(), key=lambda kv: kv[1], reverse=True)[:top_seed]
        cur = conn.cursor()
        propagated: Dict[int, float] = {}

        for seed_id, seed_score in seeds:
            frontier = [(seed_id, seed_score, 0)]
            visited = {seed_id}
            while frontier:
                current_id, current_score, depth = frontier.pop(0)
                if depth >= self.graph_depth:
                    continue
                cur.execute(
                    "SELECT target_id AS neighbor, weight FROM graph_edges WHERE source_id=? "
                    "UNION "
                    "SELECT source_id AS neighbor, weight FROM graph_edges WHERE target_id=?",
                    (current_id, current_id),
                )
                for row in cur.fetchall():
                    neighbor_id = row["neighbor"]
                    if neighbor_id in visited:
                        continue
                    propagated_score = current_score * self.graph_decay * float(row["weight"] or 1.0)
                    if propagated_score < 0.01:
                        continue
                    visited.add(neighbor_id)
                    if propagated_score > propagated.get(neighbor_id, 0.0):
                        propagated[neighbor_id] = propagated_score
                    frontier.append((neighbor_id, propagated_score, depth + 1))

        for seed_id, _ in seeds:
            propagated.pop(seed_id, None)
        return propagated

    # -----------------------------------------------------
    # تبدیل نتایج رتبه‌بندی‌شده (فقط id/score) به رکورد کامل
    # -----------------------------------------------------
    def _materialize(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not ranked:
            return []
        ids = [r["id"] for r in ranked]
        conn = self._connect()
        try:
            cur = conn.cursor()
            placeholders = ",".join("?" for _ in ids)
            cur.execute(
                f"""
SELECT
    g.id,
    g.title,
    k.content,
    g.node_type,
    k.category AS domain
FROM graph_nodes g
JOIN knowledge k
ON k.id = g.knowledge_id
WHERE g.id IN ({placeholders})
""",
                ids,
            )
            rows = {row["id"]: row for row in cur.fetchall()}
        finally:
            conn.close()

        results = []
        for r in ranked:
            row = rows.get(r["id"])
            if not row:
                continue
            results.append(
                {
                    "id": r["id"],
                    "title": row["title"],
                    "content": row["content"],
                    "node_type": row["node_type"],
                    "domain": row["domain"],
                    "score": r["score"],
                    "score_breakdown": r.get("breakdown", {}),
                }
            )
        return results


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="HDP Hybrid Search Engine (v2)")
    parser.add_argument("--db", default=None, help="پیش‌فرض: مسیر تعریف‌شده در config.py")
    parser.add_argument("--query", required=True)
    parser.add_argument("--expert", default=None)
    parser.add_argument("--top_k", type=int, default=10)
    parser.add_argument("--build-index", action="store_true", help="ساخت ایندکس vector search قبل از جستجو")
    args = parser.parse_args()

    engine = HybridEngine(args.db)
    if args.build_index and engine.vector_search_engine:
        engine.vector_search_engine.build_index()

    output = engine.search(args.query, expert=args.expert, top_k=args.top_k)
    print(json.dumps(output, ensure_ascii=False, indent=2))
