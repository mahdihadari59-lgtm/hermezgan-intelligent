from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.routing.osrm_service import osrm_service

router = APIRouter(tags=["Routing"])


@router.get("/directions")
async def get_directions(
    start_lat: float = Query(..., description="عرض جغرافیایی مبدا"),
    start_lng: float = Query(..., description="طول جغرافیایی مبدا"),
    end_lat: float = Query(..., description="عرض جغرافیایی مقصد"),
    end_lng: float = Query(..., description="طول جغرافیایی مقصد"),
    profile: str = Query(
        "driving",
        description="driving, walking, cycling",
    ),
) -> dict[str, Any]:
    """
    مسیریابی واقعی با سرویس OSRM.

    GET /api/v1/routing/directions
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
            detail=f"OSRM routing service error: {exc}",
        ) from exc


@router.get("/nearby")
async def find_nearby(
    lat: float = Query(..., description="عرض جغرافیایی"),
    lon: float = Query(..., description="طول جغرافیایی"),
    radius: float = Query(1.0, gt=0, description="شعاع به کیلومتر"),
    category: Optional[str] = Query(None),
) -> dict[str, Any]:
    """
    یافتن POIهای نزدیک از دیتابیس محلی.
    """

    import sqlite3
    import os

    db_path = os.getenv(
        "DB_PATH",
        "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db",
    )

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        delta = radius / 111.0

        query = """
            SELECT name, lat, lon, cat, subcat
            FROM poi_unified
            WHERE lat BETWEEN ? AND ?
              AND lon BETWEEN ? AND ?
              AND name IS NOT NULL
        """

        params: list[Any] = [
            lat - delta,
            lat + delta,
            lon - delta,
            lon + delta,
        ]

        if category:
            query += " AND cat = ?"
            params.append(category)

        query += " LIMIT 50"

        cursor.execute(query, params)
        pois = cursor.fetchall()
        conn.close()

        results = []

        for name, poi_lat, poi_lon, cat, subcat in pois:
            results.append(
                {
                    "name": name,
                    "lat": poi_lat,
                    "lon": poi_lon,
                    "category": cat,
                    "subcategory": subcat,
                }
            )

        return {
            "status": "success",
            "center": {
                "lat": lat,
                "lon": lon,
            },
            "radius_km": radius,
            "count": len(results),
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Nearby search error: {exc}",
        ) from exc


@router.get("/status")
async def routing_status() -> dict[str, Any]:
    """
    وضعیت سرویس مسیریابی.
    """

    return {
        "status": "active",
        "service": "routing",
        "provider": "osrm",
        "base_url": osrm_service.base_url,
    }
