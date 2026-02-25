"""Pytest configuration and fixtures for audit-service tests."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_audit_repo():
    """Create a mock AuditLogRepository."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.list_logs = AsyncMock()
    repo.get_by_resource = AsyncMock()
    repo.get_by_actor = AsyncMock()
    repo.get_stats = AsyncMock()
    return repo


@pytest.fixture
def mock_compliance_repo():
    """Create a mock ComplianceEventRepository."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.list_events = AsyncMock()
    return repo


@pytest.fixture
def mock_data_access_repo():
    """Create a mock DataAccessLogRepository."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_unauthorized_accesses = AsyncMock()
    repo.get_access_summary = AsyncMock()
    return repo


@pytest.fixture
def sample_audit_log():
    """Return a mock audit log model object."""
    log = MagicMock()
    log.id = uuid4()
    log.actor_id = uuid4()
    log.action = "create"
    log.resource_id = uuid4()
    log.resource_type = "issue"
    log.old_values = None
    log.new_values = {"title": "Bug Fix"}
    log.changes = None
    log.status = "success"
    log.error_message = None
    log.ip_address = "127.0.0.1"
    log.user_agent = "test-agent"
    log.service = "issue-service"
    log.project_id = uuid4()
    log.issue_id = uuid4()
    log.created_at = datetime.utcnow()
    return log


@pytest.fixture
def sample_compliance_event():
    """Return a mock compliance event model object."""
    event = MagicMock()
    event.id = uuid4()
    event.event_type = "data_breach"
    event.severity = "critical"
    event.actor_id = uuid4()
    event.action = "unauthorized_access"
    event.resource_id = uuid4()
    event.resource_type = "user"
    event.description = "Breach detected"
    event.details = {"ip": "10.0.0.1"}
    event.retention_days = "permanent"
    event.is_deleted = False
    event.created_at = datetime.utcnow()
    event.expires_at = None
    return event


@pytest.fixture
def sample_data_access_log():
    """Return a mock data access log model object."""
    log = MagicMock()
    log.id = uuid4()
    log.actor_id = uuid4()
    log.resource_id = uuid4()
    log.resource_type = "user"
    log.fields_accessed = ["email", "phone"]
    log.access_method = "api"
    log.operation = "read"
    log.ip_address = "127.0.0.1"
    log.purpose = "Support request"
    log.was_authorized = True
    log.accessed_at = datetime.utcnow()
    return log
