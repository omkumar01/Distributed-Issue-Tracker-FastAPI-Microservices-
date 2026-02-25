"""Audit Service - Service layer tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.schemas.audit import (
    AuditLogCreate, AuditStatusEnum, AuditActionEnum,
    AuditLogFilterParams,
    ComplianceEventCreate, SeverityEnum,
    DataAccessLogCreate, AccessMethodEnum, OperationEnum,
)
from src.services.audit_service import (
    AuditLogService, ComplianceEventService, DataAccessService,
)
from shared.utils.exceptions import ResourceNotFoundException, ServiceException


# ─── AuditLogService Tests ───


@pytest.mark.asyncio
class TestAuditLogServiceCreate:
    """Test AuditLogService.create_log."""

    async def test_create_log_success(self, mock_audit_repo, sample_audit_log):
        mock_audit_repo.create.return_value = sample_audit_log
        service = AuditLogService(mock_audit_repo)

        log_data = AuditLogCreate(
            actor_id=uuid4(), action=AuditActionEnum.CREATE,
            resource_id=uuid4(), resource_type="issue", service="issue-service",
        )
        result = await service.create_log(log_data)

        assert result is not None
        assert result.action == "create"
        mock_audit_repo.create.assert_awaited_once_with(log_data)

    async def test_create_log_repo_failure(self, mock_audit_repo):
        mock_audit_repo.create.side_effect = Exception("DB error")
        service = AuditLogService(mock_audit_repo)

        log_data = AuditLogCreate(
            actor_id=uuid4(), action=AuditActionEnum.CREATE,
            resource_id=uuid4(), resource_type="issue", service="issue-service",
        )
        with pytest.raises(ServiceException):
            await service.create_log(log_data)


@pytest.mark.asyncio
class TestAuditLogServiceGet:
    """Test AuditLogService.get_log."""

    async def test_get_log_found(self, mock_audit_repo, sample_audit_log):
        mock_audit_repo.get_by_id.return_value = sample_audit_log
        service = AuditLogService(mock_audit_repo)

        result = await service.get_log(sample_audit_log.id)
        assert result.id == sample_audit_log.id

    async def test_get_log_not_found(self, mock_audit_repo):
        mock_audit_repo.get_by_id.return_value = None
        service = AuditLogService(mock_audit_repo)

        with pytest.raises(ResourceNotFoundException):
            await service.get_log(uuid4())


@pytest.mark.asyncio
class TestAuditLogServiceList:
    """Test AuditLogService.list_logs."""

    async def test_list_logs(self, mock_audit_repo, sample_audit_log):
        mock_audit_repo.list_logs.return_value = ([sample_audit_log], 1)
        service = AuditLogService(mock_audit_repo)

        filters = AuditLogFilterParams(skip=0, limit=20)
        result = await service.list_logs(filters)

        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["skip"] == 0
        assert result["limit"] == 20

    async def test_list_logs_empty(self, mock_audit_repo):
        mock_audit_repo.list_logs.return_value = ([], 0)
        service = AuditLogService(mock_audit_repo)

        result = await service.list_logs(AuditLogFilterParams())
        assert result["total"] == 0
        assert result["items"] == []


@pytest.mark.asyncio
class TestAuditLogServiceResourceHistory:
    """Test AuditLogService.get_resource_history."""

    async def test_resource_history_with_logs(self, mock_audit_repo):
        resource_id = uuid4()
        mock_logs = []
        for action in ["create", "update"]:
            log = MagicMock()
            log.id = uuid4()
            log.action = action
            log.actor_id = uuid4()
            log.resource_id = resource_id
            log.resource_type = "issue"
            log.created_at = datetime.utcnow()
            log.old_values = None
            log.new_values = {"title": "test"}
            log.changes = None
            log.status = "success"
            log.error_message = None
            log.ip_address = None
            log.user_agent = None
            log.service = "issue-service"
            log.project_id = None
            log.issue_id = None
            mock_logs.append(log)

        mock_audit_repo.get_by_resource.return_value = mock_logs
        service = AuditLogService(mock_audit_repo)

        result = await service.get_resource_history(resource_id, "issue")

        assert result.resource_id == resource_id
        assert result.resource_type == "issue"
        assert result.total_changes == 2
        assert len(result.change_timeline) == 2

    async def test_resource_history_empty(self, mock_audit_repo):
        mock_audit_repo.get_by_resource.return_value = []
        service = AuditLogService(mock_audit_repo)

        result = await service.get_resource_history(uuid4(), "issue")

        assert result.total_changes == 0
        assert result.audit_logs == []


@pytest.mark.asyncio
class TestAuditLogServiceStats:
    """Test AuditLogService.get_stats."""

    async def test_get_stats(self, mock_audit_repo):
        actor_id = str(uuid4())
        mock_audit_repo.get_stats.return_value = {
            "total_actions": 10,
            "actions_by_type": {"create": 5, "update": 5},
            "actions_by_status": {"success": 10},
            "actions_by_service": {"issue-service": 10},
            "actions_by_actor": {actor_id: 10},
            "actions_last_24h": 3,
        }
        service = AuditLogService(mock_audit_repo)

        result = await service.get_stats(30)

        assert result.total_actions == 10
        assert result.most_active_user is not None

    async def test_get_stats_empty(self, mock_audit_repo):
        mock_audit_repo.get_stats.return_value = {
            "total_actions": 0,
            "actions_by_type": {},
            "actions_by_status": {},
            "actions_by_service": {},
            "actions_by_actor": {},
            "actions_last_24h": 0,
        }
        service = AuditLogService(mock_audit_repo)

        result = await service.get_stats(30)
        assert result.total_actions == 0
        assert result.most_active_user is None


@pytest.mark.asyncio
class TestAuditLogServiceUserActivity:
    """Test AuditLogService.get_user_activity."""

    async def test_user_activity(self, mock_audit_repo, sample_audit_log):
        mock_audit_repo.get_by_actor.return_value = [sample_audit_log]
        service = AuditLogService(mock_audit_repo)

        result = await service.get_user_activity(sample_audit_log.actor_id)
        assert len(result) == 1


# ─── ComplianceEventService Tests ───


@pytest.mark.asyncio
class TestComplianceEventService:
    """Tests for ComplianceEventService."""

    async def test_create_event(self, mock_compliance_repo, sample_compliance_event):
        mock_compliance_repo.create.return_value = sample_compliance_event
        service = ComplianceEventService(mock_compliance_repo)

        event_data = ComplianceEventCreate(
            event_type="data_breach", severity=SeverityEnum.CRITICAL,
            actor_id=uuid4(), action="unauthorized_access",
            description="Breach detected",
        )
        result = await service.create_event(event_data)

        assert result.event_type == "data_breach"
        mock_compliance_repo.create.assert_awaited_once()

    async def test_create_event_failure(self, mock_compliance_repo):
        mock_compliance_repo.create.side_effect = Exception("DB error")
        service = ComplianceEventService(mock_compliance_repo)

        with pytest.raises(ServiceException):
            await service.create_event(ComplianceEventCreate(
                event_type="test", severity=SeverityEnum.INFO,
                actor_id=uuid4(), action="test", description="test",
            ))

    async def test_get_event_found(self, mock_compliance_repo, sample_compliance_event):
        mock_compliance_repo.get_by_id.return_value = sample_compliance_event
        service = ComplianceEventService(mock_compliance_repo)

        result = await service.get_event(sample_compliance_event.id)
        assert result.id == sample_compliance_event.id

    async def test_get_event_not_found(self, mock_compliance_repo):
        mock_compliance_repo.get_by_id.return_value = None
        service = ComplianceEventService(mock_compliance_repo)

        with pytest.raises(ResourceNotFoundException):
            await service.get_event(uuid4())

    async def test_list_events(self, mock_compliance_repo, sample_compliance_event):
        mock_compliance_repo.list_events.return_value = ([sample_compliance_event], 1)
        service = ComplianceEventService(mock_compliance_repo)

        result = await service.list_events(severity="critical")
        assert result["total"] == 1
        assert len(result["items"]) == 1


# ─── DataAccessService Tests ───


@pytest.mark.asyncio
class TestDataAccessService:
    """Tests for DataAccessService."""

    async def test_log_access(self, mock_data_access_repo, sample_data_access_log):
        mock_data_access_repo.create.return_value = sample_data_access_log
        service = DataAccessService(mock_data_access_repo)

        access_data = DataAccessLogCreate(
            actor_id=uuid4(), resource_id=uuid4(), resource_type="user",
            access_method=AccessMethodEnum.API, operation=OperationEnum.READ,
        )
        result = await service.log_access(access_data)

        assert result.access_method == "api"
        mock_data_access_repo.create.assert_awaited_once()

    async def test_log_access_failure(self, mock_data_access_repo):
        mock_data_access_repo.create.side_effect = Exception("DB error")
        service = DataAccessService(mock_data_access_repo)

        with pytest.raises(ServiceException):
            await service.log_access(DataAccessLogCreate(
                actor_id=uuid4(), resource_id=uuid4(), resource_type="user",
                access_method=AccessMethodEnum.API, operation=OperationEnum.READ,
            ))

    async def test_get_log_found(self, mock_data_access_repo, sample_data_access_log):
        mock_data_access_repo.get_by_id.return_value = sample_data_access_log
        service = DataAccessService(mock_data_access_repo)

        result = await service.get_log(sample_data_access_log.id)
        assert result.id == sample_data_access_log.id

    async def test_get_log_not_found(self, mock_data_access_repo):
        mock_data_access_repo.get_by_id.return_value = None
        service = DataAccessService(mock_data_access_repo)

        with pytest.raises(ResourceNotFoundException):
            await service.get_log(uuid4())

    async def test_get_unauthorized_accesses(self, mock_data_access_repo, sample_data_access_log):
        sample_data_access_log.was_authorized = False
        mock_data_access_repo.get_unauthorized_accesses.return_value = [sample_data_access_log]
        service = DataAccessService(mock_data_access_repo)

        result = await service.get_unauthorized_accesses(days=30)
        assert len(result) == 1

    async def test_get_summary(self, mock_data_access_repo):
        mock_data_access_repo.get_access_summary.return_value = {
            "total_accesses": 50,
            "unauthorized_accesses": 2,
            "accesses_by_method": {"api": 40, "export": 10},
            "accesses_by_operation": {"read": 45, "export": 5},
            "accesses_by_actor": {"actor1": 30, "actor2": 20},
        }
        service = DataAccessService(mock_data_access_repo)

        result = await service.get_summary(30)
        assert result.total_accesses == 50
        assert result.unauthorized_accesses == 2
