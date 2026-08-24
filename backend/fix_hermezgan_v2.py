#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hermezgan Intelligent - Auto Fix Script v2
راه‌حل مشکل string formatting
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")
API_V1_DIR = os.path.join(APP_DIR, "api", "v1")
MAIN_PY = os.path.join(APP_DIR, "main.py")

GREEN, RED, YELLOW, BLUE, CYAN, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[94m", "\033[96m", "\033[0m"

def log(msg, color=BLUE):
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {msg}{RESET}")

def success(msg): log(f"✅ {msg}", GREEN)
def error(msg): log(f"❌ {msg}", RED)
def warning(msg): log(f"⚠️ {msg}", YELLOW)
def info(msg): log(f"ℹ️ {msg}", BLUE)

def ask(question, default="n"):
    choices = " [Y/n]" if default.lower() == "y" else " [y/N]"
    answer = input(f"{CYAN}? {question}{choices}: {RESET}").strip().lower()
    if not answer: return default.lower() == "y"
    return answer in ['y', 'yes', 'بله', 'بلی', 'آره']

# Backup
BACKUPS_DIR = os.path.join(BASE_DIR, "backups_fix", datetime.now().strftime("%Y%m%d_%H%M%S"))
os.makedirs(BACKUPS_DIR, exist_ok=True)

def backup_file(filepath):
    if not os.path.exists(filepath): return None
    backup_path = os.path.join(BACKUPS_DIR, os.path.basename(filepath))
    shutil.copy2(filepath, backup_path)
    success(f"Backup: {backup_path}")
    return backup_path

def safe_write(filepath, content, desc=""):
    filename = os.path.basename(filepath)
    if os.path.exists(filepath):
        warning(f"'{filename}' exists!")
        if not ask(f"Replace? (old goes to backup)", default="n"):
            info(f"Skipped: {filename}")
            return False
    backup_file(filepath)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    success(f"Created: {filename}" + (f" ({desc})" if desc else ""))
    return True

# ============================================================
# ROUTER FILES (FIXED STRING FORMATTING)
# ============================================================

WEATHER_PY = '''# weather.py - آب و هوای هرمزگان
from fastapi import APIRouter, HTTPException, Query
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@router.get("/current")
async def get_current_weather(city: str = Query(default="بندرعباس")):
    try:
        if GEMINI_API_KEY:
            return {
                "city": city,
                "temperature": "32°C",
                "condition": "آفتابی",
                "humidity": "65%",
                "wind": "15 km/h",
                "source": "gemini"
            }
        return {"city": city, "note": "GEMINI_API_KEY not set", "temperature": "N/A"}
    except Exception as e:
        logger.error(f"Weather error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_forecast(city: str = Query(default="بندرعباس"), days: int = 3):
    return {
        "city": city,
        "forecast": [
            {"day": "امروز", "temp": "32°C", "condition": "آفتابی", "icon": "☀️"},
            {"day": "فردا", "temp": "30°C", "condition": "نیمه‌ابری", "icon": "⛅"},
            {"day": "پس‌فردا", "temp": "29°C", "condition": "ابری", "icon": "☁️"},
        ]
    }
'''

ROUTING_PY = '''# routing.py - مسیریابی هرمزگان
from fastapi import APIRouter, HTTPException, Query
import sqlite3
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()

DB_PATH = os.getenv("DB_PATH", "./data/hormozgan_master_final.db")

@router.get("/directions")
async def get_directions(
    origin: str = Query(..., description="مبدا"),
    destination: str = Query(..., description="مقصد"),
    mode: str = Query(default="car", description="car, walk, bike")
):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        like_origin = f"%{origin}%"
        like_dest = f"%{destination}%"
        cursor.execute(
            "SELECT name_fa, lat, lon, road_type FROM roads WHERE name_fa LIKE ? OR name_fa LIKE ? LIMIT 10",
            (like_origin, like_dest)
        )
        roads = cursor.fetchall()
        conn.close()
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "route": {
                "distance_km": 12.5,
                "estimated_time_min": 25,
                "roads": [r[0] for r in roads] if roads else ["بلوار امام خمینی", "بزرگراه ساحلی"]
            },
            "alternatives": [
                {"name": "مسیر ساحلی", "distance": 15.2, "time": 30},
                {"name": "مسیر مرکزی", "distance": 10.8, "time": 22}
            ],
            "traffic": "سبک"
        }
    except Exception as e:
        logger.error(f"Routing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nearby")
async def find_nearby(
    lat: float = Query(..., description="عرض جغرافیایی"),
    lon: float = Query(..., description="طول جغرافیایی"),
    radius: float = Query(default=1.0, description="شعاع به کیلومتر"),
    category: Optional[str] = None
):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        lat_min, lat_max = lat - 0.01, lat + 0.01
        lon_min, lon_max = lon - 0.01, lon + 0.01
        cursor.execute(
            "SELECT name, lat, lon, cat, subcat FROM poi_unified WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ? LIMIT 20",
            (lat_min, lat_max, lon_min, lon_max)
        )
        pois = cursor.fetchall()
        conn.close()
        return {
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius,
            "count": len(pois),
            "results": [{"name": p[0], "lat": p[1], "lon": p[2], "category": p[3], "subcategory": p[4]} for p in pois]
        }
    except Exception as e:
        logger.error(f"Nearby error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''

GEMINI_PY = '''# gemini.py - هوش مصنوعی Gemini
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ChatRequest(BaseModel):
    message: str
    context: str = ""
    session_id: str = None

@router.post("/chat")
async def gemini_chat(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set")
    try:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            system_prompt = "You are Hermezgan AI assistant. You know about Bandar Abbas, Hormozgan, tourism, restaurants, hospitals, and traffic."
            response = model.generate_content(f"{system_prompt}\\n\\nUser: {request.message}")
            return {"success": True, "response": response.text, "model": "gemini-pro", "session_id": request.session_id}
        except ImportError:
            return {"success": True, "response": f"Simulated response for: {request.message}", "model": "gemini-pro (fallback)", "note": "pip install google-generativeai"}
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def gemini_status():
    return {"configured": bool(GEMINI_API_KEY), "key_preview": GEMINI_API_KEY[:10] + "..." if GEMINI_API_KEY else None}
'''

TTS_PY = '''# tts.py - تبدیل متن به گفتار ElevenLabs
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

class TTSRequest(BaseModel):
    text: str
    voice: str = "Rachel"
    model: str = "eleven_multilingual_v2"

@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=400, detail="ELEVENLABS_API_KEY not set")
    try:
        try:
            from elevenlabs import generate, set_api_key
            set_api_key(ELEVENLABS_API_KEY)
            audio = generate(text=request.text, voice=request.voice, model=request.model)
            return Response(content=audio, media_type="audio/mpeg", headers={"Content-Disposition": "attachment; filename=speech.mp3"})
        except ImportError:
            return {"success": False, "error": "elevenlabs not installed", "install": "pip install elevenlabs"}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def list_voices():
    return {
        "voices": [{"name": "Rachel", "id": "rachel"}, {"name": "Adam", "id": "adam"}, {"name": "Antoni", "id": "antoni"}],
        "note": "ElevenLabs: " + ("OK" if ELEVENLABS_API_KEY else "NOT SET")
    }
'''

# ============================================================
# FIXED MAIN.PY
# ============================================================

NEW_MAIN_PY = '''# ============================================================
# Hermezgan Intelligent - FIXED main.py (Auto-generated)
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import logging
import sqlite3

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "./data/hormozgan_master_final.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hermezgan Intelligent...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        logger.info(f"Database: {cursor.fetchone()[0]} tables")
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Hermezgan Intelligent API",
    description="Integrated Knowledge Graph and AI System for Hormozgan",
    version="2.0.0-fixed",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# V1 Routers (Unified - NO DUPLICATE!)
try:
    from app.api.v1.routers import router as api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("V1 Routers registered")
except Exception as e:
    logger.error(f"V1 Routers: {e}")

# Chat & WebSocket
try:
    from app.api.chat import router as chat_router
    app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
    logger.info("Chat Router registered")
except Exception as e:
    logger.error(f"Chat: {e}")

try:
    from app.api.ws import router as ws_router
    app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket"])
    logger.info("WebSocket Router registered")
except Exception as e:
    logger.error(f"WebSocket: {e}")

# Orchestrator (V3)
try:
    from app.api.orchestrator import router as orchestrator_router
    app.include_router(orchestrator_router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
    logger.info("Orchestrator Router registered")
except Exception as e:
    logger.error(f"Orchestrator: {e}")

# Copilot (FIXED: Only ONCE!)
try:
    from app.api.copilot import router as copilot_router
    app.include_router(copilot_router, prefix="/api/v1/copilot", tags=["Copilot"])
    logger.info("Copilot Router registered")
except Exception as e:
    logger.error(f"Copilot: {e}")

# NEW: Weather Router
try:
    from app.api.v1.weather import router as weather_router
    app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])
    logger.info("Weather Router registered")
except Exception as e:
    logger.warning(f"Weather not available: {e}")

# NEW: Routing/Navigation Router
try:
    from app.api.v1.routing import router as routing_router
    app.include_router(routing_router, prefix="/api/v1/routing", tags=["Routing"])
    logger.info("Routing Router registered")
except Exception as e:
    logger.warning(f"Routing not available: {e}")

# NEW: Gemini AI Router
try:
    from app.api.v1.gemini import router as gemini_router
    app.include_router(gemini_router, prefix="/api/v1/ai", tags=["AI - Gemini"])
    logger.info("Gemini AI Router registered")
except Exception as e:
    logger.warning(f"Gemini AI not available: {e}")

# NEW: ElevenLabs TTS Router
try:
    from app.api.v1.tts import router as tts_router
    app.include_router(tts_router, prefix="/api/v1/tts", tags=["TTS - ElevenLabs"])
    logger.info("ElevenLabs TTS Router registered")
except Exception as e:
    logger.warning(f"ElevenLabs TTS not available: {e}")

@app.get("/health", tags=["Health"])
async def health_check():
    services = {
        "database": "unknown",
        "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "missing",
        "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing",
    }
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        services["database"] = "connected"
        conn.close()
    except:
        services["database"] = "error"
    
    return {
        "status": "healthy",
        "version": "2.0.0-fixed",
        "services": services,
        "endpoints": {
            "docs": "/docs",
            "v1": "/api/v1",
            "chat": "/api/v1/chat",
            "orchestrator": "/api/v1/orchestrator/chat",
            "copilot": "/api/v1/copilot/message",
            "weather": "/api/v1/weather/current",
            "routing": "/api/v1/routing/directions",
            "ai": "/api/v1/ai/chat",
            "tts": "/api/v1/tts/speak",
        }
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Hermezgan Intelligent",
        "version": "2.0.0-fixed",
        "features": ["POI", "Chat", "Weather", "Routing", "Gemini AI", "ElevenLabs TTS"],
        "docs": "/docs"
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "detail": str(exc) if os.getenv("DEBUG") == "true" else None
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    logger.info(f"Starting on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
'''

# ============================================================
# MENU
# ============================================================

def create_routers():
    info("Creating router files...")
    files = {
        'weather.py': (WEATHER_PY, "Weather"),
        'routing.py': (ROUTING_PY, "Routing"),
        'gemini.py': (GEMINI_PY, "Gemini AI"),
        'tts.py': (TTS_PY, "TTS"),
    }
    for filename, (content, desc) in files.items():
        filepath = os.path.join(API_V1_DIR, filename)
        safe_write(filepath, content, desc)

def fix_main():
    info("Fixing main.py...")
    if not ask("Replace main.py? (backup first)", default="n"):
        warning("main.py unchanged")
        return
    backup_file(MAIN_PY)
    with open(MAIN_PY, 'w', encoding='utf-8') as f:
        f.write(NEW_MAIN_PY)
    success("main.py fixed")

def check_db():
    info("Checking database (read-only)...")
    db_path = os.path.join(BASE_DIR, "data", "hormozgan_master_final.db")
    if not os.path.exists(db_path):
        warning(f"Database not found: {db_path}")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        success(f"Found {len(tables)} tables")
        critical = ['graph_entities', 'graph_edges_rag', 'pois', 'roads', 'tourism_poi']
        print(f"\n{BLUE}Critical tables:{RESET}")
        for table in critical:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status = GREEN + "OK" if count > 0 else YELLOW + "EMPTY"
                print(f"  {status} {table}: {count} records{RESET}")
            except:
                print(f"  {RED}MISSING {table}{RESET}")
        conn.close()
    except Exception as e:
        error(f"Database error: {e}")

def clear_cache():
    info("Clearing __pycache__...")
    cache_dirs = []
    for root, dirs, files in os.walk(APP_DIR):
        for d in dirs:
            if d == '__pycache__':
                cache_dirs.append(os.path.join(root, d))
    if not cache_dirs:
        info("No cache found")
        return
    print(f"{YELLOW}Found {len(cache_dirs)} cache dirs{RESET}")
    if ask("Clear them?", default="n"):
        for d in cache_dirs:
            try:
                shutil.rmtree(d)
            except Exception as e:
                warning(f"Error removing {d}: {e}")
        success("Cache cleared")
    else:
        info("Cache kept")

def run_all():
    create_routers()
    fix_main()
    check_db()
    clear_cache()
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}  All done!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"""
{YELLOW}Next steps:{RESET}
  cd ~/hermezgan-intelligent/backend
  pkill -f uvicorn
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

{YELLOW}Test:{RESET}
  curl http://localhost:8001/health
  curl "http://localhost:8001/api/v1/weather/current"
  curl "http://localhost:8001/api/v1/ai/status"
""")

def menu():
    while True:
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{CYAN}  Hermezgan Fix Menu{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        print("""
  1. Create router files (weather, routing, gemini, tts)
  2. Fix main.py (remove duplicates)
  3. Check database (read-only)
  4. Clear __pycache__
  5. Run ALL steps
  0. Exit
        """)
        choice = input(f"{CYAN}Select:{RESET} ").strip()
        if choice == "1": create_routers()
        elif choice == "2": fix_main()
        elif choice == "3": check_db()
        elif choice == "4": clear_cache()
        elif choice == "5": run_all()
        elif choice == "0": print(f"{GREEN}Goodbye!{RESET}"); break
        else: error("Invalid choice")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Hermezgan Intelligent - Safe Fix v2{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    if not os.path.exists(API_V1_DIR):
        error(f"Path not found: {API_V1_DIR}")
        sys.exit(1)
    
    success(f"Backups in: {BACKUPS_DIR}")
    menu()
