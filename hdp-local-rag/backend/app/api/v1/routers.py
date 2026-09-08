# ============================================================
# routers.py - ثبت تمام Routerها
# ============================================================
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# لیست routerهایی که باید ثبت شوند
_MODULE_MAP = {
    "locations": "app.api.v1.endpoints.locations",
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
]

for module_name, prefix in routers_to_import:
    module = None
    # اول از endpoints/ (نسخه‌ی جدید) امتحان کن
    try:
        module = __import__(f"app.api.v1.endpoints.{module_name}", fromlist=["router"])
    except ImportError:
        module = None

    # اگه توی endpoints/ نبود، مسیر قدیمی رو امتحان کن
    if module is None:
        try:
            module = __import__(f"app.api.v1.{module_name}", fromlist=["router"])
        except ImportError as e:
            logger.warning(f"⚠️ ماژول {module_name} یافت نشد: {e}")
            continue
        except Exception as e:
            logger.error(f"❌ خطا در ثبت {module_name}: {e}")
            continue

    try:
        module = __import__(_MODULE_MAP.get(module_name, f"app.api.v1.{module_name}"), fromlist=["router"])
        if hasattr(module, "router"):
            router.include_router(
                module.router,
                prefix=f"/{prefix}",
                tags=[prefix.capitalize()]
            )
            logger.info(f"✅ Router {module_name} ثبت شد")
        else:
            logger.warning(f"⚠️ Router {module_name} دارای router نیست")
    except Exception as e:
        logger.error(f"❌ خطا در ثبت {module_name}: {e}")
