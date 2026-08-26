# 📝 تاریخچه تغییرات

## [2.2.0] - 2026-08-26

### ✨ اضافه شده
- 📖 مستندات جامع README با راهنمای کامل Termux
- 🏗️ توضیح معماری و پشته فناوری تفصیلی
- 📂 نمایش ساختار پروژه جامع
- 📡 فهرست کامل اندپوینت‌های API
- 🧪 راهنمای تست و اعتبارسنجی
- 🐛 راه‌حل 10+ مسئله رایج
- 🐳 راهنمای Docker Compose
- 🔐 بخش امنیت و بهترین‌های عملی
- 🎯 نقشه‌راه آینده پروژه

### ✅ بهبودها
- تمام routers (14 router) کار می‌کنند و تست شده‌اند
- سرور FastAPI پایدار و با reload خودکار
- Pydantic v2 integration کامل
- بکاپ و بازگردانی دیتابیس راحت‌تر

### ⚠�� شناخته‌شده
- ماژول `pois.py` موقتاً غیرفعال (وابستگی `database_service.py` مفقود)
  - راه‌حل: جستجوی POI از طریق Copilot Gateway در دسترس است

## [2.1.3] - 2026-08-06

### Added
- Full containerization with Docker
- CI/CD pipeline with GitHub Actions
- Complete documentation (ARCHITECTURE.md, INSTALL.md)
- Release tooling and scripts

### Changed
- Updated all services to use Docker
- Improved project structure
- Enhanced configuration management

### Fixed
- Various bug fixes
- Performance improvements

## [1.0.1] - 2026-08-03

### ✨ اضافه شده
- README: راهنمای راه‌اندازی با Docker و محلی
- هماهنگ‌سازی env: استفاده از DATABASE_URL
- پشتیبانی از sqlite:/// paths
- مدیریت فایل‌های بزرگ با Git LFS
- CI: workflow پایه برای pytest
- اطلاعات جامع بندرعباس (۴ منطقه، محله‌ها، امکانات)

## [1.0.0] - 2026-08-03

### ✨ اضافه شده
- سیستم احراز هویت JWT
- چت‌بات هوشمند با NLP
- نقشه تعاملی با Leaflet
- اطلس دوربین‌های نظارتی
- نقاط حادثه‌خیز
- داشبورد تحلیلی
- Docker Compose
- مستندات کامل API

### 🐛 رفع باگ
- رفع مشکل CORS
- رفع مشکل زمان پاسخ چت‌بات

### 🔧 تغییرات
- FastAPI 0.104
- React 18.2

## [0.9.0] - 2023-12-15

### ✨ اضافه شده
- نسخه اولیه Backend
- نسخه اولیه Frontend
- اتصال به PostgreSQL
- اتصال به Redis
