"""Audit Log Repository."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, between
from sqlalchemy.orm import selectinload

from src.models.audit_log import AuditLog, ComplianceEvent, DataAccessLog
from src.schemas.audit import (
    AuditLogCreate, AuditLogFilterParams,
    ComplianceEventCreate, DataAccessLogCreate
)
from shared.utils.exceptions import DatabaseException


class AuditLogRepository:
    """Repository for audit log operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, audit_log_data: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry."""
        try:
            log = AuditLog(**audit_log_data.dict())
            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)
            return log
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create audit log: {e}")
    
    async def get_by_id(self, log_id: UUID) -> Optional[AuditLog]:
        """Get audit log by ID."""
        result = await self.db.execute(
            select(AuditLog).where(AuditLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    async def list_logs(self, filters: AuditLogFilterParams) -> tuple[List[AuditLog], int]:
        """List audit logs with filters."""
        query = select(AuditLog)
        
        # Apply filters
        conditions = []
        
        if filters.actor_id:
            conditions.append(AuditLog.actor_id == filters.actor_id)
        if filters.action:
            conditions.append(AuditLog.action == filters.action)
        if filters.resource_type:
            conditions.append(AuditLog.resource_type == filters.resource_type)
        if filters.resource_id:
            conditions.append(AuditLog.resource_id == filters.resource_id)
        if filters.service:
            conditions.append(AuditLog.service == filters.service)
        if filters.status:
            conditions.append(AuditLog.status == filters.status)
        
        # Date range filter
        if filters.start_date and filters.end_date:
            conditions.append(
                between(AuditLog.created_at, filters.start_date, filters.end_date)
            )
        elif filters.start_date:
            conditions.append(AuditLog.created_at >= filters.start_date)
        elif filters.end_date:
            conditions.append(AuditLog.created_at <= filters.end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(AuditLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(desc(AuditLog.created_at))
        query = query.offset(filters.skip).limit(filters.limit)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return logs, total
    
    async def get_by_resource(self, resource_id: UUID, resource_type: str) -> List[AuditLog]:
        """Get all audit logs for a specific resource."""
        result = await self.db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.resource_id == resource_id,
                    AuditLog.resource_type == resource_type
                )
            )
            .order_by(desc(AuditLog.created_at))
        )
        return result.scalars().all()
    
    async def get_by_actor(self, actor_id: UUID, limit: int = 50) -> List[AuditLog]:
        """Get recent audit logs for a specific actor."""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.actor_id == actor_id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics for the last N days."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(AuditLog).where(AuditLog.created_at >= start_date)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            return {
                "total_actions": 0,
                "actions_by_type": {},
                "actions_by_status": {},
                "actions_by_service": {},
                "actions_by_actor": {},
                "actions_last_24h": 0
            }
        
        # Calculate statistics
        actions_by_type = {}
        actions_by_status = {}
        actions_by_service = {}
        actions_by_actor = {}
        
        for log in logs:
            actions_by_type[log.action] = actions_by_type.get(log.action, 0) + 1
            actions_by_status[log.status] = actions_by_status.get(log.status, 0) + 1
            actions_by_service[log.service] = actions_by_service.get(log.service, 0) + 1
            
            actor_id_str = str(log.actor_id)
            actions_by_actor[actor_id_str] = actions_by_actor.get(actor_id_str, 0) + 1
        
        # Count last 24 hours
        last_24h = datetime.utcnow() - timedelta(hours=24)
        last_24h_count = sum(1 for log in logs if log.created_at >= last_24h)
        
        return {
            "total_actions": len(logs),
            "actions_by_type": actions_by_type,
            "actions_by_status": actions_by_status,
            "actions_by_service": actions_by_service,
            "actions_by_actor": actions_by_actor,
            "actions_last_24h": last_24h_count
        }


class ComplianceEventRepository:
    """Repository for compliance events."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, event_data: ComplianceEventCreate) -> ComplianceEvent:
        """Create a new compliance event."""
        try:
            # Calculate expiration date if retention_days is specified
            expires_at = None
            if event_data.retention_days != "permanent":
                try:
                    retention_days = int(event_data.retention_days)
                    expires_at = datetime.utcnow() + timedelta(days=retention_days)
                except (ValueError, TypeError):
                    pass
            
            event_dict = event_data.dict()
            event_dict["expires_at"] = expires_at
            
            event = ComplianceEvent(**event_dict)
            self.db.add(event)
            await self.db.commit()
            await self.db.refresh(event)
            return event
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create compliance event: {e}")
    
    async def get_by_id(self, event_id: UUID) -> Optional[ComplianceEvent]:
        """Get compliance event by ID."""
        result = await self.db.execute(
            select(ComplianceEvent).where(ComplianceEvent.id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def list_events(
        self, 
        severity: Optional[str] = None,
        event_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[ComplianceEvent], int]:
        """List compliance events."""
        query = select(ComplianceEvent)
        
        conditions = [ComplianceEvent.is_deleted == False]
        
        if severity:
            conditions.append(ComplianceEvent.severity == severity)
        if event_type:
            conditions.append(ComplianceEvent.event_type == event_type)
        
        query = query.where(and_(*conditions))
        
        # Count total
        count_result = await self.db.execute(
            select(func.count()).select_from(ComplianceEvent).where(and_(*conditions))
        )
        total = count_result.scalar()
        
        # Get results
        query = query.order_by(desc(ComplianceEvent.created_at))
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        events = result.scalars().all()
        
        return events, total


class DataAccessLogRepository:
    """Repository for data access logs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, access_data: DataAccessLogCreate) -> DataAccessLog:
        """Create a new data access log."""
        try:
            log = DataAccessLog(**access_data.dict())
            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)
            return log
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create data access log: {e}")
    
    async def get_by_id(self, log_id: UUID) -> Optional[DataAccessLog]:
        """Get data access log by ID."""
        result = await self.db.execute(
            select(DataAccessLog).where(DataAccessLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    async def get_unauthorized_accesses(
        self,
        days: int = 30,
        limit: int = 100
    ) -> List[DataAccessLog]:
        """Get unauthorized access attempts."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(DataAccessLog)
            .where(
                and_(
                    DataAccessLog.was_authorized == False,
                    DataAccessLog.accessed_at >= start_date
                )
            )
            .order_by(desc(DataAccessLog.accessed_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_access_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get data access summary."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(DataAccessLog).where(DataAccessLog.accessed_at >= start_date)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            return {
                "total_accesses": 0,
                "unauthorized_accesses": 0,
                "accesses_by_method": {},
                "accesses_by_operation": {},
                "accesses_by_actor": {}
            }
        
        unauthorized = sum(1 for log in logs if not log.was_authorized)
        
        accesses_by_method = {}
        accesses_by_operation = {}
        accesses_by_actor = {}
        
        for log in logs:
            accesses_by_method[log.access_method] = accesses_by_method.get(log.access_method, 0) + 1
            accesses_by_operation[log.operation] = accesses_by_operation.get(log.operation, 0) + 1
            
            actor_id_str = str(log.actor_id)
            accesses_by_actor[actor_id_str] = accesses_by_actor.get(actor_id_str, 0) + 1
        
        return {
            "total_accesses": len(logs),
            "unauthorized_accesses": unauthorized,
            "accesses_by_method": accesses_by_method,
            "accesses_by_operation": accesses_by_operation,
            "accesses_by_actor": accesses_by_actor
        }
