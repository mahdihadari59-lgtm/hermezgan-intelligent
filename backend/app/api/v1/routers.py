from fastapi import APIRouter, Query
from geo.spatial_api import SpatialDB
from app.api.tourism import TourismAPI
from app.api.hospitals import HospitalAPI
from app.api.fuel import FuelAPI
from app.api.poi import PoiAPI

router = APIRouter()

db = SpatialDB("geo.db")


@router.get("/ping")
async def ping():
    return {"status": "pong"}


@router.get("/map/tourism")
def tourism(
    north: float,
    south: float,
    east: float,
    west: float,
    limit: int = Query(500),
):
    return TourismAPI.list_bbox(
        db,
        north=north,
        south=south,
        east=east,
        west=west,
        limit=limit,
    )


@router.get("/map/hospitals")
def hospitals(
    north: float,
    south: float,
    east: float,
    west: float,
):
    return HospitalAPI.list_bbox(
        db,
        north=north,
        south=south,
        east=east,
        west=west,
    )


@router.get("/map/fuel")
def fuel(
    north: float,
    south: float,
    east: float,
    west: float,
):
    return FuelAPI.list_bbox(
        db,
        north=north,
        south=south,
        east=east,
        west=west,
    )


@router.get("/map/poi")
def poi(
    north: float,
    south: float,
    east: float,
    west: float,
):
    return PoiAPI.list_bbox(
        db,
        north=north,
        south=south,
        east=east,
        west=west,
    )
