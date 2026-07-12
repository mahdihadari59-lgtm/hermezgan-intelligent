from pydantic_settings import BaseSettings
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

settings = Settings()
