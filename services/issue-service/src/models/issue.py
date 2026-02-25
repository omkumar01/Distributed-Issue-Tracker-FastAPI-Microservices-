"""
SQLAlchemy model for Issue.
"""

from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from shared.schemas import IssueStatus, IssuePriority
from src.models import Base

class IssueModel(Base):
    """
    Issue database model.
    """
    __tablename__ = "issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    status = Column(SAEnum(IssueStatus), default=IssueStatus.TODO, nullable=False, index=True)
    priority = Column(SAEnum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False, index=True)
    
    assignee_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status}')>"
