from __future__ import annotations
import asyncio, re
from typing import Any, Dict, Optional

class SpeechService:
    def normalize_text(self, text: str) -> str:
        t = str(text or "")
        t = t.replace("ي", "ی").replace("ك", "ک")
        return re.sub(r"\s+", " ", t).strip()

    def detect_dialect(self, text: str) -> str:
        t = self.normalize_text(text)
        return "bandari" if any(x in t for x in ["بندری", "شناور", "لنج", "بندر", "دریا"]) else "fa"

    async def transcribe(self, payload: Any, context: Optional[Dict[str, Any]] = None) -> str:
        context = context or {}
        if isinstance(payload, str):
            return self.normalize_text(payload)
        if isinstance(payload, dict):
            for key in ("transcript", "text", "query", "message", "content"):
                if payload.get(key):
                    return self.normalize_text(str(payload[key]))
        for mod_name in ("app.core.speech_interface", "app.core.speech_to_text", "bandari_engine_2026", "bandari_engine"):
            try:
                mod = __import__(mod_name, fromlist=["*"])
            except Exception:
                continue
            for fn_name in ("transcribe", "stt", "speech_to_text", "process", "normalize", "preprocess"):
                fn = getattr(mod, fn_name, None)
                if callable(fn):
                    try:
                        out = fn(payload, context)
                        if asyncio.iscoroutine(out):
                            out = await out
                        if isinstance(out, str) and out.strip():
                            return self.normalize_text(out)
                        if isinstance(out, dict):
                            for k in ("text", "transcript", "result"):
                                if out.get(k):
                                    return self.normalize_text(str(out[k]))
                    except Exception:
                        pass
        return ""
