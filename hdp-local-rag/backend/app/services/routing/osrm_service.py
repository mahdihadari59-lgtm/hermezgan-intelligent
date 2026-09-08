from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "https://router.project-osrm.org"


class OSRMService:
    """
    OSRM routing service for HDP.

    Coordinates from API:
        latitude, longitude

    OSRM coordinates:
        longitude,latitude
    """

    def __init__(
        self,
        base_url: str = OSRM_BASE_URL,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def route(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        profile: str = "driving",
    ) -> dict[str, Any]:

        if not (-90 <= start_lat <= 90):
            raise ValueError("Invalid start_lat")

        if not (-180 <= start_lng <= 180):
            raise ValueError("Invalid start_lng")

        if not (-90 <= end_lat <= 90):
            raise ValueError("Invalid end_lat")

        if not (-180 <= end_lng <= 180):
            raise ValueError("Invalid end_lng")

        if profile not in {"driving", "walking", "cycling"}:
            profile = "driving"

        coordinates = (
            f"{start_lng},{start_lat};"
            f"{end_lng},{end_lat}"
        )

        url = (
            f"{self.base_url}/route/v1/"
            f"{profile}/{coordinates}"
        )

        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true",
            "alternatives": "false",
        }

        logger.info(
            "OSRM route: %s,%s -> %s,%s",
            start_lat,
            start_lng,
            end_lat,
            end_lng,
        )

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:
            response = await client.get(
                url,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok":
            raise RuntimeError(
                f"OSRM error: {data.get('code', 'UNKNOWN')}"
            )

        routes = data.get("routes") or []

        if not routes:
            raise RuntimeError("OSRM returned no route")

        route = routes[0]

        distance_m = float(route.get("distance", 0))
        duration_s = float(route.get("duration", 0))

        geometry = route.get("geometry") or {
            "type": "LineString",
            "coordinates": [],
        }

        legs = route.get("legs") or []

        return {
            "status": "success",
            "route": {
                "provider": "osrm",
                "source": "OpenStreetMap",
                "profile": profile,
                "start": {
                    "latitude": start_lat,
                    "longitude": start_lng,
                },
                "end": {
                    "latitude": end_lat,
                    "longitude": end_lng,
                },
                "distance_m": round(distance_m, 1),
                "distance_km": round(distance_m / 1000, 3),
                "duration_s": round(duration_s, 1),
                "duration_min": round(duration_s / 60, 2),
                "geometry": geometry,
                "legs": legs,
                "waypoints": data.get("waypoints", []),
            },
        }


osrm_service = OSRMService()
