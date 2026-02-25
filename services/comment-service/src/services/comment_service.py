"""
Business logic for managing comments.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.repositories.comment_repository import CommentRepository
from src.schemas.comment import CommentCreate, CommentUpdate
from src.models.comment import CommentModel
from src.events.publisher import EventPublisher
from shared.events.schemas import CommentCreated, CommentUpdated, CommentDeleted


class CommentService:
    """Service handling comment business logic and event publishing."""
    
    def __init__(self, repository: CommentRepository, publisher: EventPublisher):
        self.repository = repository
        self.publisher = publisher
        
    async def create_comment(self, comment_create: CommentCreate, author_id: UUID) -> CommentModel:
        """Create a new comment and publish event."""
        comment = await self.repository.create(comment_create, author_id)
        
        # Publish event
        event = CommentCreated(
            comment_id=comment.id,
            issue_id=comment.issue_id,
            author_id=comment.author_id,
            content=comment.content,
            mentions=comment.mentions,
            service="comment-service"
        )
        self.publisher.publish(event)
        
        return comment
        
    async def get_comments_by_issue(self, issue_id: UUID, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        """Get all comments for an issue."""
        return await self.repository.get_by_issue_id(issue_id, skip, limit)
        
    async def update_comment(self, comment_id: UUID, comment_update: CommentUpdate, user_id: UUID) -> CommentModel:
        """Update an existing comment and publish event."""
        comment = await self.repository.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
            
        # Optional: check if user_id == comment.author_id. Let's assume user must be author.
        if comment.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this comment")
            
        updated_comment = await self.repository.update(comment, comment_update)
        
        # Publish event
        changes = {"content": comment_update.content}
        if comment_update.mentions is not None:
             changes["mentions"] = [str(m) for m in comment_update.mentions]
             
        event = CommentUpdated(
            comment_id=comment.id,
            issue_id=comment.issue_id,
            changes=changes,
            service="comment-service"
        )
        self.publisher.publish(event)
        
        return updated_comment
        
    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        """Delete a comment and publish event."""
        comment = await self.repository.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
            
        if comment.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")
            
        issue_id = comment.issue_id
        await self.repository.delete(comment_id)
        
        # Publish event
        event = CommentDeleted(
            comment_id=comment.id,
            issue_id=issue_id,
            service="comment-service"
        )
        self.publisher.publish(event)
        
        return True
