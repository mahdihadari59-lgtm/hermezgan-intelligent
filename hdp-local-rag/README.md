# 🧠 HDP Local RAG

سیستم هوش مصنوعی RAG محلی برای استان هرمزگان — قابل اجرا روی Termux (Android)

## 🏗️ معماری

- **Python (FastAPI)** — Core: Orchestrator, Experts, RAG, AI Tools
- **Deno (Oak)** — Frontend Web UI
- **SQLite3** — پایگاه داده محلی شما
- **Google Gemini + Local LLM (Ollama) + Levels** — هوش مصنوعی

## 📦 پیش‌نیازها

| ابزار | نسخه |
|-------|------|
| Python | 3.11+ |
| Deno | 1.40+ |
| SQLite3 | 3.40+ |
| Node.js | 20+ (optional) |

## 🚀 نصب و اجرا

```bash
# 1. Clone
cd ~/hdp-local-rag

# 2. Config
cp .env.example .env
# ویرایش .env و وارد کردن API keys

# 3. Install
./scripts/install.sh

# 4. Run
./scripts/start.sh
```

## 📊 API Endpoints

| Endpoint | Method | توضیح |
|----------|--------|-------|
| `/ask` | POST | پرسیدن سؤال |
| `/health` | GET | وضعیت سرویس |
| `/stats` | GET | آمار جداول دیتابیس |

## 🗄️ جداول پشتیبانی شده

pois, tourism_poi, markets, roads, traffic_data, fuel_stations, restaurants, hotels, cities, neighborhoods, bandari_vocabulary_master, و ۴۵+ جدول دیگر...

## 📝 مثال استفاده

```bash
curl -X POST http://localhost:8000/ask   -H "Content-Type: application/json"   -d '{"query": "رستوران خوب در بندرعباس کجاست؟"}'
```

## 🏆 توسعه‌دهنده

HDP Team — Hormozgan Data Platform
