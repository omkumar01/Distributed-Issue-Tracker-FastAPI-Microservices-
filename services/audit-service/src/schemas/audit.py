"""Audit Service - Pydantic schemas."""

from typing import Optional, Any, Dict, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class AuditActionEnum(str, Enum):
    """Audit action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    SHARE = "share"
    UNSHARE = "unshare"


class AuditStatusEnum(str, Enum):
    """Audit status types."""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"


class SeverityEnum(str, Enum):
    """Severity levels for compliance events."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AccessMethodEnum(str, Enum):
    """Data access methods."""
    API = "api"
    BATCH = "batch"
    INTERNAL = "internal"
    EXPORT = "export"


class OperationEnum(str, Enum):
    """Operations for data access."""
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"


# ============ Audit Log Schemas ============

class AuditLogCreate(BaseModel):
    """Create audit log."""
    actor_id: UUID
    action: str
    resource_id: UUID
    resource_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    status: AuditStatusEnum = AuditStatusEnum.SUCCESS
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    service: str
    project_id: Optional[UUID] = None
    issue_id: Optional[UUID] = None


class AuditLogResponse(BaseModel):
    """Audit log response."""
    id: UUID
    actor_id: UUID
    action: str
    resource_id: UUID
    resource_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    service: str
    project_id: Optional[UUID] = None
    issue_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Compliance Event Schemas ============

class ComplianceEventCreate(BaseModel):
    """Create compliance event."""
    event_type: str
    severity: SeverityEnum
    actor_id: UUID
    action: str
    resource_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    description: str
    details: Optional[Dict[str, Any]] = None
    retention_days: str = "permanent"


class ComplianceEventResponse(BaseModel):
    """Compliance event response."""
    id: UUID
    event_type: str
    severity: str
    actor_id: UUID
    action: str
    resource_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    description: str
    details: Optional[Dict[str, Any]] = None
    retention_days: str
    is_deleted: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ Data Access Log Schemas ============

class DataAccessLogCreate(BaseModel):
    """Create data access log."""
    actor_id: UUID
    resource_id: UUID
    resource_type: str
    fields_accessed: Optional[List[str]] = None
    access_method: AccessMethodEnum
    operation: OperationEnum
    ip_address: Optional[str] = None
    purpose: Optional[str] = None
    was_authorized: bool = True


class DataAccessLogResponse(BaseModel):
    """Data access log response."""
    id: UUID
    actor_id: UUID
    resource_id: UUID
    resource_type: str
    fields_accessed: Optional[List[str]] = None
    access_method: str
    operation: str
    ip_address: Optional[str] = None
    purpose: Optional[str] = None
    was_authorized: bool
    accessed_at: datetime
    
    class Config:
        from_attributes = True


# ============ Query/Filter Schemas ============

class AuditLogFilterParams(BaseModel):
    """Filter parameters for audit logs."""
    actor_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    service: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class AuditLogStats(BaseModel):
    """Statistics for audit logs."""
    total_actions: int
    actions_by_type: Dict[str, int]
    actions_by_status: Dict[str, int]
    actions_by_service: Dict[str, int]
    actions_by_actor: Dict[str, int]
    actions_last_24h: int
    most_active_user: Optional[UUID] = None


class ResourceAuditHistory(BaseModel):
    """Complete audit history for a resource."""
    resource_id: UUID
    resource_type: str
    total_changes: int
    audit_logs: List[AuditLogResponse]
    change_timeline: List[Dict[str, Any]]


class DataAccessSummary(BaseModel):
    """Summary of data access for compliance."""
    total_accesses: int
    unauthorized_accesses: int
    accesses_by_method: Dict[str, int]
    accesses_by_operation: Dict[str, int]
    accesses_by_actor: Dict[str, int]

    class Config:
        from_attributes = True
