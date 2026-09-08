# ============================================================
# base.py - کلاس‌های پایه API
# ============================================================

class ValidationError(Exception):
    """خطای اعتبارسنجی"""
    pass

class NotFoundError(Exception):
    """خطای یافت نشد"""
    pass

class ConflictError(Exception):
    """خطای تداخل"""
    pass

class UnauthorizedError(Exception):
    """خطای احراز هویت"""
    pass

class ForbiddenError(Exception):
    """خطای دسترسی غیرمجاز"""
    pass
