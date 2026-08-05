from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
import os

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.dependencies.database import get_db
from app.schemas.user import TokenData

# تنظیمات JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"

security = HTTPBearer()


def verify_token(token: str) -> Optional[TokenData]:
    """
    تأیید و تفسیر توکن JWT

    Args:
        token: توکن JWT

    Returns:
        TokenData: اطلاعات کاربر یا None در صورت خطا
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        email: str = payload.get("email")
        is_admin: bool = payload.get("is_admin", False)

        if user_id is None:
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            is_admin=is_admin
        )
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    دریافت کاربر فعلی از توکن

    Returns:
        User: کاربر احراز هویت شده

    Raises:
        HTTPException: اگر توکن نامعتبر باشد یا کاربر یافت نشود
    """
    token = credentials.credentials
    token_data = verify_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(token_data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کاربر یافت نشد",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال است"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    دریافت کاربر فعلی فعال

    Returns:
        User: کاربر فعال

    Raises:
        HTTPException: اگر کاربر غیرفعال باشد
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال است"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    دریافت کاربر ادمین فعلی

    Returns:
        User: کاربر ادمین

    Raises:
        HTTPException: اگر کاربر ادمین نباشد
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی ادمین لازم است"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    دریافت کاربر تأیید شده فعلی

    Returns:
        User: کاربر تأیید شده

    Raises:
        HTTPException: اگر کاربر تأیید نشده باشد
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری تأیید نشده است"
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    دریافت کاربر اختیاری (بدون خطا در صورت نبودن)

    Returns:
        Optional[User]: کاربر در صورت وجود، در غیر این صورت None
    """
    if not credentials:
        return None

    token = credentials.credentials
    token_data = verify_token(token)

    if not token_data:
        return None

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(token_data.user_id)

    if not user or not user.is_active:
        return None

    return user
