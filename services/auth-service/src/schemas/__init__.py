"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema."""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class TokenData(BaseModel):
    """Token data schema."""
    user_id: str
    email: str
    token_type: str


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8)


class OAuthCallbackSchema(BaseModel):
    """OAuth callback schema."""
    provider: str
    code: str
    state: Optional[str] = None


class OAuthTokenResponse(BaseModel):
    """OAuth token response schema."""
    access_token_object: TokenResponse
    user: UserResponse


class ErrorResponse(BaseModel):
    """Error response schema."""
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
