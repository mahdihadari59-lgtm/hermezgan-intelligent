# ============================================================
# routers.py - ثبت مرکزی Routerهای API v1
# ============================================================

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _register(module_path: str, name: str) -> None:
    try:
        module = __import__(module_path, fromlist=["router"])
        child_router = getattr(module, "router", None)

        if child_router is None:
            logger.warning("Router %s فاقد متغیر router است", name)
            return

        router.include_router(child_router)
        logger.info("Router %s ثبت شد", name)

    except Exception:
        logger.exception("خطا در ثبت Router %s از %s", name, module_path)


# ------------------------------------------------------------
# Root v1 routers
# ------------------------------------------------------------

_register("app.api.v1.ping", "ping")
_register("app.api.v1.health", "health")
_register("app.api.v1.auth", "auth")
_register("app.api.v1.pois", "pois")
_register("app.api.v1.analytics", "analytics")
_register("app.api.v1.cameras", "cameras")
_register("app.api.v1.hotspots", "hotspots")
_register("app.api.v1.traffic", "traffic")


# ------------------------------------------------------------
# Endpoint routers
# ------------------------------------------------------------

_register("app.api.v1.endpoints.locations", "locations")


# ------------------------------------------------------------
# نکته:
# chat از طریق app.main به صورت مستقیم ثبت می‌شود.
# بنابراین اینجا دوباره ثبت نمی‌شود.
#
# routing / weather / gemini / tts نیز در app.main
# به صورت مستقیم ثبت می‌شوند.
# ------------------------------------------------------------
