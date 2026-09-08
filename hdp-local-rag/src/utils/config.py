"""
HDP Local RAG - Configuration
Termux-ready, mobile-first AI assistant for Hormozgan
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("HDP_DB_PATH", str(BASE_DIR / "db" / "hdp_master.db"))

GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY", "")
GOOGLE_GEMINI_MODEL = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-1.5-flash")

LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama3.1:8b")

LEVELS_API_KEY = os.getenv("LEVELS_API_KEY", "")
LEVELS_BASE_URL = os.getenv("LEVELS_BASE_URL", "https://api.levels.ai/v1")

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.65"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DENO_PORT = int(os.getenv("DENO_PORT", "3000"))

DEFAULT_LANGUAGE = "fa"
SUPPORTED_DIALECTS = ["bandari", "minabi", "qeshmi", "bastaki"]
