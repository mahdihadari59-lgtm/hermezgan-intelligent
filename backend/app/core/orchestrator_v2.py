1# (محتوای کامل فایل HDPOrchestratorV2 با BandariBridge و wiring برای speech)
from __future__ import annotations

import importlib
import inspect
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.copilot_service import CopilotService

BANDARI_ENGINE_ENV = os.environ.get("BANDARI_ENGINE_PATH", "bandari-engine-2026/bandari-engine")
BANDARI_MODULES = [
    "dialect/index.js",
    "morphology/index.js",
    "grammar/index.js",
    "intent/index.js",
    "context/index.js",
    "rag/index.js",
]


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


class BandariBridge:
    """A lightweight bridge to call Bandari JS modules under the bandari-engine directory.

    It writes a small temporary Node script that requires the target module and calls a
    common set of function names (normalize, process, detect_and_normalize, run, default).
    The bridge exposes a few convenience methods used by the orchestrator.
    """

    def __init__(self, engine_path: str):
        self.engine_path = Path(engine_path)

    def _call_module(self, module_rel_path: str, text: str, ctx: Dict[str, Any], timeout: int = 20):
        module_path = (self.engine_path / module_rel_path).resolve()
        if not module_path.exists():
            return None

        payload = {
            "text": text,
            "ctx": ctx,
        }

        script = f"""
const mod = require('{module_path.as_posix()}');
const payload = {json.dumps(payload, ensure_ascii=False)};
(async () => {{
  try {{
    const candidates = ["normalize","process","detect_and_normalize","run","default"];
    let fn = null;
    for (const n of candidates) {{
      if (typeof mod[n] === 'function') {{ fn = mod[n]; break; }}
    }}
    if (!fn && typeof mod === 'function') fn = mod;
    const out = fn ? await fn(payload.text, payload.ctx) : null;
    console.log(JSON.stringify({{ok:true, out}}));
  }} catch (e) {{
    console.log(JSON.stringify({{ok:false, error: String(e)}}));
  }}
}})();
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as tmp:
            tmp.write(script)
            script_path = tmp.name
        try:
            res = subprocess.run(["node", script_path], capture_output=True, text=True, timeout=timeout)
            out = res.stdout.strip()
            try:
                parsed = json.loads(out.splitlines()[-1]) if out else {"ok": False, "error": "no output"}
            except Exception:
                parsed = {"ok": False, "error": out or res.stderr}
            return parsed
        finally:
            try:
                os.unlink(script_path)
            except Exception:
                pass

    def normalize(self, text: str, ctx: Dict[str, Any]) -> Optional[str]:
        # Run dialect -> morphology -> grammar in order and return the first non-empty result
        t = text
        for m in ["dialect/index.js", "morphology/index.js", "grammar/index.js"]:
            parsed = self._call_module(m, t, ctx)
            if not parsed:
                continue
            if not parsed.get("ok"):
                continue
            out = parsed.get("out")
            if isinstance(out, str) and out.strip():
                t = out
                continue
            if isinstance(out, dict) and out.get("text"):
                t = str(out.get("text"))
                continue
            # otherwise keep t
        return t

    def detect(self, text: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # call dialect module for detection if present
        parsed = self._call_module("dialect/index.js", text, ctx)
        if parsed and parsed.get("ok"):
            return parsed.get("out") or {}
        return {}


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

        # Ensure the copilot/call layer is created after optional services are known
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

        # If a Node-based bandari engine exists in the repository, prefer it via the bridge
        bandari_path = os.environ.get("BANDARI_ENGINE_PATH", BANDARI_ENGINE_ENV)
        if Path(bandari_path).exists():
            try:
                self._services["bandari"] = BandariBridge(bandari_path)
            except Exception:
                # Keep any Python-based bandari module if present
                pass

        # If speech interface exists as Python module, prefer the instance
        try:
            mod = importlib.import_module("app.core.speech_interface")
            if hasattr(mod, "get_speech_interface"):
                # replace the module with an instance exposing methods like transcribe
                self._services["speech"] = mod.get_speech_interface()
        except Exception:
            # leave current value
            pass

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

        # If the bridge instance is present, call its normalize method
        if hasattr(mod, "normalize") and callable(getattr(mod, "normalize")):
            try:
                out = mod.normalize(text, ctx.__dict__)
                if isinstance(out, str) and out.strip():
                    return out
                if isinstance(out, dict) and out.get("text"):
                    return str(out["text"])
            except Exception:
                pass

        # module-level preprocess / normalize (py modules)
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
            # fallback: try bandari intent module (bridge) if available
            bandari_mod = self._services.get("bandari")
            if bandari_mod and hasattr(bandari_mod, "_call_module"):
                parsed = bandari_mod._call_module("intent/index.js", text, ctx.__dict__)
                if parsed and parsed.get("ok"):
                    out = parsed.get("out")
                    if isinstance(out, dict):
                        result["intent"] = out.get("intent") or out.get("type")
                        result["entities"] = out.get("entities") or out.get("slots") or {}
                        try:
                            result["confidence"] = float(out.get("confidence") or 0.0)
                        except Exception:
                            result["confidence"] = 0.0
                        return result
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
                    passج

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
