"""Speech Interface - ASR (Speech-to-Text) and TTS (Text-to-Speech)"""

import os
import io
from typing import Optional, Tuple
from loguru import logger

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.warning("speech_recognition not available")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gtts not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")

class SpeechInterface:
    """Speech Recognition and Text-to-Speech Interface"""
    
    def __init__(self):
        """Initialize Speech Interface"""
        logger.info("🚀 Initializing Speech Interface...")
        
        # ASR (Speech-to-Text)
        self.recognizer = None
        if SR_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                logger.info("✅ Speech Recognition initialized")
            except Exception as e:
                logger.warning(f"Speech Recognition initialization error: {e}")
        
        # TTS (Text-to-Speech) - using pyttsx3 for offline support
        self.tts_engine = None
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # Configure for Farsi if possible
                self.tts_engine.setProperty('rate', 150)  # Speech rate
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                logger.info("✅ Text-to-Speech engine initialized")
            except Exception as e:
                logger.warning(f"TTS engine initialization error: {e}")
        
        logger.info("✅ Speech Interface initialized")
    
    def speech_to_text(
        self,
        audio_file: Optional[str] = None,
        use_microphone: bool = False,
        language: str = "fa-IR"
    ) -> Tuple[str, float]:
        """Convert speech to text"""
        logger.info("🎙️ Converting speech to text...")
        
        if not self.recognizer:
            logger.error("Speech Recognition not available")
            return "", 0.0
        
        try:
            if use_microphone:
                # Use microphone input
                with sr.Microphone() as source:
                    logger.info("🎙️ Listening...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=10)
            
            elif audio_file:
                # Use audio file
                if not os.path.exists(audio_file):
                    logger.error(f"Audio file not found: {audio_file}")
                    return "", 0.0
                
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            
            else:
                logger.error("Either audio_file or use_microphone must be provided")
                return "", 0.0
            
            # Recognize speech using Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                confidence = 0.95  # Google doesn't provide confidence score
                logger.info(f"✅ Recognized: {text}")
                return text, confidence
            
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return "", 0.0
            
            except sr.RequestError as e:
                logger.error(f"Error from speech recognition service: {e}")
                return "", 0.0
        
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return "", 0.0
    
    def text_to_speech(
        self,
        text: str,
        output_file: Optional[str] = None,
        language: str = "fa",
        play_audio: bool = False
    ) -> bool:
        """Convert text to speech"""
        logger.info(f"🔊 Converting text to speech: {text[:50]}...")
        
        try:
            # Try pyttsx3 first (offline)
            if self.tts_engine:
                self.tts_engine.say(text)
                
                if output_file:
                    self.tts_engine.save_to_file(text, output_file)
                    logger.info(f"✅ Audio saved to {output_file}")
                
                if play_audio:
                    self.tts_engine.runAndWait()
                    logger.info("✅ Audio played")
                
                return True
            
            # Fall back to gTTS (requires internet)
            elif GTTS_AVAILABLE and output_file:
                tts = gTTS(text=text, lang=language, slow=False)
                tts.save(output_file)
                logger.info(f"✅ Audio saved to {output_file} using gTTS")
                return True
            
            else:
                logger.warning("No TTS engine available")
                return False
        
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return False
    
    def text_to_speech_bytes(
        self,
        text: str,
        language: str = "fa"
    ) -> Optional[bytes]:
        """Convert text to speech and return as bytes"""
        logger.info(f"🔊 Converting text to speech bytes: {text[:50]}...")
        
        try:
            if GTTS_AVAILABLE:
                tts = gTTS(text=text, lang=language, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                return fp.getvalue()
            else:
                logger.warning("gTTS not available for byte conversion")
                return None
        
        except Exception as e:
            logger.error(f"Text-to-speech bytes error: {e}")
            return None
    
    def process_voice_query(
        self,
        audio_file: Optional[str] = None,
        use_microphone: bool = False
    ) -> Tuple[str, float]:
        """Process voice query end-to-end"""
        logger.info("🎙️ Processing voice query...")
        
        # Convert speech to text
        text, confidence = self.speech_to_text(
            audio_file=audio_file,
            use_microphone=use_microphone,
            language="fa-IR"
        )
        
        if text:
            logger.info(f"✅ Voice query processed: {text} (confidence: {confidence})")
        else:
            logger.warning("⚠️ Failed to process voice query")
        
        return text, confidence


# Global Speech Interface Instance
speech_interface = None

def get_speech_interface() -> SpeechInterface:
    """Get or initialize speech interface"""
    global speech_interface
    if speech_interface is None:
        speech_interface = SpeechInterface()
    return speech_interface
