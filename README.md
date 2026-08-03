# 🌊 هرمزگان هوشمند

سیستم دانش‌گراف هوشمند استان هرمزگان — شامل چت‌بات هوشمند، نقشه تعاملی، اطلس دوربین‌ها و داشبوردهای تحلیلی.

## وضعیت فعلی
- آمادهٔ توسعه محلی و اجرا با Docker Compose.
- نکات شناخته‌شده: ناسازگاری نام متغیر محیطی دیتابیس (DATABASE_URL vs DATABASE_PATH) و وجود فایل باینری بزرگ (`backend/audio.wav`) در مخزن.

## پیش‌نیازها
- Docker & docker-compose (پیشنهادی)
- یا Python 3.11+، Node 18+، npm
- (اختیاری) Git LFS برای فایل‌های بزرگ

## راه‌اندازی سریع (با Docker)
```bash
docker-compose up -d
# سپس:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

## راه‌اندازی محلی (بدون Docker)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd ../frontend
npm install
npm start
```

## اجرای موتور Bandari (اختیاری)
```bash
cd bandari-engine-2026/bandari-engine
npm install
npm start
```

## متغیرهای محیطی (نمونه .env)
- DATABASE_PATH=./data/hdp_v2.db  # یا DATABASE_URL=sqlite:///./hermezgan.db (هماهنگ کنید)
- FASTAPI_ENV=production
- REACT_APP_API_URL=http://localhost:8000

## تست‌ها
- Backend: `pytest tests/ -v --cov=app` (در پوشه backend)
- Frontend: `npm test -- --coverage` (در پوشه frontend)

## نکات نگهداری
- یکسان‌سازی اسم متغیر دیتابیس بین کد و docker-compose (پیشنهاد: استفاده از DATABASE_URL به فرمت استاندارد SQLAlchemy).
- فایل‌های بزرگ (مثل `backend/audio.wav`) بهتر است حذف یا به Git LFS منتقل شوند تا حجم مخزن کاهش یابد.
- در `backend/main.py` یک تکرار واضح در افزودن `ping_router` وجود دارد — این روتر فقط باید یک‌بار اضافه شود؛ لطفاً بررسی شود.

## ساختار کلی
```
hermezgan-intelligent/
├── backend/                # FastAPI backend (app/، main.py، requirements*.txt، Dockerfile)
├── frontend/               # React frontend (src/, public/, package.json, Dockerfile)
├── bandari-engine-2026/    # موتور Bandari (Node) — مستقل، npm-based
├── database/               # مایگریشن‌ها / اسکریپت‌های DB
├── docs/                   # مستندات تکمیلی
├── scripts/                # ابزارهای کمکی و تبدیل دیتا
├── HermezganMobile/        # پروژه موبایل (Expo / React Native)
├── docker-compose.yml      # راه‌اندازی چندکانتینری: backend, frontend, redis
├── README.md
└── فایل‌های کمکی و اسکریپت‌های تست/ایمپورت
```

## مجوز
MIT License

---

این README در مسیر `README.md` آپدیت شد تا راه‌اندازی، متغیرهای محیطی و نکات نگهداری را روشن کند. اگر می‌خواهید من تغییرات فنی دیگری هم اعمال کنم (حذف یا انتقال `backend/audio.wav`، یکسان‌سازی env در کد و docker-compose، یا حذف تکرار `ping_router` در `backend/main.py`) بگویید تا آن‌ها را هم اجرا کنم.
