# ============================================================
# schemas/__init__.py - صادرات کلاس‌های Schema
# ============================================================

# User Schemas
from .user import (
    UserRegister,
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    ChangePassword,
    UserResponse,
    UserProfile,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)

# Location Schemas
from .location import (
    Coordinates,
    ServiceBase,
    ServiceCreate,
    ServiceResponse,
    ServiceSearchParams,
)

# Camera Schemas
from .camera import (
    CameraBase,
    CameraCreate,
    CameraResponse,
    CameraFilterParams,
)

# Hotspot Schemas
from .hotspot import (
    HotspotBase,
    HotspotCreate,
    HotspotResponse,
    HotspotFilterParams,
)

# Chat Schemas (اگر وجود دارد)
try:
    from .chat import (
        ChatMessageRequest,
        ChatMessageResponse,
        ConversationResponse,
    )
except ImportError:
    pass

__all__ = [
    'UserRegister',
    # User
    'UserBase',
    'UserCreate',
    'UserLogin',
    'UserUpdate',
    'ChangePassword',
    'UserResponse',
    'UserProfile',
    'TokenResponse',
    'RefreshTokenRequest',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    # Location
    'Coordinates',
    'ServiceBase',
    'ServiceCreate',
    'ServiceResponse',
    'ServiceSearchParams',
    # Camera
    'CameraBase',
    'CameraCreate',
    'CameraResponse',
    'CameraFilterParams',
    # Hotspot
    'HotspotBase',
    'HotspotCreate',
    'HotspotResponse',
    'HotspotFilterParams',
]
