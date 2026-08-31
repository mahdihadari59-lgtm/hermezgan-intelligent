# Release notes — v2.0.0

## HDP Local RAG v2.0.0 — Initial stable release

این نسخه سرویس RAG محلی هرمزگان را به‌صورت پایدار منتشر می‌کند. شامل orchestrator، مجموعه‌ی experts برای حوزه‌های محلی، رابط FastAPI و وب ساده با Deno. مناسب برای اجرا روی Termux و سرورهای محلی.

### موارد برجسته
- پاسخ‌دهی هوشمند با ترکیب جستجوی محلی و LLMها (قابل تنظیم برای Google Gemini / Ollama / Levels).
- جستجوی متنی سریع با FTS5 و نمایه‌سازی SQLite.
- نصب ساده با اسکریپت‌های ارائه‌شده.

### راهنمای ارتقا
- قبل از ارتقا بک‌آپ کامل DB بگیرید.
- در صورت استفاده از rebase: force-push می‌تواند تاریخچه شاخه را بازنویسی کند.

### فایل‌های اضافه شده/تغییرات کلیدی
- CHANGELOG.md
- PR_BODY.md
- src/core/orchestrator.py
- src/core/expert_selector.py
- src/core/query_planner.py
- src/experts/*
- src/knowledge/db_connector.py
- main.py, requirements.txt, README.md, deno.json, main.ts

