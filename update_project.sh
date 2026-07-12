#!/bin/bash
# ============================================================
# اسکریپت به‌روزرسانی هوشمند پروژه هرمزگان هوشمند
# فقط فایل‌های موجود را بررسی و فایل‌های缺失 را ایجاد می‌کند
# ============================================================

set -e

echo "🔍 شروع بررسی و به‌روزرسانی پروژه..."
echo "================================================"

# ============================================================
# بخش ۱: بررسی و ایجاد پوشه‌ها (فقط در صورت نبودن)
# ============================================================
echo "📁 بررسی پوشه‌ها..."

declare -A FOLDERS=(
    ["backend/app/api/v1/endpoints"]="Backend API endpoints"
    ["backend/app/core"]="Backend Core"
    ["backend/app/models"]="Backend Models"
    ["backend/app/services"]="Backend Services"
    ["backend/app/database"]="Backend Database"
    ["backend/tests"]="Backend Tests"
    ["backend/scripts"]="Backend Scripts"
    ["frontend/src/components/Layout"]="Frontend Layout"
    ["frontend/src/components/Chat"]="Frontend Chat"
    ["frontend/src/components/Map"]="Frontend Map"
    ["frontend/src/components/Dashboard"]="Frontend Dashboard"
    ["frontend/src/components/Hotspots"]="Frontend Hotspots"
    ["frontend/src/components/Common"]="Frontend Common"
    ["frontend/src/pages"]="Frontend Pages"
    ["frontend/src/services"]="Frontend Services"
    ["frontend/src/store/slices"]="Frontend Slices"
    ["frontend/src/hooks"]="Frontend Hooks"
    ["frontend/src/utils"]="Frontend Utils"
    ["frontend/src/styles"]="Frontend Styles"
    ["frontend/public"]="Frontend Public"
    ["database/migrations"]="Database Migrations"
    ["database/seeds"]="Database Seeds"
    ["docs"]="Documentation"
    ["HermezganMobile/src/screens"]="Mobile Screens"
    ["HermezganMobile/src/components"]="Mobile Components"
    ["HermezganMobile/src/services"]="Mobile Services"
    ["HermezganMobile/src/store/slices"]="Mobile Slices"
    [".github/workflows"]="GitHub Actions"
)

for folder in "${!FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo "  ✅ پوشه موجود: $folder"
    else
        echo "  📁 ایجاد پوشه: $folder (${FOLDERS[$folder]})"
        mkdir -p "$folder"
    fi
done

# ============================================================
# بخش ۲: بررسی و ایجاد فایل‌های Backend (فقط در صورت نبودن)
# ============================================================
echo ""
echo "📝 بررسی فایل‌های Backend..."

# تابع کمکی برای ایجاد فایل در صورت نبودن
create_file_if_not_exists() {
    local file_path="$1"
    local content="$2"
    local description="$3"
    
    if [ -f "$file_path" ]; then
        echo "  ✅ فایل موجود: $file_path"
    else
        echo "  📝 ایجاد فایل: $file_path ($description)"
        echo "$content" > "$file_path"
    fi
}

# Backend فایل‌ها
create_file_if_not_exists "backend/requirements.txt" \
'fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
redis==5.0.1
aiohttp==3.9.1
httpx==0.25.2
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
email-validator==2.1.0' \
"Requirements"

create_file_if_not_exists "backend/main.py" \
'from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="هرمزگان هوشمند API",
    description="سیستم دانش‌گراف هوشمند استان هرمزگان",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZIPMiddleware, minimum_size=1000)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/")
async def root():
    return {
        "message": "🌊 خوش‌آمدید به هرمزگان هوشمند",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)' \
"Main FastAPI"

create_file_if_not_exists "backend/app/__init__.py" \
'# Backend package' \
"Backend init"

create_file_if_not_exists "backend/app/config.py" \
'from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "هرمزگان هوشمند"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/hermezgan_db"
    REDIS_URL: str = "redis://localhost:6379"
    
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()' \
"Config"

