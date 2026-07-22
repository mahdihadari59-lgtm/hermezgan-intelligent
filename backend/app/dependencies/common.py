from fastapi import Query, Request, HTTPException, status
from typing import Optional, List
import re

from app.schemas.response import PaginationParams


def get_pagination(
    page: int = Query(1, ge=1, description="شماره صفحه"),
    limit: int = Query(100, ge=1, le=1000, description="تعداد آیتم در هر صفحه"),
    sort_by: Optional[str] = Query(None, description="فیلد مرتب‌سازی"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="ترتیب مرتب‌سازی")
) -> PaginationParams:
    """
    دریافت پارامترهای صفحه‌بندی

    Returns:
        PaginationParams: پارامترهای صفحه‌بندی
    """
    return PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


def get_client_ip(request: Request) -> str:
    """
    دریافت IP کاربر

    Returns:
        str: IP کاربر
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    دریافت User-Agent

    Returns:
        str: User-Agent
    """
    return request.headers.get("User-Agent", "unknown")


def validate_coordinates(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="عرض جغرافیایی"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="طول جغرافیایی")
) -> tuple:
    """
    اعتبارسنجی مختصات

    Returns:
        tuple: (latitude, longitude) در صورت وجود هر دو

    Raises:
        HTTPException: اگر فقط یکی از مختصات وجود داشته باشد
    """
    if latitude is not None and longitude is not None:
        return latitude, longitude

    if latitude is not None or longitude is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هر دو مختصات باید ارائه شوند"
        )

    return None, None


def parse_search_query(query: str) -> List[str]:
    """
    تجزیه عبارت جستجو به کلمات کلیدی

    Args:
        query: عبارت جستجو

    Returns:
        List[str]: لیست کلمات کلیدی
    """
    # حذف کاراکترهای خاص
    cleaned = re.sub(r'[^\w\s]', ' ', query)
    # جداسازی کلمات و حذف تکراری‌ها
    words = cleaned.split()
    return list(set(words))[:10]  # حداکثر ۱۰ کلمه
