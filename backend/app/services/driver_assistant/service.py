from __future__ import annotations
import re
from pathlib import Path

import logging
import os
import time
from typing import Any, Optional

from app.core.ai_kernel_v6 import HDPAIKernelV6
from app.services.driver_assistant.exceptions import (
    DestinationNotFoundException,
    SessionNotFoundException,
)
from app.services.driver_assistant.models import (
    DriverIntent,
    DriverSession,
    Location,
    NavigationStatus,
    POICandidate,
)
from app.services.driver_assistant.session_store import SessionStore
from app.services.navigation.navigation_engine import NavigationEngine
from app.services.navigation.poi_resolver import POIResolver
from app.services.tts.pipeline import TTSPipeline
from app.services.websocket.hub import ws_hub

logger = logging.getLogger(__name__)


class DriverAssistantService:
    def __init__(self):
        ttl = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

        self.sessions = SessionStore(ttl_seconds=ttl)
        self.kernel = HDPAIKernelV6()
        self.nav_engine = NavigationEngine()
        self.poi_resolver = POIResolver()
        self.tts = TTSPipeline(
            os.getenv("TTS_CACHE_DIR", str(Path(__file__).resolve().parents[3] / "runtime" / "tts_cache"))
        )
        self.ws = ws_hub

    async def startup(self) -> None:
        await self.sessions.start()

    async def shutdown(self) -> None:
        await self.sessions.stop()

    @staticmethod
    def _location(
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None,
        heading: Optional[float] = None,
        speed: Optional[float] = None,
    ) -> Location:
        if not -90 <= latitude <= 90:
            raise ValueError("عرض جغرافیایی نامعتبر است")

        if not -180 <= longitude <= 180:
            raise ValueError("طول جغرافیایی نامعتبر است")

        return Location(
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            heading=heading,
            speed=speed,
        )

    async def _get_session(self, session_id: str) -> DriverSession:
        session = await self.sessions.get(session_id)

        if not session:
            raise SessionNotFoundException("جلسه دستیار راننده پیدا نشد")

        if not session.active:
            raise SessionNotFoundException("جلسه دستیار راننده فعال نیست")

        return session

    async def start(
        self,
        session_id: str,
        user_id: str,
        latitude: float,
        longitude: float,
        profile: str = "driving",
    ) -> dict[str, Any]:
        location = self._location(latitude, longitude)

        if profile not in {"driving", "walking", "cycling"}:
            profile = "driving"

        now = time.time()

        session = DriverSession(
            session_id=session_id,
            user_id=user_id,
            profile=profile,
            created_at=now,
            updated_at=now,
        )

        session.navigation.current_location = location
        session.context = {
            "current_location": location.as_dict(),
            "source": "driver_assistant",
        }

        await self.sessions.create(session)

        result = {
            "success": True,
            "status": "started",
            "session": session.as_dict(),
        }

        await self.ws.broadcast(session_id, "session_started", result)
        return result

    async def update_location(
        self,
        session_id: str,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None,
        heading: Optional[float] = None,
        speed: Optional[float] = None,
    ) -> dict[str, Any]:
        session = await self._get_session(session_id)

        location = self._location(
            latitude,
            longitude,
            accuracy,
            heading,
            speed,
        )

        session.context["current_location"] = location.as_dict()

        session.navigation, rerouted = await self.nav_engine.update(
            session.navigation,
            location,
            session.profile,
        )

        await self.sessions.update(session)

        result = {
            "success": True,
            "rerouted": rerouted,
            "off_route": session.navigation.off_route,
            "navigation": session.navigation.as_dict(),
        }

        await self.ws.broadcast(session_id, "location_update", result)

        if rerouted:
            await self.ws.broadcast(
                session_id,
                "reroute",
                session.navigation.as_dict(),
            )

        if session.navigation.status == NavigationStatus.ARRIVED:
            await self.ws.broadcast(
                session_id,
                "arrived",
                session.navigation.as_dict(),
            )

        return result

    async def _kernel_analyze(
        self,
        session: DriverSession,
        text: str,
    ) -> dict[str, Any]:
        payload = {
            "conversationId": session.session_id,
            "userId": session.user_id,
            "mode": "text",
            "query": text,
            "location": session.context.get("current_location") or {},
            "metadata": {
                "source": "driver_assistant",
                "classification": True,
            },
        }

        result = await self.kernel.handle(payload)
        context = result.get("context") or {}
        entities = context.get("entities") or {}

        raw_intent = (
            result.get("intent")
            or context.get("intent")
            or ""
        )

        return {
            "kernel_result": result,
            "kernel_intent": str(raw_intent),
            "entities": entities,
        }

    @staticmethod
    def _map_intent(
        kernel_intent: str,
        text: str,
        has_active_route: bool,
    ) -> DriverIntent:
        value = (kernel_intent or "").lower()
        text_lower = text.lower()

        # ---------------------------------------------------------
        # Bandari driving commands
        # این الگوها عمداً قبل از kernel_intent بررسی می‌شوند.
        # چون تشخیص فرمان رانندگی نباید وابسته به LLM باشد.
        #
        # «راست بِش» در داده‌های این پروژه یعنی «مستقیم برو»
        # و نباید با «به راست بپیچ» اشتباه شود.
        # «واگرد بَ چپ/راست» فرمان گردش است.
        # ---------------------------------------------------------

        bandari_navigation_patterns = (
            "چطور برم ب",
            "چِطور برَم ب",
            "چگونه برم ب",
            "چِگونه برَم ب",
            "برم ب",
            "بَرَم ب",
            "برو ب",
            "بِرو ب",
            "راست بش",
            "راست بِش",
            "واگرد ب",
            "واگِرد ب",
        )

        if any(pattern in text_lower for pattern in bandari_navigation_patterns):
            return DriverIntent.START_NAVIGATION

        # فرمان‌های مستقیم استاندارد مسیریابی
        standard_navigation_patterns = (
            "برو به ",
            "بروم به ",
            "مسیریابی به ",
            "مسیر به ",
            "حرکت به ",
            "navigate ",
            "navigation ",
        )

        if any(pattern in text_lower for pattern in standard_navigation_patterns):
            return DriverIntent.START_NAVIGATION

        if any(x in text_lower for x in ("لغو مسیر", "لغو مقصد", "لغو کن", "cancel")):
            return DriverIntent.CANCEL_DESTINATION

        if any(x in text_lower for x in ("چقدر مونده", "چقدر مانده", "زمان رسیدن", "eta")):
            return DriverIntent.ETA_QUERY

        if any(x in text_lower for x in ("نزدیک‌ترین", "نزدیکترین", "nearest")):
            return DriverIntent.FIND_NEAREST_POI

        if any(x in text_lower for x in ("عوض کن", "تغییر مسیر", "مسیر جدید", "change route")):
            return DriverIntent.CHANGE_ROUTE

        if any(x in text_lower for x in ("برو به", "بروم به", "حرکت به", "navigate", "navigation")):
            return DriverIntent.START_NAVIGATION

        if value in {
            "route",
            "routing",
            "navigation",
            "directions",
            "مسیریابی",
            "مسیر",
        }:
            return (
                DriverIntent.ROUTE
                if has_active_route
                else DriverIntent.START_NAVIGATION
            )

        return DriverIntent.GENERAL_CHAT

    async def _resolve_destination(
        self,
        text: str,
        entities: dict[str, Any],
        location: Optional[Location],
    ) -> POICandidate:
        destination = str(entities.get("destination") or "").strip()

        if not destination:
            cleaned = text.strip()

            # Bandari navigation forms:
            # چِطور بَرَم بَ بازار نیلی؟
            # چطور برم ب بازار نیلی
            # برم ب بازار نیلی
            m = re.search(
                r"(?:چطور|چِطور|چگونه|چِگونه)\s+"
                r"(?:برم|بَرَم|برو|بِرو)\s+"
                r"(?:به|بَ|ب)\s+(.+?)"
                r"[؟?!.,،]*$",
                cleaned,
                re.IGNORECASE,
            )

            if not m:
                m = re.search(
                    r"(?:برم|بَرَم|برو|بِرو)\s+"
                    r"(?:به|بَ|ب)\s+(.+?)"
                    r"[؟?!.,،]*$",
                    cleaned,
                    re.IGNORECASE,
                )

            if m:
                destination = m.group(1).strip()
            else:
                # Standard navigation forms
                for prefix in (
                    "برو به ",
                    "برو ",
                    "مسیریابی به ",
                    "مسیر به ",
                    "حرکت به ",
                    "به ",
                ):
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):]
                        break

                destination = cleaned.strip()

        # حذف علائم انتهایی مقصد
        destination = re.sub(r"[؟?!.,،]+$", "", destination).strip()

        candidates = await self.poi_resolver.search(
            destination,
            near_location=location,
            limit=10,
        )

        if not candidates:
            raise DestinationNotFoundException(
                f"مقصد «{destination}» در پایگاه مکان‌ها پیدا نشد"
            )

        return await self.poi_resolver.resolve_ambiguity(
            candidates,
            current_location=location,
        )

    async def _start_route_for_destination(
        self,
        session: DriverSession,
        poi: POICandidate,
        changing: bool = False,
    ) -> dict[str, Any]:
        current = session.navigation.current_location

        if not current:
            raise ValueError("موقعیت فعلی راننده مشخص نیست")

        session.navigation.destination_poi = poi

        session.navigation = await self.nav_engine.start_navigation(
            navigation=session.navigation,
            origin=current,
            destination=poi.location,
            destination_name=poi.name,
            profile=session.profile,
        )

        await self.sessions.update(session)

        message = (
            f"مسیر جدید به {poi.name} آماده شد."
            if changing
            else f"مسیریابی به {poi.name} شروع شد."
        )

        return {
            "success": True,
            "message": message,
            "destination": poi.as_dict(),
            "navigation": session.navigation.as_dict(),
        }

    async def _handle_eta(self, session: DriverSession) -> dict[str, Any]:
        if session.navigation.status != NavigationStatus.NAVIGATING:
            return {
                "success": False,
                "message": "در حال حاضر مسیریابی فعال نیست",
                "navigation": session.navigation.as_dict(),
            }

        return {
            "success": True,
            "message": (
                f"{self.nav_engine.get_distance_text(session.navigation)} مانده. "
                f"{self.nav_engine.get_eta_text(session.navigation)}"
            ),
            "navigation": session.navigation.as_dict(),
        }

    async def _handle_general_chat(
        self,
        session: DriverSession,
        text: str,
    ) -> dict[str, Any]:
        result = await self.kernel.handle(
            {
                "conversationId": session.session_id,
                "userId": session.user_id,
                "mode": "text",
                "query": text,
                "location": session.context.get("current_location") or {},
                "metadata": {
                    "source": "driver_assistant",
                    "chat_mode": True,
                },
            }
        )

        return {
            "success": True,
            "message": result.get("answer") or result.get("text") or "",
            "intent": result.get("intent"),
            "kernel": result,
            "navigation": session.navigation.as_dict(),
        }

    async def command(
        self,
        session_id: str,
        text: str,
    ) -> dict[str, Any]:
        session = await self._get_session(session_id)

        analysis = await self._kernel_analyze(session, text)

        intent = self._map_intent(
            analysis["kernel_intent"],
            text,
            session.navigation.status == NavigationStatus.NAVIGATING,
        )

        location = session.navigation.current_location

        if intent in {
            DriverIntent.START_NAVIGATION,
            DriverIntent.ROUTE,
            DriverIntent.CHANGE_ROUTE,
        }:
            poi = await self._resolve_destination(
                text,
                analysis["entities"],
                location,
            )

            result = await self._start_route_for_destination(
                session,
                poi,
                changing=intent == DriverIntent.CHANGE_ROUTE,
            )

        elif intent == DriverIntent.CANCEL_DESTINATION:
            session.navigation.destination = None
            session.navigation.destination_poi = None
            session.navigation.destination_name = None
            session.navigation.active_route = None
            session.navigation.instructions = []
            session.navigation.distance_remaining_m = 0.0
            session.navigation.duration_remaining_s = 0.0
            session.navigation.status = NavigationStatus.CANCELLED
            session.navigation.off_route = False

            await self.sessions.update(session)

            result = {
                "success": True,
                "message": "مقصد و مسیریابی لغو شد.",
                "navigation": session.navigation.as_dict(),
            }

        elif intent == DriverIntent.FIND_NEAREST_POI:
            query = text
            candidates = await self.poi_resolver.search(
                query,
                near_location=location,
                limit=10,
            )

            poi = await self.poi_resolver.resolve_ambiguity(
                candidates,
                current_location=location,
            )

            if not poi:
                raise DestinationNotFoundException(
                    "مکان موردنظر پیدا نشد"
                )

            result = await self._start_route_for_destination(
                session,
                poi,
            )

            result["message"] = (
                f"نزدیک‌ترین مورد پیدا شد: {poi.name}. "
                "مسیریابی شروع شد."
            )

        elif intent == DriverIntent.ETA_QUERY:
            result = await self._handle_eta(session)

        else:
            result = await self._handle_general_chat(
                session,
                text,
            )

        session.context["last_command"] = text
        session.context["last_intent"] = intent.value
        await self.sessions.update(session)

        audio_path = None
        if result.get("message"):
            audio_path = await self.tts.synthesize(result["message"])

        result["intent"] = intent.value
        result["audio"] = {
            "available": bool(audio_path),
            "path": audio_path,
        }

        await self.ws.broadcast(
            session_id,
            "command_response",
            result,
        )

        return result

    async def stop(self, session_id: str) -> dict[str, Any]:
        session = await self.sessions.get(session_id)

        if not session:
            return {
                "success": True,
                "status": "not_found",
                "session_id": session_id,
            }

        session.active = False
        session.navigation.status = NavigationStatus.CANCELLED
        await self.sessions.update(session)

        result = {
            "success": True,
            "status": "stopped",
            "session_id": session_id,
            "navigation": session.navigation.as_dict(),
        }

        await self.ws.broadcast(session_id, "session_stopped", result)
        return result

    async def status(
        self,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        if session_id:
            session = await self.sessions.get(session_id)

            if not session:
                return {
                    "success": False,
                    "status": "not_found",
                    "session_id": session_id,
                }

            return {
                "success": True,
                "session": session.as_dict(),
            }

        sessions = await self.sessions.all()

        return {
            "success": True,
            "service": "driver_assistant",
            "kernel": "HDPAIKernelV6",
            "routing_provider": "osrm",
            "session_count": len(sessions),
        }


_driver_assistant_service: Optional[DriverAssistantService] = None


def get_driver_assistant_service() -> DriverAssistantService:
    global _driver_assistant_service

    if _driver_assistant_service is None:
        _driver_assistant_service = DriverAssistantService()

    return _driver_assistant_service


driver_assistant_service = get_driver_assistant_service()
