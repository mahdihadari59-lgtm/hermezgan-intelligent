#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.services.orchestrator_service import OrchestratorService

orchestrator_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator_service
    orchestrator_service = OrchestratorService()
    app.state.orchestrator = orchestrator_service
    print("=" * 60)
    print("🚀 HDP AI CORE READY")
    print("=" * 60)
    yield
    print("🛑 Stopping HDP...")


app = FastAPI(
    title="Hormozgan Intelligent",
    version="8.0",
    lifespan=lifespan
)

# Chat
from app.api.chat import router as chat_router
app.include_router(chat_router, prefix="/api")

# Voice
from app.api.v1.endpoints.voice import router as voice_router
app.include_router(voice_router, prefix="/api/v1")
