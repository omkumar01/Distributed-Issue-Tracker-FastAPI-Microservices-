"""Audit Service - Schema validation tests."""

import pytest
from uuid import uuid4
from pydantic import ValidationError

from src.schemas.audit import (
    AuditLogCreate, AuditLogResponse, AuditLogFilterParams,
    AuditStatusEnum, AuditActionEnum,
    ComplianceEventCreate, ComplianceEventResponse, SeverityEnum,
    DataAccessLogCreate, DataAccessLogResponse,
    AccessMethodEnum, OperationEnum,
    AuditLogStats, ResourceAuditHistory, DataAccessSummary,
)


class TestAuditActionEnum:
    """Test audit action enumeration."""

    def test_all_actions_present(self):
        actions = ["create", "read", "update", "delete", "login",
                   "logout", "export", "import", "share", "unshare"]
        for action in actions:
            assert AuditActionEnum(action).value == action

    def test_invalid_action(self):
        with pytest.raises(ValueError):
            AuditActionEnum("invalid_action")


class TestAuditStatusEnum:
    """Test audit status enumeration."""

    def test_all_statuses(self):
        for val in ["success", "failure", "warning"]:
            assert AuditStatusEnum(val).value == val


class TestSeverityEnum:
    """Test severity enumeration."""

    def test_all_severities(self):
        for val in ["critical", "high", "medium", "low", "info"]:
            assert SeverityEnum(val).value == val


class TestAuditLogCreate:
    """Test AuditLogCreate schema."""

    def test_valid_minimal(self):
        data = AuditLogCreate(
            actor_id=uuid4(),
            action=AuditActionEnum.CREATE,
            resource_id=uuid4(),
            resource_type="issue",
            service="issue-service",
        )
        assert data.action == "create"
        assert data.status == AuditStatusEnum.SUCCESS
        assert data.old_values is None

    def test_valid_with_all_fields(self):
        data = AuditLogCreate(
            actor_id=uuid4(),
            action=AuditActionEnum.UPDATE,
            resource_id=uuid4(),
            resource_type="issue",
            old_values={"status": "open"},
            new_values={"status": "closed"},
            changes={"status": {"old": "open", "new": "closed"}},
            status=AuditStatusEnum.SUCCESS,
            error_message=None,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            service="issue-service",
            project_id=uuid4(),
            issue_id=uuid4(),
        )
        assert data.old_values == {"status": "open"}
        assert data.new_values == {"status": "closed"}
        assert data.ip_address == "192.168.1.1"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            AuditLogCreate(action=AuditActionEnum.CREATE)

    def test_failure_status_with_error(self):
        data = AuditLogCreate(
            actor_id=uuid4(),
            action=AuditActionEnum.DELETE,
            resource_id=uuid4(),
            resource_type="project",
            status=AuditStatusEnum.FAILURE,
            error_message="Permission denied",
            service="project-service",
        )
        assert data.status == "failure"
        assert data.error_message == "Permission denied"


class TestAuditLogFilterParams:
    """Test filter parameter schema."""

    def test_defaults(self):
        params = AuditLogFilterParams()
        assert params.skip == 0
        assert params.limit == 20
        assert params.actor_id is None

    def test_custom_pagination(self):
        params = AuditLogFilterParams(skip=10, limit=50)
        assert params.skip == 10
        assert params.limit == 50

    def test_limit_out_of_range(self):
        with pytest.raises(ValidationError):
            AuditLogFilterParams(limit=200)

    def test_negative_skip(self):
        with pytest.raises(ValidationError):
            AuditLogFilterParams(skip=-1)


class TestComplianceEventCreate:
    """Test ComplianceEventCreate schema."""

    def test_valid_permanent_retention(self):
        data = ComplianceEventCreate(
            event_type="data_breach",
            severity=SeverityEnum.CRITICAL,
            actor_id=uuid4(),
            action="unauthorized_access",
            description="Breach detected",
            retention_days="permanent",
        )
        assert data.retention_days == "permanent"

    def test_valid_numeric_retention(self):
        data = ComplianceEventCreate(
            event_type="password_change",
            severity=SeverityEnum.LOW,
            actor_id=uuid4(),
            action="password_changed",
            description="User changed password",
            retention_days="90",
        )
        assert data.retention_days == "90"

    def test_missing_description(self):
        with pytest.raises(ValidationError):
            ComplianceEventCreate(
                event_type="test",
                severity=SeverityEnum.INFO,
                actor_id=uuid4(),
                action="test",
            )


class TestDataAccessLogCreate:
    """Test DataAccessLogCreate schema."""

    def test_valid_minimal(self):
        data = DataAccessLogCreate(
            actor_id=uuid4(),
            resource_id=uuid4(),
            resource_type="user",
            access_method=AccessMethodEnum.API,
            operation=OperationEnum.READ,
        )
        assert data.was_authorized is True
        assert data.fields_accessed is None

    def test_with_fields_and_purpose(self):
        data = DataAccessLogCreate(
            actor_id=uuid4(),
            resource_id=uuid4(),
            resource_type="user",
            fields_accessed=["email", "phone", "address"],
            access_method=AccessMethodEnum.EXPORT,
            operation=OperationEnum.EXPORT,
            purpose="GDPR request",
        )
        assert len(data.fields_accessed) == 3
        assert data.purpose == "GDPR request"

    def test_unauthorized_access(self):
        data = DataAccessLogCreate(
            actor_id=uuid4(),
            resource_id=uuid4(),
            resource_type="user",
            access_method=AccessMethodEnum.API,
            operation=OperationEnum.READ,
            was_authorized=False,
        )
        assert data.was_authorized is False


class TestAuditLogStats:
    """Test AuditLogStats schema."""

    def test_valid_stats(self):
        stats = AuditLogStats(
            total_actions=100,
            actions_by_type={"create": 50, "update": 30, "delete": 20},
            actions_by_status={"success": 90, "failure": 10},
            actions_by_service={"issue-service": 60, "user-service": 40},
            actions_by_actor={"actor1": 70, "actor2": 30},
            actions_last_24h=15,
            most_active_user=uuid4(),
        )
        assert stats.total_actions == 100
        assert stats.actions_last_24h == 15

    def test_empty_stats(self):
        stats = AuditLogStats(
            total_actions=0,
            actions_by_type={},
            actions_by_status={},
            actions_by_service={},
            actions_by_actor={},
            actions_last_24h=0,
        )
        assert stats.most_active_user is None


class TestDataAccessSummary:
    """Test DataAccessSummary schema."""

    def test_valid_summary(self):
        summary = DataAccessSummary(
            total_accesses=50,
            unauthorized_accesses=2,
            accesses_by_method={"api": 40, "export": 10},
            accesses_by_operation={"read": 45, "export": 5},
            accesses_by_actor={"actor1": 30, "actor2": 20},
        )
        assert summary.total_accesses == 50
        assert summary.unauthorized_accesses == 2
