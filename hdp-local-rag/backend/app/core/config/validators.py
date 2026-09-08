from typing import Any, Dict, List, Optional
import re
from urllib.parse import urlparse


class ConfigValidator:
    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = None) -> bool:
        if not url:
            return False

        try:
            parsed = urlparse(url)
            if allowed_schemes and parsed.scheme not in allowed_schemes:
                return False
            return bool(parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_port(port: int) -> bool:
        return 1 <= port <= 65535

    @staticmethod
    def validate_path(path: str) -> bool:
        if not path:
            return False
        return not any(c in path for c in ['\\', ':', '*', '?', '"', '<', '>', '|'])

    @staticmethod
    def validate_env_name(name: str) -> bool:
        allowed = ["development", "staging", "production", "testing"]
        return name in allowed

    @staticmethod
    def validate_log_level(level: str) -> bool:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        return level.upper() in allowed


def validate_all_settings() -> Dict[str, List[str]]:
    from app.core.config.settings import settings

    errors = {}

    if settings.SECRET_KEY == "your-secret-key-here-change-in-production":
        if settings.is_production:
            errors.setdefault("SECRET_KEY", []).append("کلید امنیتی در محیط تولید باید تغییر کند")

    if not ConfigValidator.validate_url(settings.DATABASE_URL, ["postgresql", "postgresql+asyncpg"]):
        errors.setdefault("DATABASE_URL", []).append("آدرس دیتابیس نامعتبر است")

    if settings.REDIS_URL and not ConfigValidator.validate_url(settings.REDIS_URL, ["redis", "rediss"]):
        errors.setdefault("REDIS_URL", []).append("آدرس Redis نامعتبر است")

    for origin in settings.cors_origins_list:
        if not ConfigValidator.validate_url(origin, ["http", "https"]):
            errors.setdefault("CORS_ORIGINS", []).append(f"دامنه {origin} نامعتبر است")

    if settings.SMTP_USER and not ConfigValidator.validate_email(settings.SMTP_USER):
        errors.setdefault("SMTP_USER", []).append("ایمیل SMTP نامعتبر است")

    if not ConfigValidator.validate_env_name(settings.ENVIRONMENT):
        errors.setdefault("ENVIRONMENT", []).append(f"محیط {settings.ENVIRONMENT} نامعتبر است")

    if not ConfigValidator.validate_log_level(settings.LOG_LEVEL):
        errors.setdefault("LOG_LEVEL", []).append(f"سطح لاگ {settings.LOG_LEVEL} نامعتبر است")

    return errors
