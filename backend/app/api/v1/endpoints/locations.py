"""Location API Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from loguru import logger
from app.core.location_service import get_location_service

router = APIRouter(prefix="/locations", tags=["locations"])

class LocationQuery(BaseModel):
    """Location Query Request"""
    latitude: float
    longitude: float
    service_type: Optional[str] = None
    radius_km: float = 5

@router.post("/nearest")
async def get_nearest_services(query: LocationQuery) -> dict:
    """Get nearest services to a location"""
    logger.info(f"🔍 Finding nearest services for ({query.latitude}, {query.longitude})")
    
    try:
        location_service = get_location_service()
        
        # Mock entities - in real implementation, fetch from database
        mock_entities = []
        
        nearest = location_service.find_nearest_services(
            mock_entities,
            query.latitude,
            query.longitude,
            query.service_type,
            query.radius_km
        )
        
        return {
            "status": "success",
            "query_location": {"latitude": query.latitude, "longitude": query.longitude},
            "services": nearest,
            "count": len(nearest)
        }
    
    except Exception as e:
        logger.error(f"Location query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_locations(query: str = Query(...), max_results: int = Query(10)):
    """Search for locations by name or description"""
    logger.info(f"🔎 Searching locations for: {query}")
    
    try:
        location_service = get_location_service()
        
        # Mock entities - in real implementation, fetch from database
        mock_entities = []
        
        results = location_service.get_location_suggestions(
            query,
            mock_entities,
            max_results
        )
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/route")
async def calculate_route(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    end_lat: float = Query(...),
    end_lng: float = Query(...)
):
    """Calculate route between two points"""
    logger.info(f"🗺️ Calculating route from ({start_lat}, {start_lng}) to ({end_lat}, {end_lng})")
    
    try:
        location_service = get_location_service()
        
        route = location_service.get_route_info(
            start_lat,
            start_lng,
            end_lat,
            end_lng
        )
        
        return {
            "status": "success",
            "route": route
        }
    
    except Exception as e:
        logger.error(f"Route calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
