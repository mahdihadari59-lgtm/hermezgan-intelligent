from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from typing import Any, Dict, List, Optional

from app.services.db_intelligence_service import DBIntelligenceService
from app.services.query_planner_service import QueryPlannerService

DEFAULT_DB = "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"
DEFAULT_LLM_URL = "http://127.0.0.1:8080"
DEFAULT_LLM_MODEL = "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"

def _safe_text(value: Any) -> str:
    return "" if value is None else str(value)

class CopilotService:
    """
    Stage 6/7:
    - query planner
    - db intelligence against real /data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db tables
    - prompt assembly over the retrieved sources
    - still supports llama.cpp / fallback generation
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        llm_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.db_path = db_path or os.getenv("HDP_RAG_DB_PATH") or DEFAULT_DB
        self.llm_url = (llm_url or os.getenv("LLAMA_CPP_URL") or DEFAULT_LLM_URL).rstrip("/")
        self.model = model or os.getenv("LLAMA_CPP_MODEL") or DEFAULT_LLM_MODEL

        self.planner = QueryPlannerService()
        self.db = DBIntelligenceService(db_path=self.db_path)

    def _build_prompt(self, question: str, sources: List[Dict[str, Any]], history: List[Dict[str, Any]], plan: Dict[str, Any]) -> List[Dict[str, str]]:
        source_lines = []
        for idx, src in enumerate(sources[:8], start=1):
            title = src.get("title") or f"منبع {idx}"
            table = src.get("table") or "unknown"
            note = f" | {src.get('note')}" if src.get("note") else ""
            content = _safe_text(src.get("content")).strip()
            source_lines.append(f"[{idx}] {title} [{table}]{note}\n{content}")

        history_lines = []
        for turn in history[-8:]:
            role = turn.get("role", "user")
            txt = turn.get("text") or turn.get("answer") or turn.get("question") or ""
            history_lines.append(f"{role}: {txt}")

        return [
            {
                "role": "system",
                "content": (
                    "شما هسته پاسخ‌گوی HDP AI Kernel هستید. "
                    "فقط بر اساس منابع بازیابی‌شده پاسخ بده. "
                    "اگر داده کافی نیست، صریح بگو اطلاعات کافی در پایگاه دانش یافت نشد. "
                    "پاسخ را کوتاه، دقیق، فارسی و کاربردی بنویس."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"سوال: {question}\n\n"
                    f"طرح پرسش: {json.dumps(plan, ensure_ascii=False)}\n\n"
                    f"تاریخچه گفتگو:\n{chr(10).join(history_lines) if history_lines else 'ندارد'}\n\n"
                    f"منابع بازیابی‌شده:\n{chr(10).join(source_lines) if source_lines else 'هیچ منبعی یافت نشد.'}\n\n"
                    "دستور:\n"
                    "- فقط از منابع و تاریخچه استفاده کن.\n"
                    "- اگر مطمئن نیستی، بگو اطلاعات کافی در پایگاه دانش یافت نشد.\n"
                    "- در صورت امکان نام جدول‌های استفاده‌شده را کوتاه و طبیعی ذکر کن."
                ),
            },
        ]

    def _llama_chat_sync(self, messages: List[Dict[str, str]], max_tokens: int = 250, temperature: float = 0.2) -> str:
        def _post(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            data = _post(f"{self.llm_url}/v1/chat/completions", payload)
            text = (
                data.get("choices", [{}])[0].get("message", {}).get("content")
                or data.get("choices", [{}])[0].get("text")
                or data.get("content")
                or data.get("response")
                or ""
            )
            if text.strip():
                return text.strip()
        except Exception:
            pass

        fallback = {
            "prompt": "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages),
            "n_predict": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        data2 = _post(f"{self.llm_url}/completion", fallback)
        text = data2.get("content") or data2.get("response") or data2.get("choices", [{}])[0].get("text") or ""
        if not text.strip():
            raise RuntimeError("LLM_EMPTY_RESPONSE")
        return text.strip()

    async def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        conversation_id = str(context.get("conversationId") or "default")

        # planner and db intelligence
        plan = context.get("query_plan") or self.planner.plan(question, context)
        db_pack = self.db.search(question, plan=plan, limit=int(context.get("limit") or 8))
        db_sources = db_pack.get("items", [])

        # merge any precomputed candidates into sources
        extra = context.get("db_candidates") or []
        merged_sources = []
        seen = set()
        for src in (db_sources + list(extra)):
            key = f"{src.get('table')}::{src.get('title')}::{src.get('content')}".lower().strip()
            if key in seen:
                continue
            seen.add(key)
            merged_sources.append(src)

        # keep it bounded
        merged_sources = sorted(merged_sources, key=lambda x: float(x.get("score", 0.0)), reverse=True)[:12]

        history = context.get("history") or []
        prompt = self._build_prompt(question, merged_sources, history, plan)

        llm_error = None
        answer = ""
        try:
            answer = await asyncio.to_thread(
                self._llama_chat_sync,
                prompt,
                int(context.get("max_tokens") or 250),
                float(context.get("temperature") or 0.2),
            )
        except Exception as e:
            llm_error = str(e)
            if merged_sources:
                answer = _safe_text(merged_sources[0].get("content") or merged_sources[0].get("title"))
            else:
                answer = "اطلاعات کافی در پایگاه دانش یافت نشد."

        return {
            "answer": answer,
            "intent": plan.get("intent") or context.get("intent") or "general",
            "confidence": 0.5 if not merged_sources else min(0.98, 0.55 + (float(merged_sources[0].get("score", 0.0)) * 0.4)),
            "sources": [
                {
                    "table": s.get("table"),
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "category": s.get("category"),
                    "score": s.get("score"),
                    "note": s.get("note"),
                }
                for s in merged_sources
            ],
            "relations": db_pack.get("relations", []),
            "db_summary": {
                "db_path": db_pack.get("db_path"),
                "tables_scanned": db_pack.get("tables_scanned", []),
                "table_hits": db_pack.get("table_hits", {}),
                "source_count": len(merged_sources),
            },
            "debug": {
                "planner": plan,
                "llmError": llm_error,
            },
            "context": {
                "conversationId": conversation_id,
                "dbPath": self.db_path,
                "llmUrl": self.llm_url,
                "plan": plan,
            },
        }

    async def health(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "db_path": self.db_path,
            "db_exists": os.path.exists(self.db_path),
            "llm_url": self.llm_url,
            "model": self.model,
        }
