# ============================================================
# base.py - کلاس‌های پایه API
# ============================================================

class ValidationError(Exception):
    """خطای اعتبارسنجی"""
    def __init__(self, message="خطا در اعتبارسنجی", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(Exception):
    """خطای یافت نشد"""
    def __init__(self, message="مورد یافت نشد", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ConflictError(Exception):
    """خطای تداخل"""
    def __init__(self, message="تداخل در داده‌ها", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class UnauthorizedError(Exception):
    """خطای احراز هویت"""
    def __init__(self, message="نیاز به احراز هویت", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ForbiddenError(Exception):
    """خطای دسترسی غیرمجاز"""
    def __init__(self, message="دسترسی غیرمجاز", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class BadRequestError(Exception):
    """خطای درخواست نامعتبر"""
    def __init__(self, message="درخواست نامعتبر", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DatabaseError(Exception):
    """خطای دیتابیس"""
    def __init__(self, message="خطا در دیتابیس", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)
