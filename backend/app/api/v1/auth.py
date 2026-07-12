from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register")
async def register(data: RegisterRequest):
    return {"message": "ثبت‌نام موفق", "user": data.username}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    return {"access_token": "mock-token-123", "token_type": "bearer"}
