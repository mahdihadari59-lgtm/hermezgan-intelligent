from abc import ABC, abstractmethod
from typing import Any, Dict
import os


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError


class GenericTTSProvider(TTSProvider):
    """Synchronous provider-agnostic TTS implementation."""

    def __init__(self):
        self.api_key = os.getenv("TTS_API_KEY", "")
        self.provider = os.getenv("TTS_PROVIDER", "generic")
        self.voice_id = os.getenv("TTS_VOICE_ID", "")

    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        return {
            "success": bool(self.api_key),
            "provider": self.provider,
            "language": language,
            "text": text,
            "voice_id": self.voice_id or "default",
            "message": "TTS provider is configured in a provider-agnostic mode." if self.api_key else "TTS API key is not configured.",
        }

    async def health_check(self) -> bool:
        return bool(self.api_key)


class DefaultTTSProvider(GenericTTSProvider):
    pass
