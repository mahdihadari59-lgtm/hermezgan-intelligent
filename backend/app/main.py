"""FastAPI App Factory"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger
from app.api.v1.routers import router
from app.api.copilot import router as copilot_router
from app.api.orchestrator import router as orchestrator_router
from app.api.chat import router as chat_router
from app.api.ws import router as ws_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hermezgan Intelligent API",
        version="2.1.1",
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")
    app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket"])
    app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
    app.include_router(orchestrator_router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
    app.include_router(copilot_router, prefix="/api/v1/copilot", tags=["Copilot"])
    logger.info("✅ Application initialized")
    return app


app = create_app()

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.1.1"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
