"""FastAPI App Factory"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1 import routers
from app.core.logger import logger

def create_app() -> FastAPI:
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = create_app()
