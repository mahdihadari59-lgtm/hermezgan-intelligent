"""
pipelines/voice_pipeline.py

Wraps the REAL core/speech_interface.py, which is synchronous and
file-based (not a raw-bytes-in/bytes-out async API):

    class SpeechInterface:
        def speech_to_text(self, audio_file=None, use_microphone=False,
                            language="fa-IR") -> Tuple[str, float]
        def text_to_speech_bytes(self, text: str, language="fa") -> Optional[bytes]
        def process_voice_query(self, audio_file=None, use_microphone=False) -> Tuple[str, float]

    speech_interface = None   # module-level instance, NOT auto-constructed —
                               # you must instantiate SpeechInterface() yourself
                               # and pass it in (see WIRING.md).

Since the FastAPI endpoint receives raw audio bytes (upload), this pipeline
writes them to a temp file, calls speech_to_text() in a thread executor
(it's blocking network/library code), then feeds the transcript through
RAGPipeline exactly like text chat.
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Optional

from app.pipelines.rag_pipeline import RAGPipeline

logger = logging.getLogger("hdp.pipelines.voice")


@dataclass
class VoiceResult:
    transcript: str
    confidence: float
    answer_text: str
    audio: Optional[bytes] = None


class VoicePipeline:
    def __init__(self, speech_interface: Any, rag: RAGPipeline, language: str = "fa-IR"):
        """
        `speech_interface` must be a constructed `SpeechInterface()` instance
        (see core/speech_interface.py) — the module only defines a `None`
        placeholder, it does not build one for you.
        """
        self.speech = speech_interface
        self.rag = rag
        self.language = language

    async def handle_audio(
        self, audio_bytes: bytes, category: str | None = None, want_audio_reply: bool = True
    ) -> VoiceResult:
        transcript, confidence = await self._transcribe(audio_bytes)
        if not transcript:
            return VoiceResult(transcript="", confidence=0.0, answer_text="متوجه نشدم، لطفاً دوباره تلاش کنید.")

        rag_result = await self.rag.answer(transcript, category=category)

        audio_reply = None
        if want_audio_reply:
            audio_reply = await self._synthesize(rag_result.answer)

        return VoiceResult(
            transcript=transcript, confidence=confidence, answer_text=rag_result.answer, audio=audio_reply
        )

    async def _transcribe(self, audio_bytes: bytes) -> tuple[str, float]:
        if self.speech is None:
            logger.warning("voice_pipeline: no SpeechInterface configured")
            return "", 0.0

        loop = asyncio.get_running_loop()
        tmp_path: Optional[str] = None
        try:
            # speech_to_text() only accepts a file path or microphone flag,
            # so uploaded bytes are spooled to a temp WAV/OGG file first.
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            text, confidence = await loop.run_in_executor(
                None, partial(self.speech.speech_to_text, audio_file=tmp_path, language=self.language)
            )
            return text or "", float(confidence or 0.0)
        except Exception as exc:  # noqa: BLE001
            logger.error("voice_pipeline: transcription failed: %s", exc)
            return "", 0.0
        finally:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)

    async def _synthesize(self, text: str) -> Optional[bytes]:
        if self.speech is None:
            return None
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, partial(self.speech.text_to_speech_bytes, text, language="fa"))
        except Exception as exc:  # noqa: BLE001
            logger.error("voice_pipeline: synthesis failed: %s", exc)
            return None
