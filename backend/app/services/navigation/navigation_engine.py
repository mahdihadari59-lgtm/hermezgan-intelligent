from __future__ import annotations

import math
import time
from typing import Any, Optional

from app.services.driver_assistant.models import (
    DriverSession,
    Location,
    NavigationState,
    NavigationStatus,
    POICandidate,
)
from app.services.routing.osrm_service import osrm_service
from app.services.navigation.instructions import InstructionExtractor


class NavigationEngine:
    OFF_ROUTE_METERS = 100.0
    ARRIVAL_METERS = 35.0

    def __init__(self):
        self.osrm = osrm_service

    @staticmethod
    def _distance_m(a: Location, b: Location) -> float:
        r = 6371000.0
        p1 = math.radians(a.latitude)
        p2 = math.radians(b.latitude)
        dp = math.radians(b.latitude - a.latitude)
        dl = math.radians(b.longitude - a.longitude)

        x = (
            math.sin(dp / 2) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        )

        return 2 * r * math.asin(math.sqrt(x))

    @staticmethod
    def _point_segment_distance_m(
        p: Location,
        a: tuple[float, float],
        b: tuple[float, float],
    ) -> float:
        mean_lat = math.radians(p.latitude)
        scale_x = 111320.0 * max(math.cos(mean_lat), 0.01)
        scale_y = 110540.0

        px = p.longitude * scale_x
        py = p.latitude * scale_y
        ax = a[0] * scale_x
        ay = a[1] * scale_y
        bx = b[0] * scale_x
        by = b[1] * scale_y

        dx = bx - ax
        dy = by - ay

        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)

        t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        qx = ax + t * dx
        qy = ay + t * dy

        return math.hypot(px - qx, py - qy)

    def distance_from_route(
        self,
        location: Location,
        route_data: Optional[dict[str, Any]],
    ) -> float:
        if not route_data:
            return float("inf")

        geometry = (route_data.get("route") or {}).get("geometry") or {}
        coords = geometry.get("coordinates") or []

        if len(coords) < 2:
            return float("inf")

        minimum = float("inf")

        for a, b in zip(coords, coords[1:]):
            minimum = min(
                minimum,
                self._point_segment_distance_m(
                    location,
                    (float(a[0]), float(a[1])),
                    (float(b[0]), float(b[1])),
                ),
            )

        return minimum

    @staticmethod
    def _encode_polyline(coords: list[list[float]], precision: int = 5) -> str:
        result: list[str] = []
        last_lat = 0
        last_lon = 0
        factor = 10 ** precision

        for lon, lat in coords:
            ilat = int(round(lat * factor))
            ilon = int(round(lon * factor))

            for value in (ilat - last_lat, ilon - last_lon):
                value = ~(value << 1) if value < 0 else (value << 1)
                while value >= 0x20:
                    result.append(chr((0x20 | (value & 0x1F)) + 63))
                    value >>= 5
                result.append(chr(value + 63))

            last_lat = ilat
            last_lon = ilon

        return "".join(result)

    def _mobile_route(self, raw: dict[str, Any]) -> dict[str, Any]:
        route = dict(raw.get("route") or {})
        geometry = route.get("geometry") or {}
        coords = geometry.get("coordinates") or []

        route["geometry"] = {
            "type": geometry.get("type", "LineString"),
            "coordinates": coords,
            "polyline": self._encode_polyline(coords) if coords else "",
        }

        route["instructions"] = InstructionExtractor.extract(raw)
        return route

    async def start_navigation(
        self,
        navigation: NavigationState,
        origin: Location,
        destination: Location,
        destination_name: str,
        profile: str,
    ) -> NavigationState:
        navigation.status = NavigationStatus.REROUTING
        navigation.current_location = origin
        navigation.destination = destination
        navigation.destination_name = destination_name

        raw = await self.osrm.route(
            start_lat=origin.latitude,
            start_lng=origin.longitude,
            end_lat=destination.latitude,
            end_lng=destination.longitude,
            profile=profile,
        )

        navigation.active_route = self._mobile_route(raw)

        route = raw["route"]
        navigation.distance_remaining_m = float(route["distance_m"])
        navigation.duration_remaining_s = float(route["duration_s"])
        navigation.eta_timestamp = time.time() + navigation.duration_remaining_s

        # دستورهای turn-by-turn تولیدشده برای مسیر موبایل
        navigation.instructions = (
            navigation.active_route.get("instructions")
            or route.get("instructions")
            or []
        )

        navigation.next_instruction_index = 0
        navigation.off_route = False
        navigation.last_reroute_timestamp = time.time()
        navigation.status = NavigationStatus.NAVIGATING

        return navigation

    async def reroute(
        self,
        navigation: NavigationState,
        current_location: Location,
        profile: str,
    ) -> NavigationState:
        if not navigation.destination:
            return navigation

        navigation.status = NavigationStatus.REROUTING

        return await self.start_navigation(
            navigation=navigation,
            origin=current_location,
            destination=navigation.destination,
            destination_name=navigation.destination_name or "مقصد",
            profile=profile,
        )

    async def update(
        self,
        navigation: NavigationState,
        location: Location,
        profile: str,
    ) -> tuple[NavigationState, bool]:
        navigation.current_location = location

        if navigation.status != NavigationStatus.NAVIGATING:
            return navigation, False

        if not navigation.destination:
            return navigation, False

        remaining_direct = self._distance_m(
            location,
            navigation.destination,
        )

        if remaining_direct <= self.ARRIVAL_METERS:
            navigation.distance_remaining_m = 0.0
            navigation.duration_remaining_s = 0.0
            navigation.status = NavigationStatus.ARRIVED
            navigation.off_route = False
            return navigation, False

        off_route_distance = self.distance_from_route(
            location,
            navigation.active_route,
        )

        navigation.off_route = off_route_distance > self.OFF_ROUTE_METERS

        if navigation.off_route:
            navigation = await self.reroute(
                navigation,
                location,
                profile,
            )
            return navigation, True

        route_distance = float(
            ((navigation.active_route or {}).get("distance_m"))
            or 0
        )
        route_duration = float(
            ((navigation.active_route or {}).get("duration_s"))
            or 0
        )

        ratio = (
            remaining_direct / route_distance
            if route_distance > 0
            else 0.0
        )

        navigation.distance_remaining_m = min(
            remaining_direct,
            max(route_distance * ratio, 0.0),
        )

        speed = location.speed
        if speed and speed > 1.0:
            navigation.duration_remaining_s = (
                navigation.distance_remaining_m / speed
            )
        elif route_distance > 0:
            navigation.duration_remaining_s = (
                route_duration
                * navigation.distance_remaining_m
                / route_distance
            )

        navigation.eta_timestamp = (
            time.time() + navigation.duration_remaining_s
        )

        return navigation, False

    def get_eta_text(self, navigation: NavigationState) -> str:
        if navigation.status != NavigationStatus.NAVIGATING:
            return "در حال حاضر مسیریابی فعال نیست"

        minutes = navigation.duration_remaining_s / 60.0

        if minutes < 1:
            return "کمتر از یک دقیقه تا مقصد مانده است"

        return f"حدود {round(minutes)} دقیقه تا مقصد مانده است"

    def get_distance_text(self, navigation: NavigationState) -> str:
        km = navigation.distance_remaining_m / 1000.0

        if km < 1:
            return f"{round(navigation.distance_remaining_m)} متر"

        return f"{km:.1f} کیلومتر"
