import os
import json
from typing import Optional, List, Any, Dict
from pathlib import Path
from dotenv import load_dotenv


def load_env(env_file: Optional[str] = None) -> bool:
    if env_file is None:
        env_file = ".env"

    env_path = Path(env_file)

    if env_path.exists():
        load_dotenv(env_path)
        return True

    parent_env = Path("..") / env_file
    if parent_env.exists():
        load_dotenv(parent_env)
        return True

    return False


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on", "y")


def get_env_int(key: str, default: int = 0) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_list(key: str, default: Optional[List[str]] = None, sep: str = ",") -> List[str]:
    if default is None:
        default = []

    value = os.getenv(key)

    if not value:
        return default

    return [item.strip() for item in value.split(sep) if item.strip()]


def get_env_dict(key: str, default: Optional[Dict] = None) -> Dict:
    if default is None:
        default = {}

    value = os.getenv(key)

    if not value:
        return default

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def get_env_path(key: str, default: Optional[str] = None) -> Optional[Path]:
    value = os.getenv(key, default)

    if not value:
        return None

    return Path(value)


def set_env(key: str, value: str):
    os.environ[key] = str(value)


def get_required_env(key: str) -> str:
    value = os.getenv(key)

    if value is None:
        raise ValueError(f"متغیر محیطی {key} اجباری است و تنظیم نشده")

    return value


def get_env_or_raise(key: str) -> str:
    return get_required_env(key)


class Env:
    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        return get_env(key, default)

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        return get_env_bool(key, default)

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        return get_env_int(key, default)

    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        return get_env_float(key, default)

    @staticmethod
    def get_list(key: str, default: Optional[List[str]] = None, sep: str = ",") -> List[str]:
        return get_env_list(key, default, sep)

    @staticmethod
    def get_dict(key: str, default: Optional[Dict] = None) -> Dict:
        return get_env_dict(key, default)

    @staticmethod
    def get_path(key: str, default: Optional[str] = None) -> Optional[Path]:
        return get_env_path(key, default)

    @staticmethod
    def get_required(key: str) -> str:
        return get_required_env(key)

    @staticmethod
    def set(key: str, value: str):
        set_env(key, value)


env = Env()
