#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.services.orchestrator_service import OrchestratorService

from app.api.chat import router as chat_router
from app.api.v1.endpoints.voice import router as voice_router

try:
    from app.api.v1.routers import router as api_v1_router
except Exception:
    api_v1_router = None

try:
    from app.api.ws import router as ws_router
except Exception:
    ws_router = None

try:
    from app.api.orchestrator import router as orchestrator_router
except Exception:
    orchestrator_router = None

try:
    from app.api.copilot import router as copilot_router
except Exception:
    copilot_router = None

orchestrator_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator_service
    orchestrator_service = OrchestratorService()
    app.state.orchestrator = orchestrator_service
    logger.info("🚀 HDP AI CORE READY")
    yield
    logger.info("🛑 Stopping HDP...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hormozgan Intelligent",
        version="8.0",
        debug=os.getenv("DEBUG", "false").lower() == "true",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if api_v1_router is not None:
        app.include_router(api_v1_router, prefix="/api/v1")

    app.include_router(chat_router, prefix="/api")
    app.include_router(voice_router, prefix="/api/v1")

    if ws_router is not None:
        app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket"])

    if orchestrator_router is not None:
        app.include_router(orchestrator_router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])

    if copilot_router is not None:
        app.include_router(copilot_router, prefix="/api/v1/copilot", tags=["Copilot"])

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "8.0"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
