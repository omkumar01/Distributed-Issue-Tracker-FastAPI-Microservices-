"""Audit Service - API route tests with mocked dependencies."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient, ASGITransport

from src.schemas.audit import (
    AuditActionEnum, AuditStatusEnum, SeverityEnum,
    AccessMethodEnum, OperationEnum,
)


def _make_audit_log_mock():
    """Create a mock audit log for response testing."""
    log = MagicMock()
    log.id = uuid4()
    log.actor_id = uuid4()
    log.action = "create"
    log.resource_id = uuid4()
    log.resource_type = "issue"
    log.old_values = None
    log.new_values = {"title": "Bug"}
    log.changes = None
    log.status = "success"
    log.error_message = None
    log.ip_address = None
    log.user_agent = None
    log.service = "issue-service"
    log.project_id = None
    log.issue_id = None
    log.created_at = datetime.utcnow()
    return log


def _make_compliance_event_mock():
    """Create a mock compliance event."""
    event = MagicMock()
    event.id = uuid4()
    event.event_type = "data_breach"
    event.severity = "critical"
    event.actor_id = uuid4()
    event.action = "unauthorized_access"
    event.resource_id = None
    event.resource_type = None
    event.description = "Breach"
    event.details = None
    event.retention_days = "permanent"
    event.is_deleted = False
    event.created_at = datetime.utcnow()
    event.expires_at = None
    return event


def _make_data_access_mock():
    """Create a mock data access log."""
    log = MagicMock()
    log.id = uuid4()
    log.actor_id = uuid4()
    log.resource_id = uuid4()
    log.resource_type = "user"
    log.fields_accessed = None
    log.access_method = "api"
    log.operation = "read"
    log.ip_address = None
    log.purpose = None
    log.was_authorized = True
    log.accessed_at = datetime.utcnow()
    return log


@pytest.fixture
def mock_get_session():
    """Patch get_session dependency to return a mock session."""
    mock_session = AsyncMock()

    async def _override():
        yield mock_session

    return mock_session, _override


@pytest.fixture
async def client(mock_get_session):
    """Create async client with mocked DB session."""
    mock_session, override = mock_get_session

    # Import app and override the dependency
    from src.main import app
    from src.database import get_session

    app.dependency_overrides[get_session] = override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


# ─── Health & Root Endpoints ───


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health and root endpoints."""

    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "audit-service"

    async def test_root(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Audit Service" in data["message"]


# ─── Audit Log Endpoints ───


@pytest.mark.asyncio
class TestAuditLogEndpoints:
    """Test audit log API endpoints."""

    @patch("src.routers.audit_router.AuditLogRepository")
    @patch("src.routers.audit_router.AuditLogService")
    async def test_create_audit_log(self, MockService, MockRepo, client):
        mock_log = _make_audit_log_mock()
        mock_service_instance = AsyncMock()
        mock_service_instance.create_log.return_value = MagicMock(
            id=mock_log.id, actor_id=mock_log.actor_id,
            action="create", resource_id=mock_log.resource_id,
            resource_type="issue", old_values=None, new_values=None,
            changes=None, status="success", error_message=None,
            ip_address=None, user_agent=None, service="issue-service",
            project_id=None, issue_id=None,
            created_at=mock_log.created_at.isoformat(),
        )
        MockService.return_value = mock_service_instance

        response = await client.post("/api/v1", json={
            "actor_id": str(uuid4()),
            "action": "create",
            "resource_id": str(uuid4()),
            "resource_type": "issue",
            "service": "issue-service",
        })

        assert response.status_code == 201

    @patch("src.routers.audit_router.AuditLogRepository")
    @patch("src.routers.audit_router.AuditLogService")
    async def test_get_audit_log(self, MockService, MockRepo, client):
        log_id = uuid4()
        mock_service_instance = AsyncMock()
        mock_service_instance.get_log.return_value = MagicMock(
            id=log_id, actor_id=uuid4(), action="create",
            resource_id=uuid4(), resource_type="issue",
            old_values=None, new_values=None, changes=None,
            status="success", error_message=None, ip_address=None,
            user_agent=None, service="issue-service",
            project_id=None, issue_id=None,
            created_at=datetime.utcnow().isoformat(),
        )
        MockService.return_value = mock_service_instance

        response = await client.get(f"/api/v1/logs/{log_id}")
        assert response.status_code == 200

    @patch("src.routers.audit_router.AuditLogRepository")
    @patch("src.routers.audit_router.AuditLogService")
    async def test_list_audit_logs(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.list_logs.return_value = {
            "total": 0, "items": [], "skip": 0, "limit": 20,
        }
        MockService.return_value = mock_service_instance

        response = await client.get("/api/v1/logs")
        assert response.status_code == 200

    @patch("src.routers.audit_router.AuditLogRepository")
    @patch("src.routers.audit_router.AuditLogService")
    async def test_get_resource_history(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.get_resource_history.return_value = MagicMock(
            resource_id=uuid4(), resource_type="issue",
            total_changes=0, audit_logs=[], change_timeline=[],
        )
        MockService.return_value = mock_service_instance

        resource_id = uuid4()
        response = await client.get(
            f"/api/v1/resource/{resource_id}?resource_type=issue"
        )
        assert response.status_code == 200

    @patch("src.routers.audit_router.AuditLogRepository")
    @patch("src.routers.audit_router.AuditLogService")
    async def test_get_user_activity(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.get_user_activity.return_value = []
        MockService.return_value = mock_service_instance

        actor_id = uuid4()
        response = await client.get(f"/api/v1/user/{actor_id}/activity")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @patch("src.routers.audit_router.AuditLogRepository")
    @patch("src.routers.audit_router.AuditLogService")
    async def test_get_audit_stats(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.get_stats.return_value = MagicMock(
            total_actions=0, actions_by_type={}, actions_by_status={},
            actions_by_service={}, actions_by_actor={},
            actions_last_24h=0, most_active_user=None,
        )
        MockService.return_value = mock_service_instance

        response = await client.get("/api/v1/stats")
        assert response.status_code == 200


# ─── Compliance Endpoints ───


@pytest.mark.asyncio
class TestComplianceEndpoints:
    """Test compliance event API endpoints."""

    @patch("src.routers.audit_router.ComplianceEventRepository")
    @patch("src.routers.audit_router.ComplianceEventService")
    async def test_create_compliance_event(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.create_event.return_value = MagicMock(
            id=uuid4(), event_type="data_breach", severity="critical",
            actor_id=uuid4(), action="unauthorized_access",
            resource_id=None, resource_type=None,
            description="Breach", details=None,
            retention_days="permanent", is_deleted=False,
            created_at=datetime.utcnow().isoformat(), expires_at=None,
        )
        MockService.return_value = mock_service_instance

        response = await client.post("/api/v1/compliance", json={
            "event_type": "data_breach",
            "severity": "critical",
            "actor_id": str(uuid4()),
            "action": "unauthorized_access",
            "description": "Breach detected",
        })
        assert response.status_code == 201

    @patch("src.routers.audit_router.ComplianceEventRepository")
    @patch("src.routers.audit_router.ComplianceEventService")
    async def test_list_compliance_events(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.list_events.return_value = {
            "total": 0, "items": [], "skip": 0, "limit": 50,
        }
        MockService.return_value = mock_service_instance

        response = await client.get("/api/v1/compliance")
        assert response.status_code == 200


# ─── Data Access Endpoints ───


@pytest.mark.asyncio
class TestDataAccessEndpoints:
    """Test data access log API endpoints."""

    @patch("src.routers.audit_router.DataAccessLogRepository")
    @patch("src.routers.audit_router.DataAccessService")
    async def test_log_data_access(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.log_access.return_value = MagicMock(
            id=uuid4(), actor_id=uuid4(), resource_id=uuid4(),
            resource_type="user", fields_accessed=None,
            access_method="api", operation="read",
            ip_address=None, purpose=None, was_authorized=True,
            accessed_at=datetime.utcnow().isoformat(),
        )
        MockService.return_value = mock_service_instance

        response = await client.post("/api/v1/data-access", json={
            "actor_id": str(uuid4()),
            "resource_id": str(uuid4()),
            "resource_type": "user",
            "access_method": "api",
            "operation": "read",
        })
        assert response.status_code == 201

    @patch("src.routers.audit_router.DataAccessLogRepository")
    @patch("src.routers.audit_router.DataAccessService")
    async def test_get_data_access_summary(self, MockService, MockRepo, client):
        mock_service_instance = AsyncMock()
        mock_service_instance.get_summary.return_value = {
            "total_accesses": 0,
            "unauthorized_accesses": 0,
            "accesses_by_method": {},
            "accesses_by_operation": {},
            "accesses_by_actor": {},
        }
        MockService.return_value = mock_service_instance

        response = await client.get("/api/v1/data-access/summary")
        print(f"\nResponse Body: {response.text}")
        assert response.status_code == 200
