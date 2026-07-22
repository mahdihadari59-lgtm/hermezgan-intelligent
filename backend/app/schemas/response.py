from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')


class ResponseBase(BaseModel):
    """پاسخ پایه API"""
    success: bool = True
    message: str = "عملیات با موفقیت انجام شد"
    timestamp: datetime = datetime.utcnow()


class ResponseData(ResponseBase, Generic[T]):
    """پاسخ با داده"""
    data: Optional[T] = None


class ResponseList(ResponseBase, Generic[T]):
    """پاسخ با لیست داده‌ها"""
    data: List[T] = []
    total: int = 0
    page: int = 1
    limit: int = 100


class ErrorResponse(BaseModel):
    """پاسخ خطا"""
    success: bool = False
    message: str
    detail: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    status_code: int


class PaginationParams(BaseModel):
    """پارامترهای صفحه‌بندی"""
    page: int = 1
    limit: int = 100
    sort_by: Optional[str] = None
    sort_order: str = "desc"
