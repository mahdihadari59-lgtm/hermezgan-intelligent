# ⚠️ Legacy Generator — DO NOT RUN

## fix_hermezgan_v2.py

اسکریپت «Auto Fix Script v2» که در commit `45f1a8d` (Aug 25 2026)
ساخته شد و `backend/app/main.py` را از روی متغیر `NEW_MAIN_PY` بازنویسی می‌کند.

## چرا خطرناک است

| ویژگی | در generator | در main.py فعال |
|---|---|---|
| driver_assistant router | ❌ ندارد | ✅ دارد |
| voice router (جدا) | ❌ داخل try orchestrator | ✅ جدا |
| last touched | 45f1a8d (Aug 25) | 76fa463 (HEAD, v2.0.3) |

## نتیجه‌ی اجرای مجدد

- router `driver_assistant` از main.py حذف می‌شود
- باگ تودرتویی voice در try orchestrator برمی‌گردد
- تغییرات بعد از Aug 25 از دست می‌رود

## منبع حقیقت فعلی

`backend/app/main.py` — دستی نگهداری می‌شود، از generator ساخته نمی‌شود.
