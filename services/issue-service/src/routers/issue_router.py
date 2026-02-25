"""Issue routers module."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from src.database import database
from src.repositories.issue_repository import IssueRepository
from src.services.issue_service import IssueService
from src.events.publisher import get_publisher, EventPublisher
from shared.schemas import (
    IssueCreate, 
    IssueResponse, 
    IssueUpdate, 
    IssueStatus, 
    PaginatedResponse,
    PaginationParams
)

router = APIRouter()

async def get_service(db: AsyncSession = Depends(database.get_session)) -> IssueService:
    """Dependency to get issue service."""
    repo = IssueRepository(db)
    publisher = get_publisher()
    return IssueService(repo, publisher)


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_create: IssueCreate,
    service: IssueService = Depends(get_service)
):
    """Create a new issue."""
    return await service.create_issue(issue_create)


@router.get("", response_model=List[IssueResponse])
async def list_issues(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: IssueService = Depends(get_service)
):
    """List all issues."""
    return await service.list_issues(skip=skip, limit=limit)


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: UUID,
    service: IssueService = Depends(get_service)
):
    """Get issue by ID."""
    issue = await service.get_issue(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    return issue


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: UUID,
    issue_update: IssueUpdate,
    service: IssueService = Depends(get_service)
):
    """Update issue."""
    try:
        updated_issue = await service.update_issue(issue_id, issue_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not updated_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    return updated_issue


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: UUID,
    service: IssueService = Depends(get_service)
):
    """Delete issue."""
    success = await service.delete_issue(issue_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    return None


@router.post("/{issue_id}/transition", response_model=IssueResponse)
async def transition_issue(
    issue_id: UUID,
    new_status: IssueStatus,
    service: IssueService = Depends(get_service)
):
    """Transition issue status."""
    update_data = IssueUpdate(status=new_status)
    try:
        updated_issue = await service.update_issue(issue_id, update_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    if not updated_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    return updated_issue
