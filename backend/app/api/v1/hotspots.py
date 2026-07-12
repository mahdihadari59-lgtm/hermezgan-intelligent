from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/hotspots", tags=["Hotspots"])

@router.get("/")
async def get_hotspots(type: Optional[str] = None):
    return {"hotspots": [], "total": 0}

@router.get("/nearby")
async def nearby_hotspots(latitude: float, longitude: float, radius: float = 5.0):
    return {"hotspots": [], "total": 0}
