from __future__ import annotations
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.bandari import BandariDetectRequest, BandariDetectResponse, BandariStatsResponse, BandariTranslateRequest, BandariTranslateResponse
from app.services.bandari.database import get_db
from app.services.bandari.exceptions import BandariEngineError
from app.services.bandari.service import BandariServiceV6

router = APIRouter(prefix="/bandari/v2", tags=["Bandari"])

def get_service(db: AsyncSession = Depends(get_db)) -> BandariServiceV6:
    return BandariServiceV6(db)

@router.get("/health")
async def health(service: BandariServiceV6 = Depends(get_service)):
    try:
        stats = await service.stats()
        return {"status": "healthy", "engine": "python", "node_dependency": False, "data": stats}
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)})

@router.post("/translate", response_model=BandariTranslateResponse)
async def translate(request: BandariTranslateRequest, service: BandariServiceV6 = Depends(get_service)):
    try:
        result = await service.translate(request.text, request.source, request.target)
        return {"success": True, "data": {"translation": result.translation, "normalized_text": result.normalized_text, **result.raw}}
    except BandariEngineError as exc:
        raise HTTPException(status_code=400, detail=exc.to_dict())

@router.post("/detect", response_model=BandariDetectResponse)
async def detect(request: BandariDetectRequest, service: BandariServiceV6 = Depends(get_service)):
    try:
        result = await service.detect(request.text)
        return {"success": True, "data": {"dialect": result.dialect, "confidence": result.confidence, "language": result.language, **result.raw}}
    except BandariEngineError as exc:
        raise HTTPException(status_code=400, detail=exc.to_dict())

@router.get("/search")
async def search_words(q: str = Query(..., min_length=2, max_length=200), dialect: str = Query("ban", pattern=r"^(ban|min|qes|jas|lan|bas|kha|rud|sir)$"), limit: int = Query(20, ge=1, le=100), service: BandariServiceV6 = Depends(get_service)):
    return {"success": True, "data": {"query": q, "dialect": dialect, "results": await service.search_word(q, dialect, limit)}}

@router.get("/categories")
async def categories(service: BandariServiceV6 = Depends(get_service)):
    return {"success": True, "data": {"categories": await service.categories()}}

@router.get("/knowledge")
async def knowledge(category: Optional[str] = None, region: Optional[str] = None, limit: int = Query(50, ge=1, le=200), service: BandariServiceV6 = Depends(get_service)):
    rows = await service.knowledge(category, region, limit)
    return {"success": True, "data": {"count": len(rows), "results": rows}}

@router.get("/stats", response_model=BandariStatsResponse)
async def stats(service: BandariServiceV6 = Depends(get_service)):
    return {"success": True, "data": await service.stats()}
