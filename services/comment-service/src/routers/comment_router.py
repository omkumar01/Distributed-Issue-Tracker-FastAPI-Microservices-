"""
REST API endpoints for comments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.database import database
from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from src.repositories.comment_repository import CommentRepository
from src.services.comment_service import CommentService
from src.events.publisher import get_publisher

router = APIRouter()

async def get_comment_service(session: AsyncSession = Depends(database.get_session)):
    """Dependency injection for CommentService."""
    repository = CommentRepository(session)
    publisher = get_publisher()
    return CommentService(repository, publisher)

# Mock user for testing without full auth
async def get_current_user():
    return UUID("00000000-0000-0000-0000-000000000001")


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    current_user: UUID = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    """Create a new comment."""
    return await service.create_comment(comment, current_user)


@router.get("/issue/{issue_id}", response_model=List[CommentResponse])
async def get_issue_comments(
    issue_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: CommentService = Depends(get_comment_service)
):
    """Get all comments for a specific issue."""
    return await service.get_comments_by_issue(issue_id, skip, limit)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    comment_update: CommentUpdate,
    current_user: UUID = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    """Update an existing comment."""
    return await service.update_comment(comment_id, comment_update, current_user)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    current_user: UUID = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    """Delete a comment."""
    await service.delete_comment(comment_id, current_user)
    return None
