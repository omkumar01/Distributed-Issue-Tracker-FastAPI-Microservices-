"""Audit Service - Business logic services."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from src.repositories.audit_repository import (
    AuditLogRepository,
    ComplianceEventRepository,
    DataAccessLogRepository
)
from src.schemas.audit import (
    AuditLogCreate, AuditLogResponse, AuditLogFilterParams,
    AuditLogStats, ResourceAuditHistory,
    ComplianceEventCreate, ComplianceEventResponse,
    DataAccessLogCreate, DataAccessLogResponse,
    DataAccessSummary
)
from shared.utils.exceptions import ResourceNotFoundException, ServiceException


class AuditLogService:
    """Service for audit log operations."""
    
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository
    
    async def create_log(self, log_data: AuditLogCreate) -> AuditLogResponse:
        """Create a new audit log entry."""
        try:
            log = await self.repository.create(log_data)
            return AuditLogResponse.from_orm(log)
        except Exception as e:
            raise ServiceException(f"Failed to create audit log: {e}")
    
    async def get_log(self, log_id: UUID) -> AuditLogResponse:
        """Get audit log by ID."""
        log = await self.repository.get_by_id(log_id)
        if not log:
            raise ResourceNotFoundException("AuditLog", str(log_id))
        return AuditLogResponse.from_orm(log)
    
    async def list_logs(self, filters: AuditLogFilterParams) -> Dict[str, Any]:
        """List audit logs with filtering."""
        logs, total = await self.repository.list_logs(filters)
        return {
            "total": total,
            "items": [AuditLogResponse.from_orm(log) for log in logs],
            "skip": filters.skip,
            "limit": filters.limit
        }
    
    async def get_resource_history(
        self, 
        resource_id: UUID, 
        resource_type: str
    ) -> ResourceAuditHistory:
        """Get complete audit history for a resource."""
        logs = await self.repository.get_by_resource(resource_id, resource_type)
        
        if not logs:
            return ResourceAuditHistory(
                resource_id=resource_id,
                resource_type=resource_type,
                total_changes=0,
                audit_logs=[],
                change_timeline=[]
            )
        
        # Build change timeline
        change_timeline = []
        for log in logs:
            timeline_entry = {
                "timestamp": log.created_at.isoformat(),
                "action": log.action,
                "actor_id": str(log.actor_id),
                "changes": log.changes,
                "old_values": log.old_values,
                "new_values": log.new_values
            }
            change_timeline.append(timeline_entry)
        
        return ResourceAuditHistory(
            resource_id=resource_id,
            resource_type=resource_type,
            total_changes=len(logs),
            audit_logs=[AuditLogResponse.from_orm(log) for log in logs],
            change_timeline=change_timeline
        )
    
    async def get_user_activity(self, actor_id: UUID) -> List[AuditLogResponse]:
        """Get recent activity for a user."""
        logs = await self.repository.get_by_actor(actor_id)
        return [AuditLogResponse.from_orm(log) for log in logs]
    
    async def get_stats(self, days: int = 30) -> AuditLogStats:
        """Get audit statistics."""
        stats = await self.repository.get_stats(days)
        
        # Find most active user
        most_active_user = None
        if stats.get("actions_by_actor"):
            most_active = max(stats["actions_by_actor"], key=stats["actions_by_actor"].get)
            most_active_user = UUID(most_active) if most_active else None
        
        return AuditLogStats(
            total_actions=stats["total_actions"],
            actions_by_type=stats["actions_by_type"],
            actions_by_status=stats["actions_by_status"],
            actions_by_service=stats["actions_by_service"],
            actions_by_actor=stats["actions_by_actor"],
            actions_last_24h=stats["actions_last_24h"],
            most_active_user=most_active_user
        )


class ComplianceEventService:
    """Service for compliance events."""
    
    def __init__(self, repository: ComplianceEventRepository):
        self.repository = repository
    
    async def create_event(self, event_data: ComplianceEventCreate) -> ComplianceEventResponse:
        """Create a new compliance event."""
        try:
            event = await self.repository.create(event_data)
            return ComplianceEventResponse.from_orm(event)
        except Exception as e:
            raise ServiceException(f"Failed to create compliance event: {e}")
    
    async def get_event(self, event_id: UUID) -> ComplianceEventResponse:
        """Get compliance event by ID."""
        event = await self.repository.get_by_id(event_id)
        if not event:
            raise ResourceNotFoundException("ComplianceEvent", str(event_id))
        return ComplianceEventResponse.from_orm(event)
    
    async def list_events(
        self,
        severity: Optional[str] = None,
        event_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """List compliance events."""
        events, total = await self.repository.list_events(severity, event_type, skip, limit)
        return {
            "total": total,
            "items": [ComplianceEventResponse.from_orm(event) for event in events],
            "skip": skip,
            "limit": limit
        }


class DataAccessService:
    """Service for data access logs."""
    
    def __init__(self, repository: DataAccessLogRepository):
        self.repository = repository
    
    async def log_access(self, access_data: DataAccessLogCreate) -> DataAccessLogResponse:
        """Log a data access event."""
        try:
            log = await self.repository.create(access_data)
            return DataAccessLogResponse.from_orm(log)
        except Exception as e:
            raise ServiceException(f"Failed to log data access: {e}")
    
    async def get_log(self, log_id: UUID) -> DataAccessLogResponse:
        """Get data access log by ID."""
        log = await self.repository.get_by_id(log_id)
        if not log:
            raise ResourceNotFoundException("DataAccessLog", str(log_id))
        return DataAccessLogResponse.from_orm(log)
    
    async def get_unauthorized_accesses(
        self,
        days: int = 30,
        limit: int = 100
    ) -> List[DataAccessLogResponse]:
        """Get unauthorized data access attempts."""
        logs = await self.repository.get_unauthorized_accesses(days, limit)
        return [DataAccessLogResponse.from_orm(log) for log in logs]
    
    async def get_summary(self, days: int = 30) -> DataAccessSummary:
        """Get data access summary."""
        summary = await self.repository.get_access_summary(days)
        return DataAccessSummary(**summary)
