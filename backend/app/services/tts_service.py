"""Text-to-Speech (TTS) Service Integration for HDP

Provides unified TTS interface supporting multiple providers.
Supports Persian/Bandari dialect synthesis with caching.
"""

import os
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import base64
from pathlib import Path

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        """
        Synthesize text to speech
        
        Returns:
            {
                "success": bool,
                "audio_base64": str,
                "audio_format": str,
                "duration_seconds": float,
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available"""
        pass


class GoogleTTSProvider(TTSProvider):
    """Google Cloud Text-to-Speech Provider"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_TTS_API_KEY")
        self.api_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self.voice_name = "fa-IR-Standard-A"  # Persian female voice
    
    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        """Synthesize using Google Cloud TTS"""
        try:
            if not self.api_key:
                logger.error("Google TTS API key not configured")
                return {"success": False, "error": "API key not configured"}
            
            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": "fa-IR",
                    "name": self.voice_name
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "pitch": 0.0,
                    "speakingRate": kwargs.get("speed", 1.0)
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_content = data.get("audioContent")
                
                return {
                    "success": True,
                    "audio_base64": audio_content,
                    "audio_format": "mp3",
                    "duration_seconds": len(text) / 150,  # Approximate
                    "provider": "google"
                }
            else:
                logger.error(f"Google TTS error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Google TTS synthesis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> bool:
        """Check Google TTS availability"""
        try:
            if not self.api_key:
                return False
            
            payload = {
                "input": {"text": "سلام"},
                "voice": {"languageCode": "fa-IR", "name": self.voice_name},
                "audioConfig": {"audioEncoding": "MP3"}
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Google TTS health check failed: {e}")
            return False


class AzureTTSProvider(TTSProvider):
    """Microsoft Azure Text-to-Speech Provider"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_TTS_API_KEY")
        self.region = os.getenv("AZURE_TTS_REGION", "eastus")
        self.api_url = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
        self.voice_name = "fa-IR-DilaraNeural"  # Persian female voice
    
    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        """Synthesize using Azure TTS"""
        try:
            if not self.api_key:
                logger.error("Azure TTS API key not configured")
                return {"success": False, "error": "API key not configured"}
            
            ssml = f"""
            <speak version='1.0' xml:lang='fa-IR'>
                <voice name='{self.voice_name}'>
                    <prosody rate='{kwargs.get("speed", 1.0)}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3"
            }
            
            response = requests.post(
                self.api_url,
                data=ssml.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                audio_base64 = base64.b64encode(response.content).decode()
                return {
                    "success": True,
                    "audio_base64": audio_base64,
                    "audio_format": "mp3",
                    "duration_seconds": len(text) / 150,
                    "provider": "azure"
                }
            else:
                logger.error(f"Azure TTS error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Azure TTS synthesis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> bool:
        """Check Azure TTS availability"""
        try:
            if not self.api_key:
                return False
            
            ssml = f"""
            <speak version='1.0' xml:lang='fa-IR'>
                <voice name='{self.voice_name}'>سلام</voice>
            </speak>
            """
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/ssml+xml"
            }
            
            response = requests.post(
                self.api_url,
                data=ssml.encode('utf-8'),
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Azure TTS health check failed: {e}")
            return False


class LocalTTSProvider(TTSProvider):
    """Local TTS Provider (gTTS or pyttsx3 fallback)"""
    
    def __init__(self):
        try:
            from gtts import gTTS
            self.gTTS = gTTS
            self.available = True
        except ImportError:
            logger.warning("gTTS not installed, local TTS disabled")
            self.available = False
    
    async def synthesize(self, text: str, language: str = "fa", **kwargs) -> Dict[str, Any]:
        """Synthesize using local TTS"""
        try:
            if not self.available:
                return {"success": False, "error": "Local TTS not available"}
            
            tts = self.gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            temp_path = f"/tmp/tts_{hashlib.md5(text.encode()).hexdigest()}.mp3"
            tts.save(temp_path)
            
            # Read and encode to base64
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            audio_base64 = base64.b64encode(audio_data).decode()
            
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "audio_format": "mp3",
                "duration_seconds": len(text) / 150,
                "provider": "local"
            }
        except Exception as e:
            logger.error(f"Local TTS synthesis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> bool:
        """Check local TTS availability"""
        return self.available


class TTSService:
    """Unified Text-to-Speech Service"""
    
    def __init__(self):
        self.provider_name = os.getenv("TTS_PROVIDER", "local")
        self.cache_dir = Path(os.getenv("TTS_CACHE_DIR", "./cache/tts"))
        self.cache_enabled = os.getenv("TTS_CACHE_ENABLED", "true").lower() == "true"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize provider
        self.provider = self._init_provider()
        logger.info(f"✅ TTS Service initialized with provider: {self.provider_name}")
    
    def _init_provider(self) -> TTSProvider:
        """Initialize TTS provider"""
        if self.provider_name == "google":
            return GoogleTTSProvider()
        elif self.provider_name == "azure":
            return AzureTTSProvider()
        else:
            return LocalTTSProvider()
    
    def _get_cache_key(self, text: str, language: str, speed: float) -> str:
        """Generate cache key for TTS result"""
        key_str = f"{text}_{language}_{speed}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load TTS result from cache"""
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            import json
            with open(cache_file, "r") as f:
                return json.load(f)
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Save TTS result to cache"""
        if not self.cache_enabled:
            return
        
        import json
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(result, f)
    
    async def synthesize(
        self,
        text: str,
        language: str = "fa",
        speed: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synthesize text to speech with caching
        
        Args:
            text: Text to synthesize
            language: Language code (default: fa)
            speed: Speech speed (0.5-2.0)
            **kwargs: Additional provider-specific arguments
        
        Returns:
            {
                "success": bool,
                "audio_base64": str (or None if failed),
                "audio_format": str,
                "duration_seconds": float,
                "provider": str,
                "cached": bool,
                "error": str (if failed)
            }
        """
        try:
            # Check cache
            cache_key = self._get_cache_key(text, language, speed)
            cached_result = self._load_from_cache(cache_key)
            if cached_result:
                cached_result["cached"] = True
                logger.info(f"✅ TTS result loaded from cache")
                return cached_result
            
            # Synthesize
            result = await self.provider.synthesize(text, language, speed=speed, **kwargs)
            result["cached"] = False
            
            if result["success"]:
                self._save_to_cache(cache_key, result)
                logger.info(f"✅ TTS synthesized: {len(text)} chars")
            
            return result
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_base64": None,
                "provider": self.provider_name,
                "cached": False
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check TTS service health"""
        try:
            is_healthy = await self.provider.health_check()
            return {
                "status": "healthy" if is_healthy else "degraded",
                "provider": self.provider_name,
                "cache_enabled": self.cache_enabled,
                "cache_dir": str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"TTS health check failed: {e}")
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e)
            }


# Global instance
_tts_service = None


def get_tts_service() -> TTSService:
    """Get or create TTS service instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
