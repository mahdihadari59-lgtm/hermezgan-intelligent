# 🏗️ معماری سیستم Hermezgan Intelligent

## نمای کلی

```
┌─────────────────────────────────────────────────────────┐
│            User Interface Layer                         │
│      (Web + Mobile + Voice Interface)                  │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────▼────────────┐
        │   API Gateway         │
        │  Authentication       │
        └──────────┬────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│           Backend Services (Python)                    │
├─────────────────────────────────────────────────────────┤
│ ├─ Knowledge Engine (Graph Processing)                 │
│ ├─ NLP Pipeline (Farsi Text Understanding)             │
│ ├─ RAG Engine (Retrieval + Generation)                 │
│ ├─ Location Services (GPS + Routing)                   │
│ ├─ Analytics Engine (Reports & Statistics)             │
│ └─ Meta-Learning (Continuous Improvement)              │
└──────────────────┬──────────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼────┐  ┌────▼────┐  ┌─────▼──┐
│ SQLite  │  │ Vector   │  │ Redis  │
│(Dev)    │  │ Database │  │(Cache) │
└─────────┘  └──────────┘  └────────┘
```

## مؤلفه‌های اصلی

### 1. Knowledge Graph Engine
- تجزیه گره‌ها و یال‌ها
- جستجوی پیشرفته در گراف
- محاسبه روابط و مسیرها

### 2. NLP Pipeline
- Tokenization (فارسی-specific)
- Named Entity Recognition
- Intent Classification
- Semantic Understanding

### 3. RAG System
- Vector Embeddings
- Document Retrieval
- Context Assembly
- LLM-based Generation

### 4. Location Services
- GPS Tracking
- Distance Calculation
- Route Finding
- Nearest Service Discovery

---

## جریان داده

```
1. User Input → 2. NLP Processing → 3. Graph Query → 4. RAG Pipeline → 5. Output
```