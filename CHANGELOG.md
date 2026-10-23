# Changelog

## [Unreleased]

### Added
- پیاده‌سازی HdpOrchestrator برای هدایت queryها بین intent routing، experts و RAG.
- مجموعه‌ی Experts: local, tourism, business, routing, traffic, auto, dialect, legal.
- اتصالات SQLite و جداول FTS (db_connector).
- API با FastAPI: endpoints /ask, /health, /stats.
- رابط وب ساده با Deno/Oak (main.ts).

### Changed
- ساختار پروژه سازماندهی شد تا هسته‌ی RAG و ابزارهای AI جدا شوند.
- هم‌راستایی نسخه‌های پروژه با سیاست Compatibility-safe Upgrade و نسخهٔ مرکزی `2.2.0`.

### Fixed
- (هیچ مورد مشهود فعلاً گزارش نشده — لطفاً تست‌های محلی را اجرا کنید.)

## [2.2.0] - 2026-10-23

### Safe Compatibility Upgrade
- هم‌راستایی نسخهٔ کلی پروژه به `2.2.0`.
- حفظ مسیرهای legacy و compatibility برای جلوگیری از آسیب به ماژول‌های موجود.
- نگه‌داشتن بخش‌های سالم و Archiving بخش‌های تکراری به‌جای حذف ناگهانی.
- استانداردسازی نسخه‌بندی بین پروژه ریشه، frontend و backend.
- آماده‌سازی مستندات آپگرید ایمن برای تیم و توسعه آینده.

## [2.0.0] - Unreleased
- انتشار پایدار اولیه شامل همه‌ی قابلیت‌های بالا.