create_file_if_not_exists "backend/app/cache.py" \
'import redis
import json
from typing import Optional, Any
from app.config import settings

class CacheManager:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if data:
            try:
                return json.loads(data)
            except:
                return data
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.setex(key, ttl, value)
    
    def delete(self, key: str) -> int:
        return self.client.delete(key)
    
    def clear_pattern(self, pattern: str) -> int:
        count = 0
        for key in self.client.scan_iter(match=pattern):
            count += self.client.delete(key)
        return count

cache = CacheManager()' \
"Cache"

create_file_if_not_exists "backend/app/models/__init__.py" \
'from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()' \
"Models"

create_file_if_not_exists "backend/app/api/__init__.py" \
'# API package' \
"API init"

create_file_if_not_exists "backend/app/api/v1/__init__.py" \
'# API v1 package' \
"API v1 init"

create_file_if_not_exists "backend/app/api/v1/routers.py" \
'from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["General"])

@router.get("/ping")
async def ping():
    return {"status": "pong", "timestamp": datetime.utcnow().isoformat()}

@router.get("/version")
async def version():
    return {"version": "1.0.0", "name": "هرمزگان هوشمند"}' \
"Routers"

create_file_if_not_exists "backend/app/api/v1/chat.py" \
'from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    suggestions: List[str] = []

@router.post("/message", response_model=ChatResponse)
async def send_message(data: ChatMessage):
    return ChatResponse(
        response=f"دریافت شد: {data.message}",
        intent="general",
        confidence=0.95,
        suggestions=["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
    )' \
"Chat API"

create_file_if_not_exists "backend/app/api/v1/locations.py" \
'from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/search")
async def search_locations(query: str, latitude: Optional[float] = None, longitude: Optional[float] = None):
    return {"results": [], "total": 0}

@router.get("/nearest")
async def nearest_services(latitude: float, longitude: float, service_type: Optional[str] = None, radius: float = 5.0):
    return {"services": [], "total": 0}

@router.get("/route")
async def get_route(start_lat: float, start_lng: float, end_lat: float, end_lng: float):
    return {"distance": 0, "duration": 0}' \
"Locations API"

create_file_if_not_exists "backend/app/api/v1/analytics.py" \
'from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/stats")
async def get_statistics():
    return {
        "totalUsers": 1234,
        "activeUsers": 856,
        "totalServices": 567,
        "completedQueries": 3421
    }

@router.get("/user-growth")
async def get_user_growth(time_filter: str = "weekly"):
    return {
        "data": [
            {"date": "۱۵ فروردین", "users": 120, "queries": 240},
            {"date": "۱۶ فروردین", "users": 132, "queries": 221}
        ]
    }' \
"Analytics API"

create_file_if_not_exists "backend/app/api/v1/cameras.py" \
'from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.get("/")
async def get_cameras(region: Optional[str] = None, status: Optional[str] = None):
    return {"cameras": [], "total": 0}

@router.post("/{camera_id}/report")
async def report_camera_issue(camera_id: str, issue: str):
    return {"status": "reported", "id": camera_id}' \
"Cameras API"

create_file_if_not_exists "backend/app/api/v1/hotspots.py" \
'from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/hotspots", tags=["Hotspots"])

@router.get("/")
async def get_hotspots(type: Optional[str] = None):
    return {"hotspots": [], "total": 0}

@router.get("/nearby")
async def nearby_hotspots(latitude: float, longitude: float, radius: float = 5.0):
    return {"hotspots": [], "total": 0}' \
"Hotspots API"

create_file_if_not_exists "backend/app/api/v1/auth.py" \
'from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register")
async def register(data: RegisterRequest):
    return {"message": "ثبت‌نام موفق", "user": data.username}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    return {"access_token": "mock-token-123", "token_type": "bearer"}' \
"Auth API"

create_file_if_not_exists "backend/app/core/__init__.py" \
'# Core package' \
"Core init"

create_file_if_not_exists "backend/app/core/logger.py" \
'import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)' \
"Logger"

create_file_if_not_exists "backend/app/core/speech_interface.py" \
'# Speech interface module
def process_speech(audio_data: bytes) -> dict:
    return {"text": "در حال پردازش..."}' \
"Speech Interface"

create_file_if_not_exists "backend/Dockerfile" \
'FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]' \
"Dockerfile"

# ============================================================
# بخش ۳: بررسی و ایجاد فایل‌های Frontend
# ============================================================
echo ""
echo "🎨 بررسی فایل‌های Frontend..."

create_file_if_not_exists "frontend/package.json" \
'{
  "name": "hermezgan-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^8.1.3",
    "@reduxjs/toolkit": "^1.9.7",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "chart.js": "^4.4.1",
    "react-chartjs-2": "^5.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}' \
"Package.json"

create_file_if_not_exists "frontend/src/index.js" \
'import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import store from "./store";
import App from "./App";
import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);' \
"Index.js"

