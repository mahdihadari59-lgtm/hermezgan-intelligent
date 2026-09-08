from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.services.copilot_service import CopilotService

@dataclass
class OrchestrationContext:
    conversation_id: str = "default"
    user_id: str = "anon"
    location: Dict[str, Any] = field(default_factory=dict)
    dialect: Optional[str] = None
    mode: str = "text"  # text | voice
    raw_input: str = ""
    normalized_input: str = ""
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class HDPOrchestratorV2:
    """
    Central coordinator for:
    - Bandari dialect preprocessing
    - Vosk STT (lazy)
    - Intent / entity / context
    - Expert routing
    - Hybrid/RAG retrieval
    - LLM answer generation
    """

    def __init__(self, db_path: Optional[str] = None, llm_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.db_path = db_path
        self.llm_url = llm_url
        self.model = model
        self._services = {}
        self._load_optional_services()

        self.copilot = CopilotService(db_path=self.db_path, llm_url=self.llm_url, model=self.model)

    def _load_optional_services(self) -> None:
        module_candidates = {
            "bandari": [
                "app.core.bandari_engine",
                "app.core.bandari",
                "app.engine.bandari_engine",
                "app.gateways.bandari_engine",
            ],
            "speech": [
                "app.core.speech_interface",
                "app.core.speech_to_text",
                "app.gateway.speech_gateway",
            ],
            "intent": [
                "app.engine.intent_engine",
                "app.engine.intent",
            ],
            "expert": [
                "app.engine.expert_dispatcher",
                "app.engine.expert_router",
            ],
            "search": [
                "app.engine.search_manager",
                "app.engine.pipeline",
                "app.engine.orchestrator",
                "app.engine.rag_pipeline",
            ],
        }

        for key, mods in module_candidates.items():
            loaded = None
            for name in mods:
                try:
                    loaded = importlib.import_module(name)
                    break
                except Exception:
                    continue
            self._services[key] = loaded

    def _try_call(self, target: Any, names: List[str], *args, **kwargs):
        if target is None:
            return None
        for n in names:
            fn = getattr(target, n, None)
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

    def _bandari_normalize(self, text: str, ctx: OrchestrationContext) -> str:
        mod = self._services.get("bandari")
        if not mod:
            return text

        # module-level preprocess / normalize
        for candidate in ["normalize", "preprocess", "detect_and_normalize", "process"]:
            fn = getattr(mod, candidate, None)
            if callable(fn):
                try:
                    out = fn(text, ctx.__dict__)
                    if isinstance(out, str) and out.strip():
                        return out
                    if isinstance(out, dict) and out.get("text"):
                        return str(out["text"])
                except Exception:
                    pass

        # class-based engine
        for cls_name in ["BandariEngine", "BandariProcessor", "DialectEngine"]:
            cls = getattr(mod, cls_name, None)
            if inspect.isclass(cls):
                try:
                    obj = cls()
                except Exception:
                    try:
                        obj = cls(ctx.__dict__)
                    except Exception:
                        continue
                out = self._try_call(obj, ["normalize", "preprocess", "process", "detect"], text, ctx.__dict__)
                if isinstance(out, str) and out.strip():
                    return out
                if isinstance(out, dict) and out.get("text"):
                    return str(out["text"])
        return text

    def _intent_entities(self, text: str, ctx: OrchestrationContext) -> Dict[str, Any]:
        mod = self._services.get("intent")
        result = {"intent": None, "entities": {}, "confidence": 0.0}
        if not mod:
            return result

        for candidate in ["detect_intent", "detect", "predict", "classify"]:
            fn = getattr(mod, candidate, None)
            if callable(fn):
                try:
                    out = fn(text, ctx.__dict__)
                    if isinstance(out, dict):
                        result["intent"] = out.get("intent") or out.get("type")
                        result["entities"] = out.get("entities") or out.get("slots") or {}
                        result["confidence"] = float(out.get("confidence") or 0.0)
                        return result
                except Exception:
                    pass

        for cls_name in ["IntentEngine", "IntentDetector", "IntentClassifier"]:
            cls = getattr(mod, cls_name, None)
            if inspect.isclass(cls):
                try:
                    obj = cls()
                except Exception:
                    try:
                        obj = cls(self.db_path)
                    except Exception:
                        continue
                out = self._try_call(obj, ["detect", "detect_intent", "predict", "classify"], text, ctx.__dict__)
                if isinstance(out, dict):
                    result["intent"] = out.get("intent") or out.get("type")
                    result["entities"] = out.get("entities") or out.get("slots") or {}
                    result["confidence"] = float(out.get("confidence") or 0.0)
                    return result

        return result

    def _expert_dispatch(self, query: str, ctx: OrchestrationContext, intent_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mod = self._services.get("expert")
        if not mod:
            return None

        for candidate in ["dispatch", "route", "run", "execute"]:
            fn = getattr(mod, candidate, None)
            if callable(fn):
                try:
                    out = fn(query, ctx.__dict__, intent_payload)
                    if out:
                        return out if isinstance(out, dict) else {"answer": str(out)}
                except Exception:
                    pass

        for cls_name in ["ExpertDispatcher", "ExpertRouter", "Dispatcher"]:
            cls = getattr(mod, cls_name, None)
            if inspect.isclass(cls):
                try:
                    obj = cls()
                except Exception:
                    try:
                        obj = cls(self.db_path)
                    except Exception:
                        continue
                out = self._try_call(obj, ["dispatch", "route", "run", "execute"], query, ctx.__dict__, intent_payload)
                if out:
                    return out if isinstance(out, dict) else {"answer": str(out)}

        return None

    async def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ctx = OrchestrationContext(
            conversation_id=str(payload.get("conversationId") or payload.get("conversation_id") or "default"),
            user_id=str(payload.get("userId") or payload.get("user_id") or "anon"),
            location=payload.get("location") or {},
            dialect=payload.get("dialect"),
            mode=str(payload.get("mode") or "text"),
            raw_input=str(payload.get("query") or payload.get("text") or payload.get("message") or ""),
            metadata=payload.get("metadata") or {},
        )

        if not ctx.raw_input.strip():
            return {
                "answer": "لطفاً یک پرسش وارد کنید.",
                "intent": "empty",
                "confidence": 1.0,
                "sources": [],
                "relations": [],
                "context": ctx.__dict__,
            }

        normalized = self._bandari_normalize(ctx.raw_input, ctx)
        ctx.normalized_input = normalized

        # Voice mode: lazy STT if raw input is audio/transcript-like
        # No hard dependency on Vosk here; if speech module exists, use it.
        speech_mod = self._services.get("speech")
        if ctx.mode == "voice" and speech_mod and hasattr(speech_mod, "transcribe"):
            try:
                transcript = await self._maybe_async(self._try_call(speech_mod, ["transcribe", "stt", "speech_to_text"], ctx.raw_input, ctx.__dict__))
                if isinstance(transcript, str) and transcript.strip():
                    normalized = transcript.strip()
                    ctx.normalized_input = normalized
            except Exception:
                pass

        intent_payload = self._intent_entities(normalized, ctx)
        ctx.intent = intent_payload.get("intent")
        ctx.entities = intent_payload.get("entities") or {}

        # Expert dispatcher gets first chance
        expert_result = self._expert_dispatch(normalized, ctx, intent_payload)
        if expert_result:
            answer = expert_result.get("answer") or expert_result.get("text") or ""
            return {
                "answer": answer,
                "intent": ctx.intent or expert_result.get("intent") or "expert",
                "confidence": float(intent_payload.get("confidence") or expert_result.get("confidence") or 0.5),
                "sources": expert_result.get("sources") or [],
                "relations": expert_result.get("relations") or [],
                "context": ctx.__dict__,
                "debug": {"stage": "expert_dispatch"},
            }

        # Fallback to existing Hybrid/RAG + LLM
        result = await self.copilot.ask(normalized, {
            "conversationId": ctx.conversation_id,
            "userId": ctx.user_id,
            "location": ctx.location,
            "intent": ctx.intent,
            "entities": ctx.entities,
            "dialect": ctx.dialect,
            "mode": ctx.mode,
        })
        result["context"] = {**ctx.__dict__, **(result.get("context") or {})}
        result["debug"] = {**(result.get("debug") or {}), "stage": "copilot_service"}
        return result

    async def health(self) -> Dict[str, Any]:
        h = await self.copilot.health()
        h.update({
            "orchestrator": "HDPOrchestratorV2",
            "loaded_services": {k: bool(v) for k, v in self._services.items()},
        })
        return h

    async def _maybe_async(self, value):
        if inspect.isawaitable(value):
            return await value
        return value
