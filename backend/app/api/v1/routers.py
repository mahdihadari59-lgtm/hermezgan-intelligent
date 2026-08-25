# ============================================================
# routers.py - ثبت تمام Routerها
# ============================================================
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

_MODULE_MAP = {
    "tts": "app.api.v1.tts",
    "locations": "app.api.v1.endpoints.locations",
    "bandari_voice": "app.api.v1.endpoints.bandari_voice",
}

routers_to_import = [
    ("ping", "ping"),
    ("chat", "chat"),
    ("locations", "locations"),
    ("analytics", "analytics"),
    ("cameras", "cameras"),
    ("hotspots", "hotspots"),
    ("health", "health"),
    ("traffic", "traffic"),
    ("auth", "auth"),
    ("pois", "pois"),
    ("bandari_voice", "bandari-voice"),
]

for module_name, prefix in routers_to_import:
    try:
        module_path = _MODULE_MAP.get(
            module_name,
            f"app.api.v1.{module_name}",
        )
        module = __import__(
            module_path,
            fromlist=["router"],
        )
        if hasattr(module, "router"):
            router.include_router(
                module.router,
                prefix=f"/{prefix}",
                tags=[prefix.capitalize()]
            )
            logger.info(f"✅ Router {module_name} ثبت شد")
        else:
            logger.warning(f"⚠️ Router {module_name} دارای router نیست")
    except ImportError as e:
        logger.warning(f"⚠️ ماژول {module_name} یافت نشد: {e}")
    except Exception as e:
        logger.error(f"❌ خطا در ثبت {module_name}: {e}")
