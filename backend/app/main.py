"""FastAPI App Factory"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import router
from app.core.logger import logger


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

    logger.info("Application initialized")

    return app


app = create_app()
