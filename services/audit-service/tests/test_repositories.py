"""Audit Service - Repository layer tests with mocked AsyncSession."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from src.repositories.audit_repository import (
    AuditLogRepository, ComplianceEventRepository, DataAccessLogRepository,
)
from src.schemas.audit import (
    AuditLogCreate, AuditStatusEnum, AuditActionEnum, AuditLogFilterParams,
    ComplianceEventCreate, SeverityEnum,
    DataAccessLogCreate, AccessMethodEnum, OperationEnum,
)
from shared.utils.exceptions import DatabaseException


# ─── AuditLogRepository Tests ───


@pytest.mark.asyncio
class TestAuditLogRepositoryCreate:
    """Test AuditLogRepository.create."""

    async def test_create_success(self, mock_session):
        repo = AuditLogRepository(mock_session)
        log_data = AuditLogCreate(
            actor_id=uuid4(), action=AuditActionEnum.CREATE,
            resource_id=uuid4(), resource_type="issue", service="issue-service",
        )

        result = await repo.create(log_data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    async def test_create_rollback_on_error(self, mock_session):
        mock_session.commit.side_effect = Exception("DB error")
        repo = AuditLogRepository(mock_session)

        log_data = AuditLogCreate(
            actor_id=uuid4(), action=AuditActionEnum.CREATE,
            resource_id=uuid4(), resource_type="issue", service="issue-service",
        )

        with pytest.raises(DatabaseException):
            await repo.create(log_data)
        mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
class TestAuditLogRepositoryGetById:
    """Test AuditLogRepository.get_by_id."""

    async def test_get_by_id_found(self, mock_session, sample_audit_log):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_audit_log
        mock_session.execute.return_value = mock_result

        repo = AuditLogRepository(mock_session)
        result = await repo.get_by_id(sample_audit_log.id)

        assert result == sample_audit_log

    async def test_get_by_id_not_found(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = AuditLogRepository(mock_session)
        result = await repo.get_by_id(uuid4())

        assert result is None


@pytest.mark.asyncio
class TestAuditLogRepositoryList:
    """Test AuditLogRepository.list_logs."""

    async def test_list_logs_returns_tuple(self, mock_session, sample_audit_log):
        # First execute returns count, second returns results
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_list_result = MagicMock()
        mock_list_result.scalars.return_value.all.return_value = [sample_audit_log]

        mock_session.execute.side_effect = [mock_count_result, mock_list_result]

        repo = AuditLogRepository(mock_session)
        filters = AuditLogFilterParams(skip=0, limit=20)
        logs, total = await repo.list_logs(filters)

        assert total == 1
        assert len(logs) == 1


@pytest.mark.asyncio
class TestAuditLogRepositoryByResource:
    """Test AuditLogRepository.get_by_resource."""

    async def test_get_by_resource(self, mock_session, sample_audit_log):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_audit_log]
        mock_session.execute.return_value = mock_result

        repo = AuditLogRepository(mock_session)
        result = await repo.get_by_resource(sample_audit_log.resource_id, "issue")

        assert len(result) == 1
        assert result[0] == sample_audit_log


@pytest.mark.asyncio
class TestAuditLogRepositoryByActor:
    """Test AuditLogRepository.get_by_actor."""

    async def test_get_by_actor(self, mock_session, sample_audit_log):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_audit_log]
        mock_session.execute.return_value = mock_result

        repo = AuditLogRepository(mock_session)
        result = await repo.get_by_actor(sample_audit_log.actor_id, limit=50)

        assert len(result) == 1


@pytest.mark.asyncio
class TestAuditLogRepositoryStats:
    """Test AuditLogRepository.get_stats."""

    async def test_get_stats_with_data(self, mock_session, sample_audit_log):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_audit_log]
        mock_session.execute.return_value = mock_result

        repo = AuditLogRepository(mock_session)
        stats = await repo.get_stats(30)

        assert stats["total_actions"] == 1
        assert "actions_by_type" in stats
        assert "actions_by_status" in stats

    async def test_get_stats_empty(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = AuditLogRepository(mock_session)
        stats = await repo.get_stats(30)

        assert stats["total_actions"] == 0
        assert stats["actions_by_type"] == {}


# ─── ComplianceEventRepository Tests ───


@pytest.mark.asyncio
class TestComplianceEventRepositoryCreate:
    """Test ComplianceEventRepository.create."""

    async def test_create_success(self, mock_session):
        repo = ComplianceEventRepository(mock_session)
        event_data = ComplianceEventCreate(
            event_type="data_breach", severity=SeverityEnum.CRITICAL,
            actor_id=uuid4(), action="unauthorized_access",
            description="Breach", retention_days="permanent",
        )

        result = await repo.create(event_data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

    async def test_create_with_numeric_retention(self, mock_session):
        repo = ComplianceEventRepository(mock_session)
        event_data = ComplianceEventCreate(
            event_type="password_change", severity=SeverityEnum.LOW,
            actor_id=uuid4(), action="changed",
            description="Changed", retention_days="90",
        )

        result = await repo.create(event_data)
        mock_session.add.assert_called_once()

    async def test_create_rollback_on_error(self, mock_session):
        mock_session.commit.side_effect = Exception("DB error")
        repo = ComplianceEventRepository(mock_session)

        with pytest.raises(DatabaseException):
            await repo.create(ComplianceEventCreate(
                event_type="test", severity=SeverityEnum.INFO,
                actor_id=uuid4(), action="test", description="test",
            ))
        mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
class TestComplianceEventRepositoryGet:
    """Test ComplianceEventRepository.get_by_id."""

    async def test_get_by_id(self, mock_session, sample_compliance_event):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_compliance_event
        mock_session.execute.return_value = mock_result

        repo = ComplianceEventRepository(mock_session)
        result = await repo.get_by_id(sample_compliance_event.id)

        assert result == sample_compliance_event


@pytest.mark.asyncio
class TestComplianceEventRepositoryList:
    """Test ComplianceEventRepository.list_events."""

    async def test_list_events(self, mock_session, sample_compliance_event):
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_list_result = MagicMock()
        mock_list_result.scalars.return_value.all.return_value = [sample_compliance_event]

        mock_session.execute.side_effect = [mock_count_result, mock_list_result]

        repo = ComplianceEventRepository(mock_session)
        events, total = await repo.list_events()

        assert total == 1
        assert len(events) == 1


# ─── DataAccessLogRepository Tests ───


@pytest.mark.asyncio
class TestDataAccessLogRepositoryCreate:
    """Test DataAccessLogRepository.create."""

    async def test_create_success(self, mock_session):
        repo = DataAccessLogRepository(mock_session)
        log_data = DataAccessLogCreate(
            actor_id=uuid4(), resource_id=uuid4(), resource_type="user",
            access_method=AccessMethodEnum.API, operation=OperationEnum.READ,
        )

        result = await repo.create(log_data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

    async def test_create_rollback_on_error(self, mock_session):
        mock_session.commit.side_effect = Exception("DB error")
        repo = DataAccessLogRepository(mock_session)

        with pytest.raises(DatabaseException):
            await repo.create(DataAccessLogCreate(
                actor_id=uuid4(), resource_id=uuid4(), resource_type="user",
                access_method=AccessMethodEnum.API, operation=OperationEnum.READ,
            ))
        mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
class TestDataAccessLogRepositoryGet:
    """Test DataAccessLogRepository.get_by_id."""

    async def test_get_by_id(self, mock_session, sample_data_access_log):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_data_access_log
        mock_session.execute.return_value = mock_result

        repo = DataAccessLogRepository(mock_session)
        result = await repo.get_by_id(sample_data_access_log.id)

        assert result == sample_data_access_log


@pytest.mark.asyncio
class TestDataAccessLogRepositoryUnauthorized:
    """Test DataAccessLogRepository.get_unauthorized_accesses."""

    async def test_get_unauthorized(self, mock_session, sample_data_access_log):
        sample_data_access_log.was_authorized = False
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_data_access_log]
        mock_session.execute.return_value = mock_result

        repo = DataAccessLogRepository(mock_session)
        result = await repo.get_unauthorized_accesses(30, 100)

        assert len(result) == 1


@pytest.mark.asyncio
class TestDataAccessLogRepositorySummary:
    """Test DataAccessLogRepository.get_access_summary."""

    async def test_summary_with_data(self, mock_session, sample_data_access_log):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_data_access_log]
        mock_session.execute.return_value = mock_result

        repo = DataAccessLogRepository(mock_session)
        summary = await repo.get_access_summary(30)

        assert summary["total_accesses"] == 1
        assert "accesses_by_method" in summary

    async def test_summary_empty(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        repo = DataAccessLogRepository(mock_session)
        summary = await repo.get_access_summary(30)

        assert summary["total_accesses"] == 0
