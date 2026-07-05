# Speech Interface Implementation Guide

## Overview

The Speech Interface module enables voice-based interaction with Hermezgan Intelligent through:
- **ASR (Automatic Speech Recognition)**: Converting spoken words to text
- **TTS (Text-to-Speech)**: Converting text responses to spoken audio

## Installation

### Required Packages

```bash
# Core speech packages
pip install speech-recognition==3.10.0
pip install pyttsx3==2.90
pip install gtts==2.4.0

# System dependencies (for pyttsx3)
# Ubuntu/Debian:
sudo apt-get install espeak ffmpeg libespeak1

# macOS:
brew install espeak

# Windows: Already included or use SAPI5
```

## Architecture

```
┌─────────────────────────────────────────┐
│       Speech Interface Module           │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────┐   │
│  │   ASR (Speech-to-Text)         │   │
│  ├────────────────────────────────┤   │
│  │ • Google Speech Recognition    │   │
│  │ • Microphone input             │   │
│  │ • Audio file processing        │   │
│  │ • Language support: fa-IR      │   │
│  └────────────────────────────────┘   │
│                                         │
│  ┌────────────────────────────────┐   │
│  │   TTS (Text-to-Speech)         │   │
│  ├────────────────────────────────┤   │
│  │ • pyttsx3 (offline)            │   │
│  │ • gTTS (online)                │   │
│  │ • Audio file output            │   │
│  │ • Byte stream support          │   │
│  └────────────────────────────────┘   │
│                                         │
│  ┌────────────────────────────────┐   │
│  │   Voice Chat (End-to-End)      │   │
│  ├────────────────────────────────┤   │
│  │ 1. Audio Input (Speech)        │   │
│  │ 2. Convert to Text (ASR)       │   │
│  │ 3. Process (Chat Service)      │   │
│  │ 4. Convert to Audio (TTS)      │   │
│  │ 5. Audio Output (Speech)       │   │
│  └────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## API Endpoints

### 1. Speech-to-Text

**Endpoint**: `POST /api/v1/voice/speech-to-text`

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/voice/speech-to-text \
  -F "file=@audio.wav" \
  -F "language=fa-IR"
```

**Response**:
```json
{
  "status": "success",
  "text": "نزدیک‌ترین بیمارستان کجاست؟",
  "confidence": 0.95,
  "file_name": "audio.wav"
}
```

### 2. Text-to-Speech

**Endpoint**: `POST /api/v1/voice/text-to-speech`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/voice/text-to-speech?text=سلام&language=fa" \
  --output response.mp3
```

**Response**: Audio file (MP3)

### 3. Voice Chat (End-to-End)

**Endpoint**: `POST /api/v1/voice/voice-chat`

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/voice/voice-chat \
  -F "file=@audio.wav" \
  -F "user_id=user123" \
  -F "language=fa-IR"
```

**Response**:
```json
{
  "status": "success",
  "user_message": "نزدیک‌ترین بیمارستان کجاست؟",
  "stt_confidence": 0.95,
  "chat_response": "نزدیک‌ترین بیمارستان: بیمارستان فوق‌تخصصی کودکان...",
  "chat_intent": "location_query",
  "audio_url": "/api/v1/voice/text-to-speech?text=..."
}
```

## Usage Examples

### Python

```python
from app.core.speech_interface import get_speech_interface

speech_interface = get_speech_interface()

# Speech to Text
text, confidence = speech_interface.speech_to_text(
    audio_file="user_query.wav",
    language="fa-IR"
)
print(f"User said: {text} (confidence: {confidence})")

# Text to Speech
speech_interface.text_to_speech(
    text="سلام! به سیستم هوشمند هرمزگان خوش‌آمدید",
    output_file="response.mp3",
    language="fa"
)

# Voice Chat (End-to-End)
text, confidence = speech_interface.process_voice_query(
    audio_file="user_audio.wav"
)
```

### JavaScript/Frontend

```javascript
// Using Web Speech API (browser)
const recognition = new webkitSpeechRecognition();
recognition.lang = 'fa-IR';
recognition.start();

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  console.log('User said:', transcript);
  
  // Send to backend
  fetch('/api/v1/chat/message', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      message: transcript,
      user_id: 'user123'
    })
  }).then(res => res.json()).then(data => {
    // Play response
    const audio = new Audio(`/api/v1/voice/text-to-speech?text=${encodeURIComponent(data.response)}`);
    audio.play();
  });
};
```

## Configuration

### pyttsx3 Settings

```python
engine = pyttsx3.init()

# Set speech rate (default: 200)
engine.setProperty('rate', 150)

# Set volume (0.0 - 1.0)
engine.setProperty('volume', 0.9)

# Set voice (available voices vary by OS)
voices = engine.getProperty('voices')
for voice in voices:
    if 'Persian' in voice.name or 'Farsi' in voice.name:
        engine.setProperty('voice', voice.id)
        break
```

### Language Codes

| Language | Code | Module |
|----------|------|--------|
| Persian/Farsi | `fa-IR` | ASR (Google) |
| Persian/Farsi | `fa` | TTS |
| English | `en-US` | ASR/TTS |
| German | `de-DE` | ASR/TTS |

## Troubleshooting

### Issue: "Speech Recognition not available"

**Solution**: Install and test speech_recognition

```bash
pip install --upgrade speech-recognition
# Test:
python -c "import speech_recognition; print('OK')"
```

### Issue: "Could not understand audio"

**Solution**: 
- Check audio quality and format
- Ensure Farsi audio (fa-IR language)
- Reduce background noise
- Check internet connection (for Google ASR)

### Issue: "No voice output"

**Solution**:
- Check pyttsx3 installation
- On Linux: install espeak
- Test: `python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"`

## Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| Speech-to-Text | 2-5s | Depends on audio duration |
| Text-to-Speech | 0.5-2s | Offline (pyttsx3) |
| Voice Chat (E2E) | 5-10s | Total time for full pipeline |

## Future Enhancements

1. ✅ Real-time streaming ASR
2. ✅ Local Farsi TTS models
3. ✅ Speaker identification
4. ✅ Emotion detection
5. ✅ Multi-language voice commands
6. ✅ Voice biometrics

## Security

- All audio files are temporary (deleted after processing)
- No audio logging unless explicitly enabled
- Consider privacy: inform users about voice recording
- Use HTTPS for audio transmission

## References

- [SpeechRecognition Documentation](https://github.com/Uberi/speech_recognition)
- [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)
- [gTTS Documentation](https://gtts.readthedocs.io/)
