from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from .copilot_hybrid import HybridRAGBridge
from .copilot_sqlite import SQLiteCopilotSearch

DEFAULT_DB = "/data/data/com.termux/files/home/hermezgan-intelligent/backend/data/hdp_v2.db"
DEFAULT_LLM_URL = "http://127.0.0.1:8080"
DEFAULT_LLM_MODEL = "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"

class CopilotService:
    def __init__(
        self,
        db_path: Optional[str] = None,
        llm_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.db_path = db_path or os.getenv("HDP_RAG_DB_PATH") or DEFAULT_DB
        self.llm_url = (llm_url or os.getenv("LLAMA_CPP_URL") or DEFAULT_LLM_URL).rstrip("/")
        self.model = model or os.getenv("LLAMA_CPP_MODEL") or DEFAULT_LLM_MODEL
        self.hybrid = HybridRAGBridge(db_path=self.db_path)
        self.sqlite = SQLiteCopilotSearch(db_path=self.db_path)
        self.memory: Dict[str, List[Dict[str, Any]]] = {}

    def _mem(self, conversation_id: str) -> List[Dict[str, Any]]:
        return self.memory.setdefault(conversation_id, [])

    def _trim(self, conversation_id: str, limit: int = 12) -> None:
        mem = self._mem(conversation_id)
        if len(mem) > limit:
            self.memory[conversation_id] = mem[-limit:]

    def _build_prompt(self, question: str, sources: List[Dict[str, Any]], memory: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        source_lines = []
        for idx, src in enumerate(sources[:6], start=1):
            title = src.get("title") or f"منبع {idx}"
            cat = f" | دسته: {src.get('category')}" if src.get("category") else ""
            content = str(src.get("content") or "").strip()
            source_lines.append(f"[{idx}] {title}{cat}\n{content}")

        return [
            {
                "role": "system",
                "content": (
                    "شما Copilot آفلاین HDP BND هستید. فقط بر اساس منابع ارائه‌شده پاسخ دهید. "
                    "اگر داده کافی نبود، صریح بگویید که اطلاعات کافی در پایگاه دانش یافت نشد. "
                    "پاسخ را کوتاه، دقیق و فارسی بنویس."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"سوال: {question}\n\n"
                    f"زمینه گفتگو: {json.dumps(memory, ensure_ascii=False)}\n\n"
                    f"منابع بازیابی‌شده:\n"
                    f"{chr(10).join(source_lines) if source_lines else 'هیچ منبعی یافت نشد.'}\n\n"
                    "دستور:\n"
                    "- فقط از منابع استفاده کن.\n"
                    "- اگر مطمئن نیستی، بگو اطلاعات کافی در پایگاه دانش یافت نشد.\n"
                    "- در صورت امکان به 1 تا 3 منبع ارجاع بده."
                ),
            },
        ]

    def _llama_chat_sync(self, messages: List[Dict[str, str]], max_tokens: int = 700, temperature: float = 0.2) -> str:
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

    async def ask(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        conversation_id = str(context.get("conversationId") or "default")
        memory = self._mem(conversation_id)

        hybrid_result = self.hybrid.search(query, limit=int(context.get("limit") or 5))
        sources = [x for x in hybrid_result.get("items", []) if float(x.get("score", 0.0)) >= 0.42]

        # graph relations returned by existing Hybrid/RAG engine or SQLite fallback
        relations = hybrid_result.get("relations", [])
        prompt = self._build_prompt(query, sources, memory)

        llm_error = None
        answer = ""
        try:
            answer = await asyncio.to_thread(
                self._llama_chat_sync,
                prompt,
                int(context.get("max_tokens") or 700),
                float(context.get("temperature") or 0.2),
            )
        except Exception as e:
            llm_error = str(e)
            if sources:
                top = sources[0]
                answer = (top.get("content") or top.get("title") or "اطلاعات کافی در پایگاه دانش یافت نشد.")
            else:
                answer = "اطلاعات کافی در پایگاه دانش یافت نشد."

        turn_user = {"role": "user", "question": query}
        turn_assistant = {
            "role": "assistant",
            "answer": answer,
            "sources": [
                {
                    "table": s.get("table"),
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "category": s.get("category"),
                    "score": s.get("score"),
                }
                for s in sources
            ],
        }
        memory.extend([turn_user, turn_assistant])
        self._trim(conversation_id)

        confidence = 0.5 if not sources else min(0.98, 0.55 + (float(sources[0].get("score", 0.0)) * 0.4))
        return {
            "answer": answer,
            "intent": context.get("intent") or "general",
            "confidence": confidence,
            "sources": turn_assistant["sources"],
            "relations": relations,
            "debug": hybrid_result.get("debug", {}),
            "context": {
                "conversationId": conversation_id,
                "dbPath": self.db_path,
                "llmUrl": self.llm_url,
                "llmError": llm_error,
            },
        }

    async def health(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "db_path": self.db_path,
            "db_exists": Path(self.db_path).exists(),
            "llm_url": self.llm_url,
            "model": self.model,
        }
