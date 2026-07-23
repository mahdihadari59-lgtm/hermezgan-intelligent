# Bandari Engine v4.2

موتور پردازش و ترجمه گویش بندری — معماری ۸ لایه‌ای + دیکشنری ۹-گویشی.

## نصب و اجرا

```bash
npm install
npm start
```

پیکربندی LLM

فایل .env را تنظیم کنید:

```env
BANDARI_LLM_ENABLED=1
LLM_API_URL=http://127.0.0.1:8080/v1/chat/completions
LLM_MODEL=Qwen2.5-1.5B-Instruct-Q4_K_M
```

API

Endpoint Method توضیح
/api/translate POST ترجمه متن
/api/detect POST تشخیص گویش
/api/multilingual/translate POST ترجمه بین گویش‌ها
/api/learn POST یادگیری واژه جدید
/api/stats GET آمار
/api/health GET وضعیت سلامت

تست

```bash
npm run test:llm
```

