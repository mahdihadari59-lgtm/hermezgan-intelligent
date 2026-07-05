"""Pull Request Template for NLP & RAG Features"""

# Pull Request: 🧠 NLP Pipeline + 🔄 RAG System + 📍 Location Services + 💬 Chat Interface

## 📋 Description

This PR implements the core AI and location services for Hermezgan Intelligent:

### 🧠 NLP Engine (Farsi Text Processing)
- Text normalization using Hazm library
- Tokenization and lemmatization
- Named Entity Recognition (NER)
- Intent classification (pattern-based + transformer-based)
- Sentence embeddings using multilingual models

### 🔄 RAG Pipeline (Retrieval-Augmented Generation)
- Knowledge base loading from entities
- Vector similarity search with cosine similarity
- Context generation from retrieved documents
- Template-based response generation
- Full end-to-end RAG processing

### 📍 Location Services
- Distance calculation using geodesic formulas
- Nearest services discovery within radius
- Route information and ETA calculation
- Geographic search and suggestions

### 💬 Chat Service
- Context-aware message processing
- Intent-driven response generation
- Location integration for nearby services
- Chat history management

### 🎤 Speech Interface (NEW)
- Speech-to-Text (ASR) using Google Speech Recognition
- Text-to-Speech (TTS) using pyttsx3 and gTTS
- End-to-end voice chat processing
- Support for Farsi language

## 🎯 Key Features

✅ Farsi language support (normalized text processing)
✅ Intent classification with 5 main intents: location_query, direction, service_inquiry, greeting, other
✅ Geographic routing with distance and time estimates
✅ Voice interaction support (ASR + TTS)
✅ RAG-based knowledge retrieval
✅ Context-aware responses
✅ Extensible architecture for new services

## 📂 Files Changed

### Backend Core Modules
- `backend/app/core/nlp_engine.py` - Farsi NLP processing (300+ lines)
- `backend/app/core/rag_pipeline.py` - RAG implementation (250+ lines)
- `backend/app/core/location_service.py` - GPS and routing (200+ lines)
- `backend/app/core/speech_interface.py` - ASR and TTS (250+ lines)

### Services
- `backend/app/services/chat_service.py` - Chat logic (250+ lines)
- `backend/app/services/__init__.py`

### API Endpoints
- `backend/app/api/v1/endpoints/chat.py` - Chat API endpoints
- `backend/app/api/v1/endpoints/locations.py` - Location API endpoints
- `backend/app/api/v1/endpoints/voice.py` - Voice API endpoints (NEW)

### Database
- `backend/scripts/seed_database.py` - Database initialization and seeding
- `database/seeds/organizations.json` - Sample organizations data

### Dependencies
- `backend/requirements_speech.txt` - New speech packages (speech-recognition, pyttsx3, gtts)

## 🧪 Testing

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "نزدیک‌ترین بیمارستان کجاست؟",
    "user_id": "user123",
    "latitude": 27.2158,
    "longitude": 56.2808
  }'
```

### Speech-to-Text
```bash
curl -X POST http://localhost:8000/api/v1/voice/speech-to-text \
  -F "file=@audio.wav" \
  -F "language=fa-IR"
```

### Text-to-Speech
```bash
curl -X POST "http://localhost:8000/api/v1/voice/text-to-speech?text=سلام&language=fa" \
  --output response.mp3
```

### Voice Chat (End-to-End)
```bash
curl -X POST http://localhost:8000/api/v1/voice/voice-chat \
  -F "file=@audio.wav" \
  -F "user_id=user123" \
  -F "language=fa-IR"
```

## 🚀 Deployment Notes

- Speech Recognition requires internet for Google API
- pyttsx3 works offline for TTS
- gTTS requires internet for online TTS
- NLP models auto-download on first use
- Database seeding required: `python scripts/seed_database.py`

## ✅ Checklist

- [x] Code follows PEP 8 style guide
- [x] All functions have docstrings
- [x] Logging implemented for debugging
- [x] Error handling in place
- [x] Farsi language support verified
- [x] API documentation in README
- [x] Database schema updated
- [x] Sample data provided

## 🔗 Related Issues

- Implements: Hermezgan Intelligent core features
- Related: Knowledge Graph, Location Services, Voice Interface

## 📸 Screenshots

API Documentation: `http://localhost:8000/api/docs`

---

**Branch**: `feature/nlp-rag-pipeline`
**Base**: `main`
**Commits**: 2
**Files Changed**: 15
