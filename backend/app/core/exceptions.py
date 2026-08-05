# ============================================================
# exceptions.py - مدیریت استثناها و خطاهای سفارشی
# ============================================================
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================
# انواع خطاها
# ============================================================

class ErrorCode(Enum):
    """کدهای خطای استاندارد"""
    # خطاهای عمومی (1000-1999)
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    NOT_FOUND = 1002
    UNAUTHORIZED = 1003
    FORBIDDEN = 1004
    CONFLICT = 1005
    RATE_LIMIT = 1006
    SERVICE_UNAVAILABLE = 1007
    
    # خطاهای کاربر (2000-2999)
    USER_NOT_FOUND = 2000
    USER_ALREADY_EXISTS = 2001
    INVALID_CREDENTIALS = 2002
    USER_INACTIVE = 2003
    USER_NOT_VERIFIED = 2004
    INVALID_TOKEN = 2005
    TOKEN_EXPIRED = 2006
    TOKEN_REVOKED = 2007
    INVALID_PASSWORD = 2008
    WEAK_PASSWORD = 2009
    
    # خطاهای دیتابیس (3000-3999)
    DB_CONNECTION_ERROR = 3000
    DB_QUERY_ERROR = 3001
    DB_INTEGRITY_ERROR = 3002
    
    # خطاهای سرویس (4000-4999)
    SERVICE_ERROR = 4000
    EXTERNAL_API_ERROR = 4001
    CACHE_ERROR = 4002
    
    # خطاهای بوم‌شناسی (5000-5999)
    LOCATION_NOT_FOUND = 5000
    INVALID_COORDINATES = 5001
    NO_NEARBY_SERVICES = 5002
    
    # خطاهای چت‌بات (6000-6999)
    CHAT_ERROR = 6000
    INTENT_NOT_RECOGNIZED = 6001
    NLP_ERROR = 6002


# ============================================================
# کلاس‌های استثنا
# ============================================================