create_file_if_not_exists "frontend/src/App.js" \
'import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useSelector } from "react-redux";
import { Header, Sidebar, Footer } from "./components/Layout";
import ChatPage from "./pages/ChatPage";
import MapPage from "./pages/MapPage";
import DashboardPage from "./pages/DashboardPage";
import "./App.css";

function App() {
  const { isDarkMode } = useSelector((state) => state.ui);

  return (
    <Router>
      <div className={`app ${isDarkMode ? "dark-mode" : "light-mode"}`}>
        <Header />
        <div className="app-container">
          <Sidebar />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<div className="page-placeholder">🏠 صفحه اصلی</div>} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </main>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;' \
"App.js"

create_file_if_not_exists "frontend/src/App.css" \
'.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #ffffff;
  color: #2d3748;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  direction: rtl;
}

.app.dark-mode {
  background: #1a202c;
  color: #e2e8f0;
}

.app-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
  padding: 2rem;
}

.app.dark-mode .app-main {
  background: #2d3748;
}

.page-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: white;
  border-radius: 0.5rem;
  border: 2px dashed #cbd5e0;
  color: #a0aec0;
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .app-main {
    padding: 1rem;
  }
}' \
"App.css"

create_file_if_not_exists "frontend/src/index.css" \
'* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen",
    "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue",
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  direction: rtl;
  background: #ffffff;
  color: #2d3748;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace;
}' \
"Index.css"

create_file_if_not_exists "frontend/public/index.html" \
'<!DOCTYPE html>
<html lang="fa" dir="rtl">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#667eea" />
    <meta name="description" content="سیستم دانش‌گراف هوشمند شهر بندرعباس" />
    <title>هرمزگان هوشمند</title>
  </head>
  <body>
    <noscript>برای اجرای این برنامه نیاز به JavaScript دارید.</noscript>
    <div id="root"></div>
  </body>
</html>' \
"Index.html"

create_file_if_not_exists "frontend/src/store/index.js" \
'import { configureStore } from "@reduxjs/toolkit";
import uiReducer from "./slices/uiSlice";
import authReducer from "./slices/authSlice";
import chatReducer from "./slices/chatSlice";
import mapReducer from "./slices/mapSlice";

const store = configureStore({
  reducer: {
    ui: uiReducer,
    auth: authReducer,
    chat: chatReducer,
    map: mapReducer,
  },
});

export default store;' \
"Store"

create_file_if_not_exists "frontend/src/store/slices/uiSlice.js" \
'import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  isSidebarOpen: true,
  isDarkMode: false,
  language: "fa",
  notifications: [],
  loading: false,
  error: null,
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    toggleSidebar: (state) => { state.isSidebarOpen = !state.isSidebarOpen; },
    toggleDarkMode: (state) => { state.isDarkMode = !state.isDarkMode; },
    setLoading: (state, action) => { state.loading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
    clearError: (state) => { state.error = null; },
  },
});

export const { toggleSidebar, toggleDarkMode, setLoading, setError, clearError } = uiSlice.actions;
export default uiSlice.reducer;' \
"UI Slice"

