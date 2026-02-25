"""
Repository for managing comments in the database.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.models.comment import CommentModel
from src.schemas.comment import CommentCreate, CommentUpdate

class CommentRepository:
    """Repository handling CRUD operations for CommentModel."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, comment_id: UUID) -> Optional[CommentModel]:
        """Get comment by ID."""
        result = await self.session.execute(
            select(CommentModel).where(CommentModel.id == comment_id)
        )
        return result.scalars().first()
        
    async def get_by_issue_id(self, issue_id: UUID, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        """Get all comments for an issue, ordered by creation time."""
        result = await self.session.execute(
            select(CommentModel)
            .where(CommentModel.issue_id == issue_id)
            .order_by(CommentModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
        
    async def create(self, comment: CommentCreate, author_id: UUID) -> CommentModel:
        """Create a new comment."""
        db_comment = CommentModel(
            issue_id=comment.issue_id,
            author_id=author_id,
            content=comment.content,
            mentions=comment.mentions or []
        )
        self.session.add(db_comment)
        await self.session.commit()
        await self.session.refresh(db_comment)
        return db_comment
        
    async def update(self, db_comment: CommentModel, update_data: CommentUpdate) -> CommentModel:
        """Update an existing comment."""
        db_comment.content = update_data.content
        db_comment.is_edited = True
        if update_data.mentions is not None:
            db_comment.mentions = update_data.mentions
            
        await self.session.commit()
        await self.session.refresh(db_comment)
        return db_comment
        
    async def delete(self, comment_id: UUID) -> bool:
        """Delete a comment."""
        result = await self.session.execute(
            delete(CommentModel).where(CommentModel.id == comment_id)
        )
        await self.session.commit()
        return result.rowcount > 0