class BaseAppException(Exception):
    """
    کلاس پایه برای تمام استثناهای برنامه
    """
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.errors = errors or []
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای پاسخ API"""
        return {
            "success": False,
            "error": {
                "code": self.code.value,
                "code_name": self.code.name,
                "message": self.message,
                "status_code": self.status_code,
                "errors": self.errors,
                "details": self.details
            }
        }


# ============================================================
# استثناهای عمومی
# ============================================================

class ValidationError(BaseAppException):
    """خطای اعتبارسنجی"""
    def __init__(
        self,
        message: str = "خطا در اعتبارسنجی داده‌ها",
        errors: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details,
            errors=errors
        )


class NotFoundException(BaseAppException):
    """خطای یافت نشد - alias برای NotFoundError"""
    def __init__(
        self,
        message: str = "مورد درخواستی یافت نشد",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details
        )


class NotFoundError(NotFoundException):
    """خطای یافت نشد (همنام با NotFoundException)"""
    pass


class UnauthorizedError(BaseAppException):
    """خطای احراز هویت"""
    def __init__(
        self,
        message: str = "لطفاً وارد حساب کاربری خود شوید",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.UNAUTHORIZED,
            status_code=401,
            details=details
        )


class ForbiddenError(BaseAppException):
    """خطای دسترسی غیرمجاز"""
    def __init__(
        self,
        message: str = "شما دسترسی لازم را ندارید",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.FORBIDDEN,
            status_code=403,
            details=details
        )


class ConflictError(BaseAppException):
    """خطای تداخل"""
    def __init__(
        self,
        message: str = "منبع با داده‌های موجود تداخل دارد",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.CONFLICT,
            status_code=409,
            details=details
        )


class RateLimitError(BaseAppException):
    """خطای محدودیت نرخ درخواست"""
    def __init__(
        self,
        message: str = "تعداد درخواست‌ها بیش از حد مجاز است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT,
            status_code=429,
            details=details
        )


# ============================================================
# استثناهای کاربر
# ============================================================

class UserNotFoundError(BaseAppException):
    """کاربر یافت نشد"""
    def __init__(
        self,
        message: str = "کاربر یافت نشد",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.USER_NOT_FOUND,
            status_code=404,
            details=details
        )


class UserAlreadyExistsError(BaseAppException):
    """کاربر از قبل وجود دارد"""
    def __init__(
        self,
        message: str = "کاربر با این اطلاعات قبلاً ثبت شده است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.USER_ALREADY_EXISTS,
            status_code=409,
            details=details
        )


class InvalidCredentialsError(BaseAppException):
    """اطلاعات ورود نامعتبر"""
    def __init__(
        self,
        message: str = "نام کاربری یا رمز عبور نادرست است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_CREDENTIALS,
            status_code=401,
            details=details
        )


class UserInactiveError(BaseAppException):
    """کاربر غیرفعال است"""
    def __init__(
        self,
        message: str = "حساب کاربری شما غیرفعال است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.USER_INACTIVE,
            status_code=403,
            details=details
        )


class InvalidTokenError(BaseAppException):
    """توکن نامعتبر"""
    def __init__(
        self,
        message: str = "توکن نامعتبر است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_TOKEN,
            status_code=401,
            details=details
        )


class TokenExpiredError(BaseAppException):
    """توکن منقضی شده"""
    def __init__(
        self,
        message: str = "توکن منقضی شده است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.TOKEN_EXPIRED,
            status_code=401,
            details=details
        )


class WeakPasswordError(BaseAppException):
    """رمز عبور ضعیف"""
    def __init__(
        self,
        message: str = "رمز عبور ضعیف است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.WEAK_PASSWORD,
            status_code=400,
            details=details
        )


# ============================================================
# استثناهای دیتابیس
# ============================================================

class DatabaseError(BaseAppException):
    """خطای دیتابیس"""
    def __init__(
        self,
        message: str = "خطا در ارتباط با دیتابیس",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.DB_CONNECTION_ERROR,
            status_code=500,
            details=details
        )


class IntegrityError(BaseAppException):
    """خطای یکپارچگی دیتابیس"""
    def __init__(
        self,
        message: str = "خطا در یکپارچگی داده‌ها",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.DB_INTEGRITY_ERROR,
            status_code=409,
            details=details
        )


# ============================================================
# استثناهای سرویس‌ها
# ============================================================

class ServiceError(BaseAppException):
    """خطای سرویس"""
    def __init__(
        self,
        message: str = "خطا در سرویس",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.SERVICE_ERROR,
            status_code=500,
            details=details
        )


class ExternalAPIError(BaseAppException):
    """خطای API خارجی"""
    def __init__(
        self,
        message: str = "خطا در ارتباط با سرویس خارجی",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.EXTERNAL_API_ERROR,
            status_code=502,
            details=details
        )


# ============================================================
# استثناهای مکان‌یابی
# ============================================================

class LocationNotFoundError(BaseAppException):
    """مکان یافت نشد"""
    def __init__(
        self,
        message: str = "مکان مورد نظر یافت نشد",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.LOCATION_NOT_FOUND,
            status_code=404,
            details=details
        )


class InvalidCoordinatesError(BaseAppException):
    """مختصات نامعتبر"""
    def __init__(
        self,
        message: str = "مختصات جغرافیایی نامعتبر است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_COORDINATES,
            status_code=400,
            details=details
        )


# ============================================================
# استثناهای چت‌بات
# ============================================================

class ChatError(BaseAppException):
    """خطای چت‌بات"""
    def __init__(
        self,
        message: str = "خطا در پردازش چت",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.CHAT_ERROR,
            status_code=500,
            details=details
        )


class IntentNotRecognizedError(BaseAppException):
    """نیت تشخیص داده نشد"""
    def __init__(
        self,
        message: str = "نیت پیام تشخیص داده نشد",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INTENT_NOT_RECOGNIZED,
            status_code=400,
            details=details
        )


# ============================================================
# هندلرهای FastAPI
# ============================================================

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def setup_exception_handlers(app: FastAPI):
    """
    تنظیم هندلرهای استثنا برای FastAPI
    """

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        logger.error(f"خطای برنامه: {exc.message} (code={exc.code.value})")
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        error_map = {
            400: ("خطا در درخواست", ErrorCode.VALIDATION_ERROR),
            401: ("نیاز به احراز هویت", ErrorCode.UNAUTHORIZED),
            403: ("دسترسی غیرمجاز", ErrorCode.FORBIDDEN),
            404: ("منبع یافت نشد", ErrorCode.NOT_FOUND),
            405: ("متد غیرمجاز", ErrorCode.VALIDATION_ERROR),
            429: ("محدودیت نرخ درخواست", ErrorCode.RATE_LIMIT),
            500: ("خطای داخلی سرور", ErrorCode.UNKNOWN_ERROR),
            502: ("خطای سرویس", ErrorCode.SERVICE_ERROR),
        }
        message, code = error_map.get(exc.status_code, (exc.detail or "خطا", ErrorCode.UNKNOWN_ERROR))
        
        return JSONResponse(
            status_code=exc.status_code,
            content=BaseAppException(
                message=message,
                code=code,
                status_code=exc.status_code
            ).to_dict()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            msg = error["msg"]
            errors.append(f"{field}: {msg}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ValidationError(
                errors=errors,
                details={"validation_errors": exc.errors()}
            ).to_dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"خطای پیش‌بینی نشده: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=BaseAppException(
                message="خطای داخلی سرور رخ داده است",
                code=ErrorCode.UNKNOWN_ERROR,
                status_code=500
            ).to_dict()
        )


# ============================================================
# توابع کمکی
# ============================================================

def raise_if_not_found(obj: Any, message: str = "مورد یافت نشد"):
    """اگر شیء None باشد، خطای NotFoundError پرتاب می‌کند"""
    if obj is None:
        raise NotFoundError(message)
    return obj


def raise_if_not_authorized(condition: bool, message: str = "شما دسترسی لازم را ندارید"):
    """اگر شرط برقرار نباشد، خطای ForbiddenError پرتاب می‌کند"""
    if not condition:
        raise ForbiddenError(message)


def raise_if_validation_error(condition: bool, message: str = "خطا در اعتبارسنجی", errors: Optional[List[str]] = None):
    """اگر شرط برقرار باشد، خطای ValidationError پرتاب می‌کند"""
    if condition:
        raise ValidationError(message, errors)


# ============================================================
# Export کردن کلاس‌های اصلی
# ============================================================

__all__ = [
    # کلاس پایه
    'BaseAppException',
    
    # کدهای خطا
    'ErrorCode',
    
    # استثناهای عمومی
    'ValidationError',
    'NotFoundException',
    'NotFoundError',  # Alias
    'UnauthorizedError',
    'ForbiddenError',
    'ConflictError',
    'RateLimitError',
    
    # استثناهای کاربر
    'UserNotFoundError',
    'UserAlreadyExistsError',
    'InvalidCredentialsError',
    'UserInactiveError',
    'InvalidTokenError',
    'TokenExpiredError',
    'WeakPasswordError',
    
    # استثناهای دیتابیس
    'DatabaseError',
    'IntegrityError',
    
    # استثناهای سرویس
    'ServiceError',
    'ExternalAPIError',
    
    # استثناهای مکان‌یابی
    'LocationNotFoundError',
    'InvalidCoordinatesError',
    
    # استثناهای چت‌بات
    'ChatError',
    'IntentNotRecognizedError',
    
    # هندلرها
    'setup_exception_handlers',
    
    # توابع کمکی
    'raise_if_not_found',
    'raise_if_not_authorized',
    'raise_if_validation_error',
]


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("⚠️ تست مدیریت استثناها")
    print("=" * 60)

    # تست NotFoundException
    try:
        raise NotFoundException("منبع درخواستی یافت نشد", details={"resource": "user", "id": 123})
    except BaseAppException as e:
        print(f"\n❌ NotFoundException:")
        print(f"  پیام: {e.message}")
        print(f"  کد: {e.code.value} - {e.code.name}")
        print(f"  وضعیت: {e.status_code}")
        print(f"  جزئیات: {e.details}")
        print(f"  دیکشنری: {e.to_dict()}")

    # تست NotFoundError (همنام)
    try:
        raise NotFoundError("کاربر یافت نشد")
    except NotFoundException as e:
        print(f"\n❌ NotFoundError:")
        print(f"  پیام: {e.message}")
        print(f"  نوع: {type(e).__name__}")

    # تست سایر استثناها
    exceptions = [
        ValidationError(errors=["فیلد نام الزامی است"]),
        NotFoundException(details={"resource": "user"}),
        NotFoundError(details={"resource": "product"}),
        UnauthorizedError(),
        ForbiddenError(),
        ConflictError(),
        RateLimitError(),
        UserNotFoundError(),
        InvalidCredentialsError(),
        InvalidTokenError(),
        DatabaseError(),
        ChatError(),
        LocationNotFoundError(),
    ]

    print("\n📋 لیست استثناها:")
    for exc in exceptions:
        print(f"  {exc.__class__.__name__}: {exc.code.value} - {exc.status_code}")

    # تست توابع کمکی
    print("\n🛠️ تست توابع کمکی:")
    try:
        raise_if_not_found(None, "دیتا یافت نشد")
    except NotFoundError as e:
        print(f"  raise_if_not_found: {e.message}")

    try:
        raise_if_not_authorized(False, "دسترسی غیرمجاز")
    except ForbiddenError as e:
        print(f"  raise_if_not_authorized: {e.message}")

    print("\n✅ تست استثناها با موفقیت انجام شد!")