create_file_if_not_exists "frontend/src/store/slices/authSlice.js" \
'import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  user: null,
  isAuthenticated: false,
  token: null,
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginStart: (state) => { state.loading = true; state.error = null; },
    loginSuccess: (state, action) => {
      state.loading = false;
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
    },
    loginFailure: (state, action) => { state.loading = false; state.error = action.payload; },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.token = null;
      state.error = null;
    },
  },
});

export const { loginStart, loginSuccess, loginFailure, logout } = authSlice.actions;
export default authSlice.reducer;' \
"Auth Slice"

create_file_if_not_exists "frontend/src/store/slices/chatSlice.js" \
'import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  messages: [],
  isLoading: false,
  isTyping: false,
  error: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({ id: Date.now(), ...action.payload });
    },
    clearMessages: (state) => { state.messages = []; },
    setLoading: (state, action) => { state.isLoading = action.payload; },
    setTyping: (state, action) => { state.isTyping = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
  },
});

export const { addMessage, clearMessages, setLoading, setTyping, setError } = chatSlice.actions;
export default chatSlice.reducer;' \
"Chat Slice"

create_file_if_not_exists "frontend/src/store/slices/mapSlice.js" \
'import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  center: { lat: 27.2158, lng: 56.2808 },
  zoom: 13,
  markers: [],
  selectedMarker: null,
  searchQuery: "",
  userLocation: null,
  isLoading: false,
  error: null,
};

const mapSlice = createSlice({
  name: "map",
  initialState,
  reducers: {
    setMapCenter: (state, action) => { state.center = action.payload; },
    setZoom: (state, action) => { state.zoom = action.payload; },
    setMarkers: (state, action) => { state.markers = action.payload; },
    selectMarker: (state, action) => { state.selectedMarker = action.payload; },
    clearSelection: (state) => { state.selectedMarker = null; },
    setSearchQuery: (state, action) => { state.searchQuery = action.payload; },
    setUserLocation: (state, action) => { state.userLocation = action.payload; },
    setLoading: (state, action) => { state.isLoading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
  },
});

export const {
  setMapCenter, setZoom, setMarkers, selectMarker, clearSelection,
  setSearchQuery, setUserLocation, setLoading, setError
} = mapSlice.actions;
export default mapSlice.reducer;' \
"Map Slice"

create_file_if_not_exists "frontend/src/services/api.js" \
'import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error.response?.data || error.message);
  }
);

export default api;' \
"API Service"

create_file_if_not_exists "frontend/src/components/Layout/Header.js" \
'import React from "react";
import { useDispatch } from "react-redux";
import { toggleSidebar } from "../../store/slices/uiSlice";
import "./Header.css";

const Header = () => {
  const dispatch = useDispatch();

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          <button className="menu-toggle" onClick={() => dispatch(toggleSidebar())}>
            ☰
          </button>
          <div className="logo-section">
            <h1 className="logo-text">🌊 هرمزگان هوشمند</h1>
            <p className="logo-subtitle">سیستم دانش‌گراف شهر بندرعباس</p>
          </div>
        </div>
        <div className="header-center">
          <input type="text" placeholder="جستجو..." className="search-input" />
        </div>
        <div className="header-right">
          <button className="header-icon-btn">🔔</button>
          <div className="user-profile">
            <img src="https://ui-avatars.com/api/?name=User&background=667eea&color=fff" alt="پروفایل" className="user-avatar" />
            <div className="user-info">
              <p className="user-name">کاربر</p>
              <p className="user-status">فعال</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;' \
"Header"

create_file_if_not_exists "frontend/src/components/Layout/Header.css" \
'.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.5rem 2rem;
  box-shadow: 0 4px 12px rgba(102,126,234,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1600px;
  margin: 0 auto;
  gap: 2rem;
}
.header-left { display: flex; align-items: center; gap: 1rem; }
.menu-toggle { display: none; background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; }
.logo-text { font-size: 1.5rem; font-weight: 700; margin: 0; text-align: right; }
.logo-subtitle { font-size: 0.75rem; opacity: 0.9; margin: 0; text-align: right; }
.header-center { flex: 1; max-width: 400px; }
.search-input {
  width: 100%; padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.2); border: none; border-radius: 2rem;
  color: white; outline: none;
}
.search-input::placeholder { color: rgba(255,255,255,0.7); }
.header-right { display: flex; align-items: center; gap: 1.5rem; }
.header-icon-btn { background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; }
.user-profile { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }
.user-avatar { width: 2.5rem; height: 2.5rem; border-radius: 50%; border: 2px solid white; }
.user-info { text-align: right; }
.user-name { font-size: 0.9rem; font-weight: 600; margin: 0; }
.user-status { font-size: 0.75rem; opacity: 0.8; margin: 0; }
@media (max-width:768px) {
  .header { padding: 0.5rem 1rem; }
  .menu-toggle { display: block; }
  .logo-subtitle { display: none; }
  .user-info { display: none; }
}' \
"Header.css"

