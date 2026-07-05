# 🌊 Hermezgan Intelligent - پروژه هوشمند هرمزگان

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Node.js](https://img.shields.io/badge/node.js-16%2B-green)

## 📋 نمای کلی پروژه

پروژه **Hermezgan Intelligent** یک سیستم یکپارچه برای مدیریت دانش‌گراف شهر بندرعباس است که به کاربران امکان می‌دهد:

✅ **پاسخ به سؤالات فارسی** - موتور NLP هوشمند
✅ **یافتن نزدیک‌ترین خدمات** - جستجوی مکان‌بنیان
✅ **مشاهده روی نقشه** - OpenStreetMap Integration
✅ **تحلیل داده‌ها** - گزارش‌های تفصیلی
✅ **گفتگوی طبیعی** - چت‌بات هوشمند

---

## 🏗️ معماری پروژه

```
┌────────────────────────────────────────────────────────────────┐
│                    Frontend (React + Node.js)                  │
│              Chat │ Map │ Dashboard │ Search                   │
└────────────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────▼───────────────┐
        │   API Gateway (Express)    │
        ��� Authentication & Rate Limit│
        └────────────┬───────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────┐
│              Backend (Python + FastAPI)                        │
│ ├─ NLP Engine                                                  │
│ ├─ RAG Pipeline                                                │
│ ├─ Location Services                                           │
│ ├─ Analytics Engine                                            │
│ └─ Meta-Learning System                                        │
└────────────────────┬───────────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐   ┌──────▼──────┐  ┌────▼─────┐
│ SQLite  │   │Vector DB    │  │  Redis   │
│ (Dev)   │   │(Embeddings) │  │ (Cache)  │
└─────────┘   └─────────────┘  └──────────┘
```

---

## 🚀 شروع سریع

### پیش‌نیازها
- Python 3.9+
- Node.js 16+
- Git
- Docker & Docker Compose (اختیاری)

### نصب و اجرا

```bash
# Clone Repository
git clone https://github.com/mahdihadari59-lgtm/hermezgan-intelligent.git
cd hermezgan-intelligent

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # یا: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Database Setup
python scripts/seed_database.py

# Run Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend Setup (در Terminal جدید)
cd ../frontend
npm install
npm start
```

### Docker Setup

```bash
docker-compose up -d
```

---

## 📂 ساختار پروژه

```
hermezgan-intelligent/
├── backend/                      # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI Entry Point
│   │   ├── api/v1/              # API Routes
│   │   ├── core/                # Core Modules (NLP, RAG, etc.)
│   │   ├── models/              # Database Models
│   │   ├── services/            # Business Logic
│   │   └── database/            # Database Connection
│   ├── tests/
│   ├── scripts/                 # Seed & Migration Scripts
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                     # React + Node.js Frontend
│   ├── src/
│   │   ├── components/          # React Components
│   │   ├── pages/               # Page Components
│   │   ├── services/            # API Calls
│   │   ├── hooks/               # Custom Hooks
│   │   └── store/               # Redux Store
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
│
├── database/                     # SQL & Seeds
│   ├── migrations/              # Database Migrations
│   ├── seeds/                   # Initial Data
│   └── schema.sql
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
│
├── docker-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔌 API Endpoints

### Chat API
```
POST   /api/v1/chat/message      - ارسال پیام
GET    /api/v1/chat/history      - دریافت تاریخ گفتگو
```

### Knowledge Graph
```
GET    /api/v1/graph/entities    - دریافت موجودیت‌ها
GET    /api/v1/graph/relations   - دریافت روابط
POST   /api/v1/graph/entity      - ایجاد موجودیت
```

### Location Services
```
GET    /api/v1/locations/search  - جستجوی مکانی
GET    /api/v1/locations/nearest - نزدیک‌ترین خدمات
GET    /api/v1/locations/route   - مسیریابی
```

### Analytics
```
GET    /api/v1/analytics/stats   - آمار کلی
GET    /api/v1/analytics/report  - گزارش‌های تفصیلی
```

---

## 🛠️ فناوری‌های استفاده‌شده

### Backend
- **FastAPI** - Web Framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data Validation
- **Transformers** - NLP Models
- **Geopy** - Location Services

### Frontend
- **React** - UI Framework
- **Leaflet** - Interactive Maps
- **Redux** - State Management
- **Tailwind CSS** - Styling

### Database
- **SQLite** - Development
- **PostgreSQL** - Production
- **Redis** - Caching

---

## 📝 مثال استفاده

### Chat Example
```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "نزدیک‌ترین بیمارستان کجاست؟"}'
```

### Response
```json
{
  "response": "نزدیک‌ترین بیمارستان، بیمارستان فوق‌تخصصی کودکان است...",
  "location": {
    "latitude": 27.2158,
    "longitude": 56.2808,
    "distance_km": 2.3
  }
}
```

---

## 🧪 تست‌ها

```bash
# Backend Tests
cd backend
pytest tests/ -v

# Frontend Tests
cd ../frontend
npm test
```

---

## 📚 مستندات

- [معماری سیستم](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [راهنمای استقرار](docs/DEPLOYMENT.md)
- [راهنمای مشارکت](docs/CONTRIBUTING.md)

---

## 🔧 متغیرهای محیط

یک فایل `.env` ایجاد کنید:

```env
# Backend
FASTAPI_ENV=development
DATABASE_URL=sqlite:///./hermezgan.db
SECRET_KEY=your-secret-key

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAP_TOKEN=your-mapbox-token
```

---

## 🚀 استقرار

### AWS EC2
```bash
# ایجاد Instance
aws ec2 run-instances --image-id ami-xxxxx
```

### VPS
```bash
ssh user@your-vps.com
cd /app
git pull origin main
docker-compose down && docker-compose up -d
```

---

## 👤 نویسنده

- **Mahdi Haidari Puri** - Project Lead & Full-Stack Developer
  - GitHub: [@mahdihadari59-lgtm](https://github.com/mahdihadari59-lgtm)
  - Email: mahdihadari59@gmail.com

---

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. جزئیات را در فایل [LICENSE](LICENSE) ببینید.

---

## 🤝 مشارکت

ما از مشارکت‌های جدید استقبال می‌کنیم! لطفاً [راهنمای مشارکت](docs/CONTRIBUTING.md) را بخوانید.

---

## 📞 تماس

- **Issues**: [GitHub Issues](https://github.com/mahdihadari59-lgtm/hermezgan-intelligent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahdihadari59-lgtm/hermezgan-intelligent/discussions)

---

**آخرین به‌روزرسانی**: ۱۴۰۵/۰۳/۲۵
