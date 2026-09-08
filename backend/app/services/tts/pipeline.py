from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TTSPipeline:
    def __init__(self, cache_dir: str = "/tmp/hdp_driver_tts"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
    ) -> Optional[str]:
        text = (text or "").strip()
        if not text:
            return None

        key = hashlib.sha256(
            f"{voice_id or 'default'}:{text}".encode("utf-8")
        ).hexdigest()

        target = self.cache_dir / f"{key}.mp3"

        if target.exists():
            return str(target)

        try:
            from app.core.speech_interface import get_speech_interface

            interface = get_speech_interface()
            audio = interface.text_to_speech_bytes(
                text=text,
                language="fa",
            )

            if not audio:
                return None

            target.write_bytes(audio)
            return str(target)

        except Exception:
            logger.exception("Driver TTS synthesis failed")
            return None
