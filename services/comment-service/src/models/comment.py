"""
SQLAlchemy model for Comment.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid

from src.models import Base

class CommentModel(Base):
    """
    Comment database model.
    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    mentions = Column(ARRAY(UUID(as_uuid=True)), nullable=True, default=list)
    
    is_edited = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Comment(id={self.id}, issue_id={self.issue_id}, author_id={self.author_id})>"
