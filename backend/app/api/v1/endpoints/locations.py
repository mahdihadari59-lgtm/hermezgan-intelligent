from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.routing.osrm_service import osrm_service

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/route")
async def calculate_route(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    end_lat: float = Query(...),
    end_lng: float = Query(...),
    profile: str = Query("driving"),
) -> dict[str, Any]:
    """
    Calculate a route using the existing OSRM service.

    GET /api/v1/locations/route
    """

    try:
        return await osrm_service.route(
            start_lat=start_lat,
            start_lng=start_lng,
            end_lat=end_lat,
            end_lng=end_lng,
            profile=profile,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Routing service error: {exc}",
        ) from exc
