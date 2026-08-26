# هرمزگان هوشمند (Hermezgan Intelligent / HDP)

سیستم دانش‌گراف هوشمند شهر بندرعباس — پلتفرم هوشمند شهری برای استان هرمزگان، شامل موتور جستجوی دانش، گراف دانش، سیستم مسیریابی و ترافیک، تشخیص گویش بندری، و دستیار هوش مصنوعی مکالمه‌ای.

## ⚙️ ویژگی‌های اصلی

- **Copilot Gateway** — پردازش هوشمند پیام با تشخیص نیت (Intent Detection) و جستجو در ۱۰۵+ جدول پایگاه‌داده (بیش از ۵۶۰ هزار رکورد)
- **موتور دانش‌گراف** — جستجوی ترکیبی (Knowledge + Graph + Vector) با پشتیبانی از FTS5
- **موتور بندری (Bandari Engine)** — سرویس داخلی Python/FastAPI برای تشخیص لهجه، ترجمه، و پردازش زبانی گویش بندری (۹ گویش هرمزگانی)
- **تشخیص گفتار (Voice/STT)** — تبدیل گفتار به متن آفلاین با Vosk، ترکیب‌شده با پردازش گویش بندری
- **دستیار هوش مصنوعی** — یکپارچه با Gemini API برای پاسخ‌گویی مکالمه‌ای
- **سیستم مسیریابی و ترافیک** — اطلاعات جاده‌ها، نقاط حادثه‌خیز، دوربین‌ها، و وضعیت ترافیک زنده
- **گردشگری و POI** — جستجوی جاذبه‌های گردشگری، غذا، هتل، و نقاط مورد علاقه
- **TTS** — تبدیل متن به گفتار با ElevenLabs

## 🏗️ معماری و پشته‌ی فناوری

- **بک‌اند:** Python (FastAPI) + Pydantic v2
- **پایگاه‌داده:** SQLite (معماری چند-دیتابیسی: core, graph, knowledge, geo, media, events, search, vector)
- **فرانت‌اند:** React (Vite) + Zustand
- **محیط اجرا:** Termux (Android/aarch64) — offline-first، بدون وابستگی اجباری به سرویس‌های ابری
- **هوش مصنوعی:** Google Gemini API (مدل: `gemini-flash-latest`)
- **تشخیص گفتار:** Vosk (آفلاین)
- **تبدیل متن به گفتار:** ElevenLabs API

## 📂 ساختار پروژه

```
hermezgan-intelligent/
├── backend/                      # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── api/
│   │   │   └── v1/              # API Routes
│   │   ├── services/            # Business logic
│   │   ├── models/              # Database schemas
│   │   ├── database.py          # DB connection
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   ├── requirements-full.txt
│   └── Dockerfile
├── frontend/                     # React Frontend (Vite)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/              # Zustand state
│   │   ├── utils/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── HermezganMobile/              # React Native (Expo)
│   ├── app/
│   ├── app.json
│   └── package.json
├── docker-compose.yml
├── .env.example
└── docs/
    ├── ARCHITECTURE.md
    ├── INSTALL.md
    ├── API.md
    └── CHANGELOG.md
```

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

#### روی Linux/macOS/Windows (WSL):
```bash
# Python 3.10+
python --version

# Node.js 18+
node --version

# Git
git --version
```

#### روی Termux (Android):
```bash
pkg install python nodejs git

# اختیاری برای تکمیل‌تر:
pkg install build-essential
```

### گام‌های نصب

#### 1️⃣ کلون مخزن
```bash
cd ~
git clone https://github.com/mahdihadari59-lgtm/hermezgan-intelligent.git
cd hermezgan-intelligent
```

#### 2️⃣ تنظیم متغیرهای محیطی
```bash
# کپی فایل نمونه
cp .env.example .env

# ویرایش با ویرایشگر دلخواه
nano .env
```

**متغیرهای ضروری:**
```env
# Database
DATABASE_URL=sqlite:///hermozgan_master_final.db

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# ElevenLabs TTS
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Services Configuration
BACKEND_PORT=8001
FRONTEND_PORT=5173
PYTHONPATH=.
```

⚠️ **هرگز کلیدهای API را در چت یا کامیت‌های گیت به اشتراک نگذارید!**

#### 3️⃣ نصب وابستگی‌های بک‌اند
```bash
cd backend

# نصب محدود (پایه)
pip install -r requirements.txt

# یا نصب کامل (شامل Gemini, ElevenLabs, Vosk, ...)
pip install -r requirements-full.txt
```

#### 4️⃣ نصب وابستگی‌های فرانت‌اند (اختیاری)
```bash
cd frontend
npm install
```

#### 5️⃣ اجرای سرور
```bash
cd backend
python -m app.main
```

سرور روی `http://localhost:8001` بالا می‌آید.
مستندات تعاملی API در `http://localhost:8001/docs` قابل مشاهده است.

#### 6️⃣ اجرای فرانت‌اند (اختیاری، در ترمینال دوم)
```bash
cd frontend
npm run dev
```

فرانت‌اند روی `http://localhost:5173` بالا می‌آید.

## 🐳 راه‌اندازی با Docker

```bash
# ساخت و اجرای تمام سرویس‌ها
docker-compose up --build

# اجرا در پس‌زمینه
docker-compose up -d

# متوقف کردن
docker-compose down
```

## 📡 اندپوینت‌های کلیدی

