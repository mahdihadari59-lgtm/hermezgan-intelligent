import logging
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.core.config.settings import settings
from app.core.config.env import get_env_bool


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.threadName,
            "environment": settings.ENVIRONMENT,
            "app": settings.APP_NAME
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }

    FORMATS = {
        'DEBUG': '\033[36m%(asctime)s\033[0m - \033[36m%(levelname)s\033[0m - \033[90m%(name)s\033[0m - %(message)s',
        'INFO': '\033[32m%(asctime)s\033[0m - \033[32m%(levelname)s\033[0m - \033[90m%(name)s\033[0m - %(message)s',
        'WARNING': '\033[33m%(asctime)s\033[0m - \033[33m%(levelname)s\033[0m - \033[90m%(name)s\033[0m - %(message)s',
        'ERROR': '\033[31m%(asctime)s\033[0m - \033[31m%(levelname)s\033[0m - \033[90m%(name)s\033[0m - %(message)s',
        'CRITICAL': '\033[35m%(asctime)s\033[0m - \033[35m%(levelname)s\033[0m - \033[90m%(name)s\033[0m - %(message)s'
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelname, self.FORMATS['INFO'])
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class LogConfig:
    def __init__(self):
        self.level = settings.LOG_LEVEL
        self.format = settings.LOG_FORMAT
        self.log_file = settings.LOG_FILE
        self.max_size = settings.LOG_MAX_SIZE
        self.backup_count = settings.LOG_BACKUP_COUNT
        self.log_body = settings.LOG_BODY

    def setup(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.level.upper()))

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        if self.format == "json":
            formatter = JSONFormatter()
        elif self.format == "colored" and sys.stdout.isatty():
            formatter = ColoredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        self._configure_external_loggers()

        logger = logging.getLogger(__name__)
        logger.info(f"✅ Logging configured: level={self.level}, format={self.format}")

    def _configure_external_loggers(self):
        external_loggers = {
            "uvicorn": logging.WARNING,
            "uvicorn.access": logging.WARNING,
            "uvicorn.error": logging.ERROR,
            "sqlalchemy": logging.WARNING,
            "sqlalchemy.engine": logging.WARNING,
            "sqlalchemy.pool": logging.WARNING,
            "redis": logging.WARNING,
            "httpx": logging.WARNING,
            "httpcore": logging.WARNING,
            "urllib3": logging.WARNING,
            "requests": logging.WARNING,
            "asyncio": logging.WARNING,
            "multipart": logging.WARNING,
        }

        for logger_name, level in external_loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)


_log_configured = False


def setup_logging(force: bool = False):
    global _log_configured

    if _log_configured and not force:
        return

    config = LogConfig()
    config.setup()
    _log_configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    def log_info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)

    def log_error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)

    def log_debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)
