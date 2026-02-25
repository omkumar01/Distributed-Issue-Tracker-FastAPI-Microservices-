"""
Pydantic schemas for Comment.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CommentBase(BaseModel):
    """Base comment schema."""
    content: str = Field(..., description="The content of the comment")
    mentions: Optional[List[UUID]] = Field(default_factory=list, description="List of user UUIDs mentioned in the comment")

class CommentCreate(CommentBase):
    """Schema for creating a comment."""
    issue_id: UUID = Field(..., description="The ID of the issue the comment belongs to")

class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: str = Field(..., description="The revised content of the comment")
    mentions: Optional[List[UUID]] = Field(default=None, description="Updated list of user UUIDs mentioned")

class CommentResponse(CommentBase):
    """Schema for passing comment data in API responses."""
    id: UUID
    issue_id: UUID
    author_id: UUID
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
