from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.api.v1.routers import router as api_router

app = FastAPI(
    title="Hormozgan Intelligent API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Hormozgan Intelligent"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
