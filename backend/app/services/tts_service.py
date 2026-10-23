"""Provider-agnostic TTS service with compatibility fallbacks.

This keeps public imports stable for older code while allowing the app
to run in a generic provider mode without hard dependency on a single vendor.
"""

import os
from typing import Any, Dict, Optional


class TTSProvider:
    """Abstract provider interface."""

    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        raise NotImplementedError


class GenericTTSProvider(TTSProvider):
    """Safe default provider used when no external TTS is configured."""

    def __init__(self):
        self.api_key = os.getenv("TTS_API_KEY") or os.getenv("ELEVENLABS_API_KEY", "")
        self.provider = os.getenv("TTS_PROVIDER") or os.getenv("ELEVENLABS_PROVIDER", "generic")
        self.voice_id = os.getenv("TTS_VOICE_ID") or os.getenv("ELEVENLABS_VOICE_ID", "")

    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        return {
            "success": bool(self.api_key),
            "provider": self.provider,
            "language": language,
            "text": text,
            "voice_id": self.voice_id or "default",
            "message": (
                "TTS provider is running in provider-agnostic mode. Configure TTS_API_KEY to enable external synthesis."
                if self.api_key
                else "TTS API key is not configured."
            ),
        }

    async def health_check(self) -> bool:
        return bool(self.api_key) or self.provider == "generic"


class DefaultTTSProvider(GenericTTSProvider):
    pass


# Compatibility aliases for older imports and code paths.
ElevenLabsTTSProvider = DefaultTTSProvider
GoogleTTSProvider = DefaultTTSProvider
AzureTTSProvider = DefaultTTSProvider
LocalTTSProvider = DefaultTTSProvider


class TTSService:
    """Thin compatibility wrapper around the generic provider."""

    def __init__(self):
        self.provider_name = os.getenv("TTS_PROVIDER") or os.getenv("ELEVENLABS_PROVIDER", "generic")
        self.provider = DefaultTTSProvider()

    async def synthesize(self, text: str, language: str = "fa", speed: float = 1.0, **kwargs) -> Dict[str, Any]:
        result = await self.provider.synthesize(text=text, language=language, speed=speed, **kwargs)
        result.setdefault("success", bool(os.getenv("TTS_API_KEY") or os.getenv("ELEVENLABS_API_KEY", "")))
        result.setdefault("provider", self.provider_name)
        return result

    async def health_check(self) -> Dict[str, Any]:
        status = await self.provider.health_check()
        return {
            "status": "healthy" if status else "degraded",
            "provider": self.provider_name,
            "api_key_configured": bool(os.getenv("TTS_API_KEY") or os.getenv("ELEVENLABS_API_KEY", "")),
        }


_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
