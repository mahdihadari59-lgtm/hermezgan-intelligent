خلاصه

- تکمیل و یکپارچه‌سازی هسته‌ی سرویس: HdpOrchestrator و مسیرهای مربوطه (intent routing, expert selector, query planner).
- افزودن Experts (local, tourism, business, routing, traffic, auto, dialect, legal) و اتصال به DB محلی از طریق src/knowledge/db_connector.py.
- آماده‌سازی API (FastAPI) در main.py و رابط ساده‌ی Deno frontend (main.ts).
- فایل‌های کمکی برای نصب و اجرا روی Termux و دسکتاپ (scripts / setup.sh / deno.json).

تغییرات کلیدی

- src/core/orchestrator.py — orchestrator اصلی و مدیریت مسیر تولید پاسخ‌ها
- src/core/expert_selector.py — انتخاب متخصصین براساس intent
- src/core/query_planner.py — تولید plan برای queryها
- src/experts/* — مجموعه‌ی متخصص‌ها برای حوزه‌های مختلف
- src/knowledge/db_connector.py — connector SQLite و جداول FTS
- main.py, requirements.txt, README.md, setup.sh, main.ts, deno.json

روش تست محلی

1. اطمینان از وجود DB: قرار دادن فایل دیتابیس در db/hdp_master.db یا تنظیم متغیر محیطی مطابق README و src/utils/config.py
2. نصب وابستگی‌ها:
   - روی لینوکس/termux: ./scripts/install.sh (یا pip install -r requirements.txt)
3. اجرا:
   - Python API: python main.py  (یا uvicorn main:app --host 0.0.0.0 --port 8000)
   - Frontend (Deno): deno task start
4. بررسی endpoint ها:
   - GET /health
   - POST /ask با نمونه سؤال فارسی

نکات انتشار

- نسخه پیشنهادی: v2.0.0 (هماهنگ با app.version در main.py)
- قبل از مرج اطمینان پیدا کنید که CI (در صورت وجود) پاس شده و دیتابیس نمونه برای تست صحت دارد.

موارد شناخته‌شده / محدودیت‌ها

- اگر از rebase استفاده شود، push شاخه به صورت --force لازم است.
- بعضی queryها وابسته به FTS5 هستند؛ اطمینان حاصل کنید SQLite شما از FTS5 پشتیبانی می‌کند.
- اگر PR از fork ارسال شود، برخی از check logs ممکن است برای upstream قابل‌دسترسی نباشد.
