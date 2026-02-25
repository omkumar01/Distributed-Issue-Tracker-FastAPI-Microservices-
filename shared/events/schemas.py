"""
Domain event schemas for event-driven architecture.
All events are serialized as JSON and published via RabbitMQ.
"""

from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base class for all domain events."""
    event_id: str = Field(default_factory=lambda: str(UUID))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service: str
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "user.created",
                "timestamp": "2024-02-13T10:30:00Z",
                "service": "user-service",
                "correlation_id": "req-123",
                "causation_id": "event-456"
            }
        }


# User Events
class UserCreated(BaseEvent):
    """Published when a new user is created."""
    event_type: str = "user.created"
    user_id: UUID
    email: str
    username: str
    data: Dict[str, Any] = Field(default_factory=dict)


class UserUpdated(BaseEvent):
    """Published when a user is updated."""
    event_type: str = "user.updated"
    user_id: UUID
    changes: Dict[str, Any]


class UserDeleted(BaseEvent):
    """Published when a user is deleted."""
    event_type: str = "user.deleted"
    user_id: UUID


# Project Events
class ProjectCreated(BaseEvent):
    """Published when a new project is created."""
    event_type: str = "project.created"
    project_id: UUID
    name: str
    owner_id: UUID
    data: Dict[str, Any] = Field(default_factory=dict)


class ProjectUpdated(BaseEvent):
    """Published when a project is updated."""
    event_type: str = "project.updated"
    project_id: UUID
    changes: Dict[str, Any]


class ProjectDeleted(BaseEvent):
    """Published when a project is deleted."""
    event_type: str = "project.deleted"
    project_id: UUID


# Issue Events
class IssueCreated(BaseEvent):
    """Published when a new issue is created."""
    event_type: str = "issue.created"
    issue_id: UUID
    project_id: UUID
    title: str
    creator_id: UUID
    data: Dict[str, Any] = Field(default_factory=dict)


class IssueUpdated(BaseEvent):
    """Published when an issue is updated."""
    event_type: str = "issue.updated"
    issue_id: UUID
    project_id: UUID
    changes: Dict[str, Any]


class IssueStatusChanged(BaseEvent):
    """Published when issue status changes."""
    event_type: str = "issue.status_changed"
    issue_id: UUID
    project_id: UUID
    old_status: str
    new_status: str
    changed_by: UUID


class IssueDeleted(BaseEvent):
    """Published when an issue is deleted."""
    event_type: str = "issue.deleted"
    issue_id: UUID
    project_id: UUID


# Comment Events
class CommentCreated(BaseEvent):
    """Published when a comment is created."""
    event_type: str = "comment.created"
    comment_id: UUID
    issue_id: UUID
    author_id: UUID
    content: str
    mentions: Optional[list[UUID]] = None


class CommentUpdated(BaseEvent):
    """Published when a comment is updated."""
    event_type: str = "comment.updated"
    comment_id: UUID
    issue_id: UUID
    changes: Dict[str, Any]


class CommentDeleted(BaseEvent):
    """Published when a comment is deleted."""
    event_type: str = "comment.deleted"
    comment_id: UUID
    issue_id: UUID


# Notification Events
class NotificationRequired(BaseEvent):
    """Generic event for triggering notifications."""
    event_type: str = "notification.required"
    user_id: UUID
    notification_type: str  # email, in_app, webhook
    subject: str
    body: str
    data: Dict[str, Any] = Field(default_factory=dict)


# Audit Events
class AuditEvent(BaseEvent):
    """Published for all significant operations for compliance."""
    event_type: str = "audit.event"
    actor_id: UUID
    action: str
    resource_id: UUID
    resource_type: str
    changes: Optional[Dict[str, Any]] = None
    status: str = "success"  # success, failure
