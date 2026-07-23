from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from pydantic import ValidationInfo


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="نام کاربری")
    email: EmailStr = Field(..., description="ایمیل")
    full_name: str = Field(..., min_length=2, max_length=100, description="نام کامل")
    phone: Optional[str] = Field(None, pattern=r"^09\d{9}$", description="شماره تلفن")
    bio: Optional[str] = Field(None, max_length=500, description="بیوگرافی")
    avatar_url: Optional[str] = Field(None, max_length=500, description="آواتار")

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="رمز عبور")
    confirm_password: str = Field(..., description="تکرار رمز عبور")

    @field_validator('confirm_password')
    def passwords_match(cls, v, info: ValidationInfo):
        """بررسی تطابق رمز عبور"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('رمز عبور و تکرار آن مطابقت ندارند')
        return v


class UserLogin(BaseModel):
    username: str = Field(..., description="نام کاربری یا ایمیل")
    password: str = Field(..., min_length=8, description="رمز عبور")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^09\d{9}$")
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=8, description="رمز عبور فعلی")
    new_password: str = Field(..., min_length=8, description="رمز عبور جدید")
    confirm_new_password: str = Field(..., description="تکرار رمز عبور جدید")

    @field_validator('confirm_new_password')
    def passwords_match(cls, v, info: ValidationInfo):
        """بررسی تطابق رمز عبور جدید"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('رمز عبور جدید و تکرار آن مطابقت ندارند')
        return v

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    region: Optional[str] = None
    address: Optional[str] = None
    language: Optional[str] = "fa"
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh Token")

    model_config = ConfigDict(from_attributes=True)


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="ایمیل")

    model_config = ConfigDict(from_attributes=True)


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="توکن بازیابی")
    new_password: str = Field(..., min_length=8, description="رمز عبور جدید")
    confirm_password: str = Field(..., description="تکرار رمز عبور جدید")

    @field_validator('confirm_password')
    def passwords_match(cls, v, info: ValidationInfo):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('رمز عبور و تکرار آن مطابقت ندارند')
        return v

    model_config = ConfigDict(from_attributes=True)


class UserRegister(UserCreate):
    """Schema برای ثبت‌نام کاربر (همنام با UserCreate)"""
    pass
