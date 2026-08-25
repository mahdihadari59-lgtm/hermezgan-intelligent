هرمزگان هوشمند (Hermezgan Intelligent / HDP)
سیستم دانش‌گراف هوشمند شهر بندرعباس — پلتفرم هوشمند شهری برای استان هرمزگان، شامل موتور جستجوی دانش، گراف دانش، سیستم مسیریابی و ترافیک، تشخیص گویش بندری، و دستیار هوش مصنوعی مکالمه‌ای.
⚙️ ویژگی‌های اصلی
Copilot Gateway — پردازش هوشمند پیام با تشخیص نیت (Intent Detection) و جستجو در ۱۰۵+ جدول پایگاه‌داده (بیش از ۵۶۰ هزار رکورد)
موتور دانش‌گراف — جستجوی ترکیبی (Knowledge + Graph + Vector) با پشتیبانی از FTS5
موتور بندری (Bandari Engine) — سرویس مستقل Node.js برای تشخیص لهجه، ترجمه، و پردازش زبانی گویش بندری (۹ گویش هرمزگانی)
تشخیص گفتار (Voice/STT) — تبدیل گفتار به متن آفلاین با Vosk، ترکیب‌شده با پردازش گویش بندری
دستیار هوش مصنوعی — یکپارچه با Gemini API برای پاسخ‌گویی مکالمه‌ای
سیستم مسیریابی و ترافیک — اطلاعات جاده‌ها، نقاط حادثه‌خیز، دوربین‌ها، و وضعیت ترافیک زنده
گردشگری و POI — جستجوی جاذبه‌های گردشگری، غذا، هتل، و نقاط مورد علاقه
TTS — تبدیل متن به گفتار با ElevenLabs
🏗️ معماری و پشته‌ی فناوری
بک‌اند: Python (FastAPI) + Node.js
پایگاه‌داده: SQLite (معماری چند-دیتابیسی: core, graph, knowledge, geo, media, events, search, vector)
فرانت‌اند: React (Vite) + Zustand
محیط اجرا: Termux (Android/aarch64) — offline-first، بدون وابستگی اجباری به سرویس‌های ابری
هوش مصنوعی: Google Gemini API (مدل: gemini-flash-latest)
تشخیص گفتار: Vosk (آفلاین)
تبدیل متن به گفتار: ElevenLabs API
📂 ساختار پروژه
Code
🚀 نصب و راه‌اندازی
نصب وابستگی‌های بک‌اند
Bash
تنظیم متغیرهای محیطی
یک فایل .env در مسیر backend/ بسازید:
Env
⚠️ هرگز کلیدهای API را در چت یا کامیت‌های گیت به اشتراک نگذارید. .env باید در .gitignore باشد.
نصب موتور بندری (اختیاری، برای پردازش گویش)
Bash
نصب Vosk برای تشخیص گفتار (اختیاری)
Bash
اجرای سرور
Bash
سرور روی http://localhost:8001 بالا می‌آید. مستندات تعاملی API در /docs قابل مشاهده است.
📡 اندپوینت‌های کلیدی
مسیر
توضیح
GET /api/v1/health/
بررسی سلامت سرویس
GET /api/v1/traffic/
وضعیت ترافیک
POST /api/v1/copilot/message
پردازش پیام از طریق Copilot Gateway
GET /api/v1/copilot/health
سلامت دیتابیس Copilot
POST /api/v1/ai/chat
چت با دستیار Gemini
GET /api/v1/ai/status
وضعیت سرویس Gemini
GET /api/v1/tts/status
وضعیت سرویس TTS
POST /api/v1/bandari-voice/transcribe
تبدیل گفتار به متن (Vosk)
POST /api/v1/bandari-voice/transcribe-and-process
گفتار → متن → تشخیص لهجه → ترجمه
GET /api/v1/bandari-voice/status
وضعیت سرویس گفتار بندری
🐞 عیب‌یابی رایج
خطای ModuleNotFoundError: No module named 'app'
از مسیر backend/ (نه backend/app/) دستور uvicorn را اجرا کنید.
خطای SyntaxError در ابتدای یک فایل
معمولاً به‌خاطر خط جداکننده‌ی ناقص (بدون #) در ابتدای فایل است؛ خط اول را بررسی/حذف کنید.
وجود نشانه‌های <<<<<<<، =======، >>>>>>> در کد
نشانه‌ی تعارض حل‌نشده‌ی git stash است. با دستور زیر فایل‌های آلوده را پیدا کنید:
Bash
خطای مدل Gemini (models/gemini-1.5-flash is not found)
مدل‌های قدیمی Gemini به‌مرور توسط Google از رده خارج می‌شوند. لیست مدل‌های فعال کلید خود را با این دستور بررسی کنید:
Bash
و در app/api/v1/gemini.py نام مدل را به‌روزرسانی کنید (پیشنهاد: از alias همیشه‌به‌روز gemini-flash-latest استفاده کنید).
ماژولی با وجود فایل، "یافت نشد" است
مسیر واقعی فایل را با مسیر تعریف‌شده در _MODULE_MAP داخل app/api/v1/routers.py مقایسه کنید.
خطای npm ci روی lock file ناسازگار
اگر package.json تغییر کرده ولی package-lock.json sync نشده، دستور زیر را بزنید و lock file جدید را کامیت کنید:
Bash
📌 وضعیت فعلی پروژه
✅ Copilot Gateway، health، traffic، tts، gemini، bandari-voice: فعال و تست‌شده
⚠️ pois.py: غیرفعال (وابستگی database_service.py مفقود شده) — قابلیت جستجوی POI از طریق Copilot Gateway در دسترس است
🔄 فرانت‌اند در حال مهاجرت از CRA/Redux به Vite/React/Zustand
📄 لایسنس
MIT
