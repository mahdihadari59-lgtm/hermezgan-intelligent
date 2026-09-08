from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

class HybridRAGBridge:
    """
    Bridge to the project's existing Hybrid/RAG engine.

    Priority:
    1) engine.search_manager / engine.pipeline / engine.orchestrator / engine.rerank_engine / engine.graph_search_engine_v2
    2) direct SQLite fallback over backend/data//data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = str(db_path) if db_path else None
        self._engine_modules = {}
        self._load_modules()

    def _load_modules(self) -> None:
        module_names = [
            "engine.search_manager",
            "engine.pipeline",
            "engine.orchestrator",
            "engine.rerank_engine",
            "engine.graph_search_engine_v2",
            "engine.answer_engine",
            "engine.hybrid",
            "engine.retrieval",
        ]
        for name in module_names:
            try:
                self._engine_modules[name] = importlib.import_module(name)
            except Exception:
                self._engine_modules[name] = None

    def _instantiate_first(self, module_name: str, class_names: Sequence[str], *args, **kwargs):
        mod = self._engine_modules.get(module_name)
        if not mod:
            return None
        for cls_name in class_names:
            cls = getattr(mod, cls_name, None)
            if inspect.isclass(cls):
                try:
                    return cls(*args, **kwargs)
                except Exception:
                    try:
                        return cls()
                    except Exception:
                        continue
        return None

    def _call_first(self, obj: Any, method_names: Sequence[str], *args, **kwargs):
        if obj is None:
            return None
        for name in method_names:
            fn = getattr(obj, name, None)
            if callable(fn):
                try:
                    return fn(*args, **kwargs)
                except TypeError:
                    try:
                        return fn(*args)
                    except Exception:
                        continue
                except Exception:
                    continue
        return None

    def _normalize_item(self, item: Any) -> Dict[str, Any]:
        if item is None:
            return {}
        if isinstance(item, dict):
            return {
                "table": item.get("table") or item.get("_table") or "unknown",
                "id": item.get("id") or item.get("rowid") or item.get("knowledge_id") or item.get("doc_id"),
                "title": item.get("title") or item.get("name") or item.get("question") or item.get("heading") or item.get("topic") or "",
                "content": item.get("content") or item.get("body") or item.get("text") or item.get("description") or item.get("answer") or item.get("chunk_text") or item.get("passage") or item.get("excerpt") or "",
                "category": item.get("category") or item.get("section") or item.get("type"),
                "source": item.get("source") or item.get("origin") or item.get("doc_source"),
                "score": float(item.get("score") or item.get("_score") or item.get("relevance") or 0.0),
                "raw": item,
            }
        if isinstance(item, str):
            return {
                "table": "text",
                "id": None,
                "title": item[:120],
                "content": item,
                "category": None,
                "source": None,
                "score": 0.5,
                "raw": item,
            }
        return {
            "table": "unknown",
            "id": None,
            "title": "",
            "content": str(item),
            "category": None,
            "source": None,
            "score": 0.0,
            "raw": item,
        }

    def _direct_sqlite_fallback(self, query: str, limit: int = 5) -> Dict[str, Any]:
        from app.services.copilot_sqlite import SQLiteCopilotSearch

        searcher = SQLiteCopilotSearch(db_path=self.db_path)
        data = searcher.search(query, limit=limit)
        return {
            "items": [self._normalize_item(x) for x in data.get("items", [])],
            "relations": data.get("relations", []),
            "debug": data.get("debug", {}),
            "source": "sqlite_fallback",
        }

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        query = str(query or "").strip()
        if not query:
            return {"items": [], "relations": [], "debug": {"counts": {}}, "source": "empty"}

        # 1) SearchManager / pipeline entry points
        for module_name in [
            "engine.search_manager",
            "engine.pipeline",
            "engine.orchestrator",
        ]:
            mod = self._engine_modules.get(module_name)
            if not mod:
                continue

            # module-level function names
            result = self._call_first(
                mod,
                ["search", "hybrid_search", "search_hybrid", "query", "run"],
                query,
                limit,
            )
            if result:
                return self._normalize_result(result, query, limit, source=module_name)

            # class-based managers
            obj = self._instantiate_first(
                module_name,
                ["SearchManager", "HybridSearchManager", "Pipeline", "Orchestrator"],
                db_path=self.db_path,
            )
            if obj is not None:
                result = self._call_first(
                    obj,
                    ["search", "hybrid_search", "search_hybrid", "query", "run", "execute", "answer"],
                    query,
                    limit,
                )
                if result:
                    return self._normalize_result(result, query, limit, source=module_name)

        # 2) Graph search as an additional signal
        graph_result = self._graph_search(query, limit)
        if graph_result and graph_result.get("items"):
            return graph_result

        # 3) SQLite fallback
        return self._direct_sqlite_fallback(query, limit)

    def _graph_search(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        mod = self._engine_modules.get("engine.graph_search_engine_v2")
        if not mod:
            return None

        obj = self._instantiate_first(
            "engine.graph_search_engine_v2",
            ["GraphSearchEngineV2", "GraphSearchEngine", "GraphEngine", "Engine"],
            db_path=self.db_path,
        )

        if obj is not None:
            result = self._call_first(
                obj,
                ["search", "query", "run", "execute", "search_graph"],
                query,
                limit,
            )
            if result:
                return self._normalize_result(result, query, limit, source="engine.graph_search_engine_v2")

        result = self._call_first(
            mod,
            ["search", "query", "run", "execute", "search_graph"],
            query,
            limit,
        )
        if result:
            return self._normalize_result(result, query, limit, source="engine.graph_search_engine_v2")

        return None

    def _normalize_result(self, result: Any, query: str, limit: int, source: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        relations: List[Dict[str, Any]] = []
        debug: Dict[str, Any] = {}

        if isinstance(result, dict):
            if "items" in result:
                items = [self._normalize_item(x) for x in (result.get("items") or [])]
            elif "results" in result:
                items = [self._normalize_item(x) for x in (result.get("results") or [])]
            elif "answer" in result:
                items = [self._normalize_item(result)]
            if "relations" in result:
                relations = list(result.get("relations") or [])
            debug = dict(result.get("debug") or {})
        elif isinstance(result, (list, tuple)):
            items = [self._normalize_item(x) for x in result]
        else:
            items = [self._normalize_item(result)]

        # Light re-rank using the query tokens
        tokens = [t.lower() for t in str(query).split() if len(t) >= 2]
        def score_item(x: Dict[str, Any]) -> float:
            text = f"{x.get('title','')} {x.get('content','')}".lower()
            overlap = sum(1 for t in tokens if t in text) / max(len(tokens), 1) if tokens else 0.0
            return float(x.get("score", 0.0)) * 0.55 + overlap * 0.45

        items = sorted(items, key=score_item, reverse=True)[:limit]
        return {
            "items": items,
            "relations": relations,
            "debug": debug or {"source": source, "count": len(items)},
            "source": source,
        }