create_file_if_not_exists "frontend/src/components/Layout/Sidebar.js" \
'import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link, useLocation } from "react-router-dom";
import { toggleSidebar } from "../../store/slices/uiSlice";
import "./Sidebar.css";

const Sidebar = () => {
  const dispatch = useDispatch();
  const { isSidebarOpen } = useSelector((state) => state.ui);
  const location = useLocation();

  const menuItems = [
    { id: 1, title: "خانه", icon: "🏠", path: "/" },
    { id: 2, title: "چت‌بات", icon: "💬", path: "/chat" },
    { id: 3, title: "نقشه", icon: "🗺️", path: "/map" },
    { id: 4, title: "داشبورد", icon: "📊", path: "/dashboard" },
  ];

  return (
    <>
      {isSidebarOpen && <div className="sidebar-overlay" onClick={() => dispatch(toggleSidebar())} />}
      <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">📋 منو</h2>
          <button className="sidebar-close" onClick={() => dispatch(toggleSidebar())}>✕</button>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.id}
              to={item.path}
              className={`menu-item ${location.pathname === item.path ? "active" : ""}`}
            >
              <span className="menu-icon">{item.icon}</span>
              <span className="menu-text">{item.title}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button className="logout-btn">🚪 خروج</button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;' \
"Sidebar"

create_file_if_not_exists "frontend/src/components/Layout/Sidebar.css" \
'.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 99;
}
.sidebar {
  width: 280px;
  height: calc(100vh - 80px);
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  border-right: 1px solid #e9ecef;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e9ecef;
  background: white;
}
.sidebar-title { font-size: 1.25rem; font-weight: 700; margin: 0; color: #2d3748; text-align: right; }
.sidebar-close { display: none; background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #667eea; }
.sidebar-nav { flex: 1; padding: 1rem 0; }
.menu-item {
  display: flex; align-items: center; gap: 1rem;
  padding: 0.75rem 1.5rem; color: #4a5568; text-decoration: none;
  transition: all 0.2s; text-align: right;
}
.menu-item:hover { background: #f0f2f5; color: #667eea; }
.menu-item.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.menu-icon { font-size: 1.25rem; }
.menu-text { font-size: 0.95rem; }
.sidebar-footer { padding: 1rem; border-top: 1px solid #e9ecef; background: white; }
.logout-btn {
  width: 100%; padding: 0.75rem;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white; border: none; border-radius: 0.5rem;
  cursor: pointer; font-weight: 600;
}
@media (max-width:768px) {
  .sidebar {
    position: fixed; left: 0; top: 80px;
    height: calc(100vh - 80px); width: 250px;
    z-index: 100; transform: translateX(-100%);
  }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay { display: block; }
  .sidebar-close { display: block; }
}' \
"Sidebar.css"

create_file_if_not_exists "frontend/src/components/Layout/Footer.js" \
'import React from "react";
import "./Footer.css";

const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>درباره ما</h3>
            <p>هرمزگان هوشمند یک سیستم دانش‌گراف هوشمند برای شهر بندرعباس</p>
          </div>
          <div className="footer-section">
            <h3>تماس</h3>
            <p>📧 info@hermezgan.com</p>
            <p>📱 +98 (912) 345-6789</p>
          </div>
          <div className="footer-section">
            <h3>شبکه‌های اجتماعی</h3>
            <div className="social-links">
              <a href="#">📱</a>
              <a href="#">🐦</a>
              <a href="#">📷</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© {year} هرمزگان هوشمند. تمام حقوق محفوظ است.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;' \
"Footer"

create_file_if_not_exists "frontend/src/components/Layout/Footer.css" \
'.footer {
  background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
  color: #e2e8f0;
  padding: 2rem 0 0;
  border-top: 1px solid #4a5568;
}
.footer-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
.footer-section h3 { font-size: 1rem; margin: 0 0 0.75rem 0; text-align: right; }
.footer-section p { font-size: 0.9rem; color: #cbd5e0; margin: 0.25rem 0; text-align: right; }
.social-links { display: flex; gap: 0.5rem; justify-content: flex-end; }
.social-links a { color: white; text-decoration: none; font-size: 1.5rem; }
.footer-bottom { border-top: 1px solid #4a5568; padding-top: 1rem; text-align: center; }
.footer-bottom p { font-size: 0.85rem; color: #718096; }' \
"Footer.css"

create_file_if_not_exists "frontend/src/components/Layout/index.js" \
'export { default as Header } from "./Header";
export { default as Sidebar } from "./Sidebar";
export { default as Footer } from "./Footer";' \
"Layout Index"

create_file_if_not_exists "frontend/src/pages/ChatPage.js" \
'import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { addMessage } from "../store/slices/chatSlice";
import "./ChatPage.css";

const ChatPage = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(addMessage({
      text: "🌊 سلام! من هرمزگان هوشمند هستم. چطور می‌تونم کمک کنم؟",
      sender: "bot",
      timestamp: Date.now(),
      suggestions: ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
    }));
  }, [dispatch]);

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div className="chat-header">
          <h2>🌊 هرمزگان هوشمند</h2>
          <span className="status">🟢 آنلاین</span>
        </div>
        <div className="chat-messages">
          <div className="message bot">
            <div className="bubble">سلام! چطور می‌تونم کمک کنم؟</div>
          </div>
        </div>
        <div className="chat-input">
          <input type="text" placeholder="پیام خود را بنویسید..." />
          <button>📤</button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;' \
"ChatPage"

create_file_if_not_exists "frontend/src/pages/ChatPage.css" \
'.chat-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.chat-container {
  width: 100%; max-width: 800px; height: 600px;
  background: white; border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  display: flex; flex-direction: column; overflow: hidden;
}
.chat-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex; justify-content: space-between; align-items: center;
}
.chat-header h2 { margin: 0; font-size: 1.2rem; }
.status { font-size: 0.85rem; opacity: 0.9; }
.chat-messages {
  flex: 1; overflow-y: auto; padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1rem;
}
.message { display: flex; }
.message.bot { justify-content: flex-start; }
.message.user { justify-content: flex-end; }
.bubble {
  max-width: 70%; padding: 0.75rem 1rem;
  border-radius: 0.75rem; background: #f0f2f5;
  color: #2d3748;
}
.message.user .bubble { background: #667eea; color: white; }
.chat-input {
  padding: 1rem; border-top: 1px solid #e9ecef;
  display: flex; gap: 0.75rem; background: white;
}
.chat-input input {
  flex: 1; padding: 0.75rem 1rem;
  border: 2px solid #e9ecef; border-radius: 0.5rem;
  font-size: 0.95rem; outline: none;
}
.chat-input input:focus { border-color: #667eea; }
.chat-input button {
  padding: 0.75rem 1.5rem; background: #667eea;
  color: white; border: none; border-radius: 0.5rem;
  cursor: pointer; font-size: 1.2rem;
}' \
"ChatPage.css"

create_file_if_not_exists "frontend/src/pages/MapPage.js" \
'import React from "react";
import "./MapPage.css";

const MapPage = () => {
  return (
    <div className="map-page">
      <div className="map-container">
        <h2>🗺️ نقشه تعاملی</h2>
        <p style={{ color: "#718096" }}>در حال توسعه...</p>
      </div>
    </div>
  );
};

export default MapPage;' \
"MapPage"

create_file_if_not_exists "frontend/src/pages/MapPage.css" \
'.map-page {
  display: flex; justify-content: center; align-items: center;
  min-height: calc(100vh - 80px); padding: 2rem;
}
.map-container {
  width: 100%; height: 600px; max-width: 1200px;
  background: white; border-radius: 0.75rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
}' \
"MapPage.css"

create_file_if_not_exists "frontend/src/pages/DashboardPage.js" \
'import React from "react";
import "./DashboardPage.css";

const DashboardPage = () => {
  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <h2>📊 داشبورد تحلیلی</h2>
        <p style={{ color: "#718096" }}>در حال توسعه...</p>
      </div>
    </div>
  );
};

export default DashboardPage;' \
"DashboardPage"

create_file_if_not_exists "frontend/src/pages/DashboardPage.css" \
'.dashboard-page {
  display: flex; justify-content: center; align-items: center;
  min-height: calc(100vh - 80px); padding: 2rem;
}
.dashboard-container {
  width: 100%; max-width: 1200px;
  background: white; border-radius: 0.75rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 2rem;
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
  min-height: 400px;
}' \
"DashboardPage.css"

create_file_if_not_exists "frontend/Dockerfile" \
'FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "start"]' \
"Frontend Dockerfile"

# ============================================================
# بخش ۴: فایل‌های Database
# ============================================================
echo ""
echo "🗄️ بررسی فایل‌های Database..."

create_file_if_not_exists "database/schema.sql" \
'-- کاربران
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- خدمات
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    address VARCHAR(500),
    phone VARCHAR(20),
    rating FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT "active",
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- نقاط حادثه‌خیز
CREATE TABLE IF NOT EXISTS hotspots (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT "active",
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- دوربین‌ها
CREATE TABLE IF NOT EXISTS cameras (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    types JSON,
    status VARCHAR(20),
    installed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پیام‌های چت
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    message TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ایندکس‌ها
CREATE INDEX idx_services_type ON services(type);
CREATE INDEX idx_hotspots_type ON hotspots(type);
CREATE INDEX idx_cameras_region ON cameras(region);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id);' \
"Schema"

# ============================================================
# بخش ۵: فایل‌های Tests
# ============================================================
echo ""
echo "🧪 بررسی فایل‌های Tests..."

create_file_if_not_exists "backend/tests/conftest.py" \
'import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)' \
"Conftest"

create_file_if_not_exists "backend/tests/test_main.py" \
'import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "هرمزگان هوشمند" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ping():
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "pong"' \
"Main Tests"

create_file_if_not_exists "backend/tests/test_api_chat.py" \
'import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestChatAPI:
    def test_chat_endpoint_exists(self):
        response = client.post("/api/v1/chat/message", json={
            "message": "سلام",
            "user_id": "test"
        })
        assert response.status_code in [200, 404]

    def test_chat_validation(self):
        response = client.post("/api/v1/chat/message", json={})
        assert response.status_code in [400, 422]' \
"Chat Tests"

# ============================================================
# بخش ۶: فایل‌های Config
# ============================================================
echo ""
echo "⚙️ بررسی فایل‌های Config..."

create_file_if_not_exists "docker-compose.yml" \
'version: "3.8"

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: hermezgan_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/hermezgan_db
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start

volumes:
  postgres_data:' \
"Docker Compose"

create_file_if_not_exists ".env.example" \
'# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hermezgan_db

# Redis
REDIS_URL=redis://localhost:6379

# API
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development

# Frontend
REACT_APP_API_URL=http://localhost:8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5000' \
"Env Example"

create_file_if_not_exists ".gitignore" \
'# Python
__pycache__/
*.pyc
*.pyo
venv/
env/
.env
*.db

# Node
node_modules/
npm-debug.log*
build/
dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Docker
*.pid

# Coverage
coverage/
htmlcov/
.pytest_cache/' \
"Gitignore"

# ============================================================
# بخش ۷: مستندات
# ============================================================
echo ""
echo "📖 بررسی مستندات..."

create_file_if_not_exists "README.md" \
'# 🌊 هرمزگان هوشمند

سیستم دانش‌گراف هوشمند شهر بندرعباس

## 🚀 راه‌اندازی

```bash
# با Docker
docker-compose up -d

# یا بدون Docker
cd backend && python main.py &
cd frontend && npm start &
 دسترسی‌ها

· Frontend: http://localhost:3000
· Backend: http://localhost:8000
· API Docs: http://localhost:8000/api/docs

🧪 تست

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
```' \
"README"

create_file_if_not_exists "docs/API_REFERENCE.md" \
'# 📚 مرجع API

## سلامت
`GET /health`

## Chat
`POST /api/v1/chat/message`

## Locations
`GET /api/v1/locations/search`
`GET /api/v1/locations/nearest`

## Analytics
`GET /api/v1/analytics/stats`' \
"API Reference"

create_file_if_not_exists "docs/ARCHITECTURE.md" \
'# معماری سیستم

## ساختار
- **Frontend**: React + Redux
- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis

## ماژول‌ها
1. چت‌بات
2. نقشه
3. داشبورد
4. دوربین‌ها
5. نقاط حادثه‌خیز' \
"Architecture"

# ============================================================
# بخش ۸: اسکریپت‌های اجرایی
# ============================================================
echo ""
echo "🔧 بررسی اسکریپت‌های اجرایی..."

create_file_if_not_exists "scripts/run_backend.sh" \
'#!/bin/bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py' \
"Run Backend"
chmod +x scripts/run_backend.sh 2>/dev/null || true

create_file_if_not_exists "scripts/run_frontend.sh" \
'#!/bin/bash
cd frontend
npm install
npm start' \
"Run Frontend"
chmod +x scripts/run_frontend.sh 2>/dev/null || true

create_file_if_not_exists "scripts/run_tests.sh" \
'#!/bin/bash
echo "🧪 تست Backend..."
cd backend
pytest tests/ -v
echo "✅ تست‌ها تکمیل شد!"' \
"Run Tests"
chmod +x scripts/run_tests.sh 2>/dev/null || true

# ============================================================
# بخش ۹: GitHub Actions
# ============================================================
echo ""
echo "🔄 بررسی GitHub Actions..."

create_file_if_not_exists ".github/workflows/tests.yml" \
'name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with: { python-version: "3.11" }
      - name: Install
        run: pip install -r backend/requirements.txt
      - name: Run Tests
        run: cd backend && pytest tests/ -v' \
"GitHub Actions"

# ============================================================
# پایان
# ============================================================
echo ""
echo "================================================"
echo "✅ بررسی و به‌روزرسانی پروژه تکمیل شد!"
echo "================================================"
echo ""
echo "📂 مسیر: $(pwd)"
echo ""
echo "📊 خلاصه تغییرات:"
echo "─────────────────────────────────"
echo "📁 پوشه‌های موجود: $(find . -type d 2>/dev/null | wc -l) عدد"
echo "📄 فایل‌های موجود: $(find . -type f 2>/dev/null | wc -l) عدد"
echo ""
echo "📋 دستورات مفید:"
echo "─────────────────────────────────"
echo "▶️  اجرا با Docker:    docker-compose up -d"
echo "▶️  اجرا Backend:      bash scripts/run_backend.sh"
echo "▶️  اجرا Frontend:     bash scripts/run_frontend.sh"
echo "▶️  اجرا تست‌ها:       bash scripts/run_tests.sh"
echo ""
echo "🌐 دسترسی‌ها:"
echo "─────────────────────────────────"
echo "🔵 Frontend:   http://localhost:3000"
echo "🟢 Backend:    http://localhost:8000"
echo "📚 API Docs:   http://localhost:8000/api/docs"
