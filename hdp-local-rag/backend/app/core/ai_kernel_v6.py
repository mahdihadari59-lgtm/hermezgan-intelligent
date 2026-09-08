from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.services.copilot_service import CopilotService
from app.services.memory_service import MemoryService
from app.services.query_planner_service import QueryPlannerService
from app.services.speech_service import SpeechService

@dataclass
class OrchestrationContext:
    conversation_id: str = "default"
    user_id: str = "anon"
    location: Dict[str, Any] = field(default_factory=dict)
    mode: str = "text"  # text | voice | ws
    dialect: Optional[str] = None
    raw_input: str = ""
    normalized_input: str = ""
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class HDPAIKernelV6:
    """
    Stage 6 + 7:
    - central AI kernel
    - planner + db intelligence + memory + speech
    - unified REST / WS / voice pipeline
    """

    def __init__(self, db_path: Optional[str] = None, llm_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.copilot = CopilotService(db_path=db_path, llm_url=llm_url, model=model)
        self.memory = MemoryService(db_path=db_path)
        self.speech = SpeechService()
        self.planner = QueryPlannerService()

    def _normalize(self, text: str) -> str:
        return self.speech.normalize_text(text)

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        entities: Dict[str, Any] = {}
        m = re.search(r"(?:به|تا|از)\s+([^\s،.]{2,}(?:\s+[^\s،.]{2,}){0,2})", text)
        if m:
            entities["destination"] = m.group(1).strip()
        r = re.search(r"(\d+)\s*(?:کیلومتر|کیلومتری|km|متر|متری|m)", text, re.IGNORECASE)
        if r:
            value = int(r.group(1))
            entities["radius_km"] = value / 1000 if ("متر" in text or "m" in text.lower()) else value
        return entities

    async def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ctx = OrchestrationContext(
            conversation_id=str(payload.get("conversationId") or payload.get("conversation_id") or "default"),
            user_id=str(payload.get("userId") or payload.get("user_id") or "anon"),
            location=payload.get("location") or {},
            mode=str(payload.get("mode") or "text"),
            dialect=payload.get("dialect"),
            raw_input=str(payload.get("query") or payload.get("message") or payload.get("text") or ""),
            metadata=payload.get("metadata") or {},
        )

        if not ctx.raw_input.strip():
            return {
                "answer": "لطفاً یک پیام وارد کنید.",
                "intent": "empty",
                "confidence": 1.0,
                "sources": [],
                "relations": [],
                "context": ctx.__dict__,
                "pipeline": {"stage": "ai_kernel_v6", "memory": True, "planner": True},
            }

        # load memory
        memory_state = self.memory.load(ctx.conversation_id, fallback={"history": [], "summary": None})
        history = memory_state.get("history") or []

        # voice -> transcript
        text = ctx.raw_input
        if ctx.mode == "voice":
            transcript = await self.speech.transcribe(payload, ctx.__dict__)
            if transcript:
                text = transcript

        text = self._normalize(text)
        ctx.dialect = ctx.dialect or self.speech.detect_dialect(text)
        ctx.normalized_input = text
        ctx.intent = self.planner.detect_intent(text)
        ctx.entities = self._extract_entities(text)

        # save user turn
        self.memory.append_turn(ctx.conversation_id, {
            "role": "user",
            "text": text,
            "intent": ctx.intent,
            "entities": ctx.entities,
            "ts": asyncio.get_event_loop().time(),
        })

        plan = self.planner.plan(text, ctx.__dict__)
        db_pack = self.copilot.db.search(text, plan=plan, limit=8)

        result = await self.copilot.ask(text, {
            "conversationId": ctx.conversation_id,
            "userId": ctx.user_id,
            "location": ctx.location,
            "mode": ctx.mode,
            "intent": ctx.intent,
            "entities": ctx.entities,
            "dialect": ctx.dialect,
            "metadata": ctx.metadata,
            "history": history,
            "query_plan": plan,
            "db_candidates": db_pack.get("items", []),
        })

        # enrich result
        result.setdefault("context", {})
        result["context"].update({
            "conversationId": ctx.conversation_id,
            "userId": ctx.user_id,
            "mode": ctx.mode,
            "dialect": ctx.dialect,
            "intent": ctx.intent,
            "entities": ctx.entities,
            "memory_count": len(history),
        })
        result["pipeline"] = {
            "stage": "stage6_7",
            "voice_enabled": True,
            "memory_enabled": True,
            "planner_enabled": True,
            "db_intelligence": True,
            "ws_ready": True,
        }
        result["plan"] = plan
        result["db_summary"] = db_pack

        # save assistant turn
        self.memory.append_turn(ctx.conversation_id, {
            "role": "assistant",
            "text": result.get("answer") or result.get("text") or "",
            "intent": ctx.intent,
            "ts": asyncio.get_event_loop().time(),
        })

        return result

    async def stream_chat(self, payload: Dict[str, Any]):
        result = await self.handle(payload)
        answer = str(result.get("answer") or result.get("text") or "")
        if not answer:
            yield {"type": "final", "data": result}
            return

        chunk_size = 120
        for i in range(0, len(answer), chunk_size):
            yield {"type": "chunk", "data": answer[i:i + chunk_size]}
        yield {"type": "final", "data": result}

    async def health(self) -> Dict[str, Any]:
        health = await self.copilot.health()
        health.update({
            "kernel": "HDPAIKernelV6",
            "stage": 7,
            "memory": True,
            "planner": True,
            "speech": True,
            "db_intelligence": True,
        })
        return health
