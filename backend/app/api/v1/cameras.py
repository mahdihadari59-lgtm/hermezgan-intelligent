from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.get("/")
async def get_cameras(region: Optional[str] = None, status: Optional[str] = None):
    return {"cameras": [], "total": 0}

@router.post("/{camera_id}/report")
async def report_camera_issue(camera_id: str, issue: str):
    return {"status": "reported", "id": camera_id}