| مسیر | توضیح |
|------|--------|
| `GET /api/v1/health/` | بررسی سلامت سرویس |
| `GET /api/v1/traffic/` | وضعیت ترافیک |
| `POST /api/v1/copilot/message` | پردازش پیام از طریق Copilot Gateway |
| `GET /api/v1/copilot/health` | سلامت دیتابیس Copilot |
| `POST /api/v1/ai/chat` | چت با دستیار Gemini |
| `GET /api/v1/ai/status` | وضعیت سرویس Gemini |
| `GET /api/v1/tts/status` | وضعیت سر��یس TTS |
| `POST /api/v1/bandari-voice/transcribe` | تبدیل گفتار به متن (Vosk) |
| `POST /api/v1/bandari-voice/transcribe-and-process` | گفتار → متن → تشخیص لهجه → ترجمه |
| `GET /api/v1/bandari-voice/status` | وضعیت سرویس گفتار بندری |

## 🧪 تست و اعتبارسنجی

```bash
# تست بک‌اند
cd backend
pytest tests/

# تست فرانت‌اند
cd frontend
npm test
```

## 🐞 عیب‌یابی رایج

### ❌ خطا: `ModuleNotFoundError: No module named 'app'`
**راه‌حل:** دستور را از مسیر `backend/` (نه `backend/app/`) اجرا کنید:
```bash
cd backend
python -m app.main
```

### ❌ خطا: `SyntaxError` در ابتدای فایل
**راه‌حل:** معمولاً خط جداکننده ناقص است. خط اول فایل را بررسی و حذف کنید.

### ❌ خطا: نشانه‌های `<<<<<<<`, `=======`, `>>>>>>>`
**راه‌حل:** تعارض‌های `git stash` حل‌نشده:
```bash
# پیدا کردن فایل‌های آلوده
git diff --name-only --diff-filter=U

# حل دستی و commit
git add .
git commit -m "resolve merge conflicts"
```

### ❌ خطا: `models/gemini-1.5-flash is not found`
**راه‌حل:** مدل‌های قدیمی Gemini توسط Google از رده خارج می‌شوند:
```bash
# بررسی مدل‌های فعال
export GOOGLE_API_KEY=your_key
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=${GOOGLE_API_KEY}" | jq '.models[].name'
```
سپس در `backend/app/api/v1/gemini.py` نام مدل را به‌روزرسانی کنید (پیشنهاد: `gemini-flash-latest`).

### ❌ خطا: `Port 8001 already in use`
**راه‌حل:**
```bash
# پیدا کردن فرایند اشغال‌کننده
lsof -i :8001
# یا در Termux:
netstat -tulpn | grep 8001

# کشتن فرایند
kill -9 <PID>
```

### ❌ خطا: `Database locked`
**راه‌حل:**
```bash
# حذف lock file
rm hermozgan_master_final.db-journal

# یا بازراه‌اندازی سرویس
pkill -f "python -m app.main"
sleep 2
python -m app.main
```

### ❌ خطا: `npm ci` lock file ناسازگار
**راه‌حل:**
```bash
cd frontend
rm package-lock.json
npm install
npm ci
```

## 📊 پایگاه‌داده

### جداول اصلی
- `users` — اطلاعات کاربران
- `entities` — نهادهای دانش‌گراف (مکان، شخص، سازمان، ...)
- `relations` — روابط بین نهادها
- `knowledge_items` — موارد دانشی
- `traffic_events` — رویدادهای ترافیکی
- `pois` — نقاط مورد علاقه (Places of Interest)

### بکاپ‌گیری
```bash
# بکاپ دیتابیس
sqlite3 hermozgan_master_final.db ".dump" > backup_$(date +%Y%m%d_%H%M%S).sql

# بازگردانی بکاپ
sqlite3 hermozgan_master_final.db < backup_20260826_120000.sql
```

## 🔐 امنیت

- ✅ استفاده از `.env` برای متغیرهای حساس
- ✅ سرویس CORS محدود
- ✅ Validation تمام Input‌ها با Pydantic v2
- ✅ Hash Password با bcrypt
- ✅ استفاده از HTTPS برای ارتباطات تولیدی

## 📝 CHANGELOG

مشاهده تغییرات در: [CHANGELOG.md](docs/CHANGELOG.md)

### نسخه‌های اخیر
- **v2.1.3** (2026-08-06) — Docker، CI/CD، مستندات کامل
- **v2.1.1** (2026-08-25) — Pre-release
- **v1.0.1** (2026-08-03) — LFS support، بکاپ اطلاعات بندرعباس
- **v1.0.0** (2026-08-03) — اولین انتشار پایدار

## 🤝 مشارکت

برای مشارکت:
1. Fork کنید
2. Branch جدید بسازید: `git checkout -b feature/amazing-feature`
3. تغییرات ��ود را Commit کنید: `git commit -m 'feat: add amazing feature'`
4. Push کنید: `git push origin feature/amazing-feature`
5. Pull Request باز کنید

## 📄 لیسانس

این پروژه تحت لیسانس MIT منتشر شده است.
برای جزئیات: [LICENSE](LICENSE)

## 📧 تماس

- **نویسنده:** mahdihadari59-lgtm
- **ایمیل:** mahdihadari59@gmail.com
- **GitHub:** [@mahdihadari59-lgtm](https://github.com/mahdihadari59-lgtm)
- **Issues:** [گزارش مشکل](https://github.com/mahdihadari59-lgtm/hermezgan-intelligent/issues)

## 🎯 راه‌پیمایی آینده

- [ ] پوشش تست 85%+
- [ ] اپلیکیشن موبایل کامل (React Native)
- [ ] داشبورد مدیریتی
- [ ] Monitoring و Logging سطح تولید
- [ ] پشتیبانی از چند زبان اضافی

---

**ساخته‌شده با ❤️ برای استان هرمزگان**
