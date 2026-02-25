"""
Issue Repository.
Handles database interactions for Issue entity.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.models.issue import IssueModel
from shared.schemas import IssueCreate, IssueUpdate

class IssueRepository:
    """Repository for Issue data access."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, issue_create: IssueCreate) -> IssueModel:
        """Create a new issue."""
        db_issue = IssueModel(
            project_id=issue_create.project_id,
            creator_id=issue_create.creator_id,
            title=issue_create.title,
            description=issue_create.description,
            status=issue_create.status,
            priority=issue_create.priority,
            assignee_id=issue_create.assignee_id
        )
        self.db.add(db_issue)
        await self.db.commit()
        await self.db.refresh(db_issue)
        return db_issue

    async def get(self, issue_id: UUID) -> Optional[IssueModel]:
        """Get issue by ID."""
        result = await self.db.execute(select(IssueModel).filter(IssueModel.id == issue_id))
        return result.scalars().first()

    async def list(self, skip: int = 0, limit: int = 10) -> List[IssueModel]:
        """List issues with pagination."""
        result = await self.db.execute(
            select(IssueModel)
            .order_by(desc(IssueModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(self, issue_id: UUID, issue_update: IssueUpdate) -> Optional[IssueModel]:
        """Update an issue."""
        db_issue = await self.get(issue_id)
        if not db_issue:
            return None
        
        update_data = issue_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_issue, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_issue)
        return db_issue

    async def delete(self, issue_id: UUID) -> bool:
        """Delete an issue."""
        db_issue = await self.get(issue_id)
        if not db_issue:
            return False
            
        await self.db.delete(db_issue)
        await self.db.commit()
        return True
