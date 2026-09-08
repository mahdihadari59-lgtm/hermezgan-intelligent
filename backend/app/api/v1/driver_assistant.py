from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel, Field

from app.services.driver_assistant.exceptions import (
    DestinationNotFoundException,
    SessionNotFoundException,
)
from app.services.driver_assistant.service import driver_assistant_service


router = APIRouter(
    prefix="/driver-assistant",
    tags=["Driver Assistant"],
)


class StartRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    user_id: str = "anonymous"
    latitude: float
    longitude: float
    profile: str = "driving"


class LocationRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None


class CommandRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)


class StopRequest(BaseModel):
    session_id: str = Field(..., min_length=1)


@router.post("/start")
async def start_driver_assistant(
    request: StartRequest,
) -> dict[str, Any]:
    try:
        return await driver_assistant_service.start(
            session_id=request.session_id,
            user_id=request.user_id,
            latitude=request.latitude,
            longitude=request.longitude,
            profile=request.profile,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/update-location")
async def update_driver_location(
    request: LocationRequest,
) -> dict[str, Any]:
    try:
        return await driver_assistant_service.update_location(
            session_id=request.session_id,
            latitude=request.latitude,
            longitude=request.longitude,
            accuracy=request.accuracy,
            heading=request.heading,
            speed=request.speed,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except SessionNotFoundException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post("/command")
async def driver_command(
    request: CommandRequest,
) -> dict[str, Any]:
    try:
        return await driver_assistant_service.command(
            session_id=request.session_id,
            text=request.text,
        )
    except SessionNotFoundException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DestinationNotFoundException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"خطای دستیار راننده: {exc}",
        ) from exc


@router.post("/stop")
async def stop_driver_assistant(
    request: StopRequest,
) -> dict[str, Any]:
    return await driver_assistant_service.stop(
        request.session_id
    )


@router.get("/status")
async def driver_assistant_status(
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    return await driver_assistant_service.status(session_id)


@router.websocket("/ws/{session_id}")
async def driver_websocket(
    websocket: WebSocket,
    session_id: str,
):
    await driver_assistant_service.ws.connect(
        websocket,
        session_id,
    )

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "location":
                result = await driver_assistant_service.update_location(
                    session_id=session_id,
                    latitude=float(data["lat"]),
                    longitude=float(data["lon"]),
                    accuracy=data.get("accuracy"),
                    heading=data.get("heading"),
                    speed=data.get("speed"),
                )

                await websocket.send_json(
                    {
                        "type": "location_response",
                        "data": result,
                    }
                )

            elif msg_type == "command":
                result = await driver_assistant_service.command(
                    session_id=session_id,
                    text=str(data["text"]),
                )

                await websocket.send_json(
                    {
                        "type": "command_response",
                        "data": result,
                    }
                )

            elif msg_type == "ping":
                await websocket.send_json(
                    {
                        "type": "pong"
                    }
                )

    except Exception:
        pass
    finally:
        await driver_assistant_service.ws.disconnect(
            websocket,
            session_id,
        )
