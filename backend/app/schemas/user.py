from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """کلاس پایه کاربر"""
    username: str = Field(..., min_length=3, max_length=50, description="نام کاربری")
    email: EmailStr = Field(..., description="ایمیل")
    full_name: Optional[str] = Field(None, max_length=100, description="نام کامل")
    phone: Optional[str] = Field(None, regex=r"^09\d{9}$", description="شماره تلفن")


class UserCreate(UserBase):
    """ایجاد کاربر جدید"""
    password: str = Field(..., min_length=8, description="رمز عبور")
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('رمز عبور باید حداقل شامل یک عدد باشد')
        if not any(c.isupper() for c in v):
            raise ValueError('رمز عبور باید حداقل شامل یک حرف بزرگ باشد')
        return v


class UserUpdate(BaseModel):
    """به‌روزرسانی کاربر"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^09\d{9}$")
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """پاسخ کاربر"""
    id: int
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    region: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """ورود کاربر"""
    username: str = Field(..., description="نام کاربری یا ایمیل")
    password: str = Field(..., description="رمز عبور")


class UserRegister(UserCreate):
    """ثبت‌نام کاربر"""
    confirm_password: str = Field(..., description="تکرار رمز عبور")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('رمز عبور و تکرار آن مطابقت ندارند')
        return v


class TokenResponse(BaseModel):
    """پاسخ توکن"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class RefreshTokenRequest(BaseModel):
    """درخواست Refresh Token"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """تغییر رمز عبور"""
    old_password: str = Field(..., description="رمز عبور فعلی")
    new_password: str = Field(..., min_length=8, description="رمز عبور جدید")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('رمز عبور باید حداقل شامل یک عدد باشد')
        if not any(c.isupper() for c in v):
            raise ValueError('رمز عبور باید حداقل شامل یک حرف بزرگ باشد')
        return v
