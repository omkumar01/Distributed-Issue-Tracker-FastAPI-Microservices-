"""
Common schemas and models used across services.
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


# Enums
class IssueStatus(str, Enum):
    """Issue status enum."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"


class IssuePriority(str, Enum):
    """Issue priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class IssueAssignment(str, Enum):
    """Issue assignment status."""
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"


# Common Response Models
class BaseResponse(BaseModel):
    """Base response model."""
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    status_code: int


class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    total: int
    items: List[dict]
    skip: int
    limit: int


# User Models
class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """User model in database."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Project Models
class ProjectBase(BaseModel):
    """Base project model."""
    name: str
    description: Optional[str] = None
    key: str  # Project key like PROJ


class ProjectCreate(ProjectBase):
    """Project creation model."""
    owner_id: UUID


class ProjectUpdate(BaseModel):
    """Project update model."""
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response model."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Issue Models
class IssueBase(BaseModel):
    """Base issue model."""
    title: str
    description: Optional[str] = None
    status: IssueStatus = IssueStatus.TODO
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: Optional[UUID] = None


class IssueCreate(IssueBase):
    """Issue creation model."""
    project_id: UUID
    creator_id: UUID


class IssueUpdate(BaseModel):
    """Issue update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[UUID] = None


class IssueResponse(IssueBase):
    """Issue response model."""
    id: UUID
    project_id: UUID
    creator_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Comment Models
class CommentBase(BaseModel):
    """Base comment model."""
    content: str
    mentions: Optional[List[UUID]] = None


class CommentCreate(CommentBase):
    """Comment creation model."""
    issue_id: UUID
    author_id: UUID


class CommentUpdate(BaseModel):
    """Comment update model."""
    content: str


class CommentResponse(CommentBase):
    """Comment response model."""
    id: UUID
    issue_id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Auth Models
class TokenData(BaseModel):
    """JWT token data."""
    user_id: UUID
    email: str
    username: str
    scopes: List[str] = []


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class RegisterRequest(UserCreate):
    """User registration request model."""
    pass
