"""Audit Service - Event consumer handler tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.services.event_consumer import AuditEventConsumer


@pytest.fixture
def consumer():
    """Create AuditEventConsumer with mocked repo and settings."""
    mock_repo = AsyncMock()
    mock_repo.create = AsyncMock()

    mock_settings = MagicMock()
    mock_settings.RABBITMQ_HOST = "localhost"
    mock_settings.RABBITMQ_PORT = 5672
    mock_settings.RABBITMQ_USER = "guest"
    mock_settings.RABBITMQ_PASSWORD = "guest"

    return AuditEventConsumer(mock_repo, mock_settings)


# ─── User Events ───


@pytest.mark.asyncio
class TestUserEventHandlers:
    """Test user event handlers."""

    async def test_handle_user_created(self, consumer):
        event = {
            "event_type": "user.created",
            "user_id": str(uuid4()),
            "data": {"email": "test@example.com", "username": "testuser"},
            "service": "user-service",
        }
        await consumer.handle_user_created(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "create"
        assert call_args.resource_type == "user"

    async def test_handle_user_updated(self, consumer):
        event = {
            "event_type": "user.updated",
            "user_id": str(uuid4()),
            "changes": {"email": {"old": "a@b.com", "new": "c@d.com"}},
            "service": "user-service",
        }
        await consumer.handle_user_updated(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "update"

    async def test_handle_user_deleted(self, consumer):
        event = {
            "event_type": "user.deleted",
            "user_id": str(uuid4()),
            "service": "user-service",
        }
        await consumer.handle_user_deleted(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "delete"
        assert call_args.resource_type == "user"


# ─── Project Events ───


@pytest.mark.asyncio
class TestProjectEventHandlers:
    """Test project event handlers."""

    async def test_handle_project_created(self, consumer):
        project_id = str(uuid4())
        event = {
            "event_type": "project.created",
            "owner_id": str(uuid4()),
            "project_id": project_id,
            "data": {"name": "My Project"},
            "service": "project-service",
        }
        await consumer.handle_project_created(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "create"
        assert call_args.resource_type == "project"
        assert str(call_args.project_id) == project_id

    async def test_handle_project_updated(self, consumer):
        event = {
            "event_type": "project.updated",
            "actor_id": str(uuid4()),
            "project_id": str(uuid4()),
            "changes": {"name": {"old": "A", "new": "B"}},
            "service": "project-service",
        }
        await consumer.handle_project_updated(event)
        consumer.repo.create.assert_awaited_once()

    async def test_handle_project_deleted(self, consumer):
        event = {
            "event_type": "project.deleted",
            "actor_id": str(uuid4()),
            "project_id": str(uuid4()),
            "service": "project-service",
        }
        await consumer.handle_project_deleted(event)

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "delete"
        assert call_args.resource_type == "project"


# ─── Issue Events ───


@pytest.mark.asyncio
class TestIssueEventHandlers:
    """Test issue event handlers."""

    async def test_handle_issue_created(self, consumer):
        event = {
            "event_type": "issue.created",
            "creator_id": str(uuid4()),
            "issue_id": str(uuid4()),
            "project_id": str(uuid4()),
            "data": {"title": "Bug", "priority": "high"},
            "service": "issue-service",
        }
        await consumer.handle_issue_created(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "create"
        assert call_args.resource_type == "issue"

    async def test_handle_issue_updated(self, consumer):
        event = {
            "event_type": "issue.updated",
            "actor_id": str(uuid4()),
            "issue_id": str(uuid4()),
            "project_id": str(uuid4()),
            "changes": {"priority": {"old": "low", "new": "high"}},
            "service": "issue-service",
        }
        await consumer.handle_issue_updated(event)
        consumer.repo.create.assert_awaited_once()

    async def test_handle_issue_status_changed(self, consumer):
        event = {
            "event_type": "issue.status_changed",
            "changed_by": str(uuid4()),
            "issue_id": str(uuid4()),
            "project_id": str(uuid4()),
            "old_status": "open",
            "new_status": "closed",
            "service": "issue-service",
        }
        await consumer.handle_issue_status_changed(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.changes == {"status": {"old": "open", "new": "closed"}}

    async def test_handle_issue_deleted(self, consumer):
        event = {
            "event_type": "issue.deleted",
            "actor_id": str(uuid4()),
            "issue_id": str(uuid4()),
            "project_id": str(uuid4()),
            "service": "issue-service",
        }
        await consumer.handle_issue_deleted(event)

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "delete"


# ─── Comment Events ───


@pytest.mark.asyncio
class TestCommentEventHandlers:
    """Test comment event handlers."""

    async def test_handle_comment_created(self, consumer):
        event = {
            "event_type": "comment.created",
            "author_id": str(uuid4()),
            "comment_id": str(uuid4()),
            "issue_id": str(uuid4()),
            "content": "This is a test comment",
            "service": "comment-service",
        }
        await consumer.handle_comment_created(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "create"
        assert call_args.resource_type == "comment"

    async def test_handle_comment_updated(self, consumer):
        event = {
            "event_type": "comment.updated",
            "actor_id": str(uuid4()),
            "comment_id": str(uuid4()),
            "issue_id": str(uuid4()),
            "changes": {"content": {"old": "old text", "new": "updated"}},
            "service": "comment-service",
        }
        await consumer.handle_comment_updated(event)
        consumer.repo.create.assert_awaited_once()

    async def test_handle_comment_deleted(self, consumer):
        event = {
            "event_type": "comment.deleted",
            "actor_id": str(uuid4()),
            "comment_id": str(uuid4()),
            "issue_id": str(uuid4()),
            "service": "comment-service",
        }
        await consumer.handle_comment_deleted(event)

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "delete"
        assert call_args.resource_type == "comment"


# ─── Generic Audit Event ───


@pytest.mark.asyncio
class TestGenericAuditEvent:
    """Test generic audit event handler."""

    async def test_handle_audit_event(self, consumer):
        event = {
            "event_type": "audit.event",
            "actor_id": str(uuid4()),
            "action": "custom_action",
            "resource_id": str(uuid4()),
            "resource_type": "custom",
            "changes": {"key": "value"},
            "service": "custom-service",
        }
        await consumer.handle_audit_event(event)
        consumer.repo.create.assert_awaited_once()

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.action == "custom_action"
        assert call_args.resource_type == "custom"

    async def test_handle_audit_event_default_service(self, consumer):
        event = {
            "event_type": "audit.event",
            "actor_id": str(uuid4()),
            "resource_id": str(uuid4()),
            "resource_type": "test",
        }
        await consumer.handle_audit_event(event)

        call_args = consumer.repo.create.call_args[0][0]
        assert call_args.service == "audit-service"


# ─── Message Routing ───


@pytest.mark.asyncio
class TestOnMessage:
    """Test message dispatch logic."""

    async def test_handler_registry_covers_all_events(self, consumer):
        expected_events = [
            "user.created", "user.updated", "user.deleted",
            "project.created", "project.updated", "project.deleted",
            "issue.created", "issue.updated", "issue.status_changed", "issue.deleted",
            "comment.created", "comment.updated", "comment.deleted",
            "audit.event",
        ]
        for event_type in expected_events:
            assert event_type in consumer.handlers, f"Missing handler for {event_type}"
