# 🌊 هرمزگان هوشمند

سیستم دانش‌گراف هوشمند شهر بندرعباس

## 🚀 راه‌اندازی

```bash
# با Docker
docker-compose up -d

# یا بدون Docker
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

cd ../frontend
npm install
npm start
```

🌐 دسترسی‌ها

· Frontend: http://localhost:3000
· Backend: http://localhost:8000
· API Docs: http://localhost:8000/api/docs

🧪 تست

```bash
cd backend && pytest tests/ -v --cov=app
cd frontend && npm test -- --coverage
```

📁 ساختار

```
hermezgan-intelligent/
├── backend/          # FastAPI Backend
├── frontend/         # React Frontend
├── database/         # Migrations & Seeds
├── docs/             # Documentation
├── scripts/          # Utility Scripts
└── archive/          # Archived files
```

📝 مجوز

MIT License
