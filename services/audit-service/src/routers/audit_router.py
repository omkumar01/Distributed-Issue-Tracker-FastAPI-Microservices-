"""Audit Service routers."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from src.database import get_session
from src.schemas.audit import (
    AuditLogResponse, AuditLogCreate, AuditLogFilterParams,
    ComplianceEventResponse, ComplianceEventCreate,
    DataAccessLogResponse, DataAccessLogCreate, DataAccessSummary
)
from src.services.audit_service import (
    AuditLogService, ComplianceEventService, DataAccessService
)
from src.repositories.audit_repository import (
    AuditLogRepository, ComplianceEventRepository,
    DataAccessLogRepository
)
from shared.utils.exceptions import ApplicationException

router = APIRouter()


# ============ Audit Log Endpoints ============

@router.post("", response_model=AuditLogResponse, status_code=201, tags=["audit-logs"])
async def create_audit_log(
    log_data: AuditLogCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new audit log entry."""
    try:
        repository = AuditLogRepository(db)
        service = AuditLogService(repository)
        return await service.create_log(log_data)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/logs/{log_id}", response_model=AuditLogResponse, tags=["audit-logs"])
async def get_audit_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get audit log by ID."""
    try:
        repository = AuditLogRepository(db)
        service = AuditLogService(repository)
        return await service.get_log(log_id)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/logs", response_model=dict, tags=["audit-logs"])
async def list_audit_logs(
    actor_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[UUID] = Query(None),
    service: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    """List audit logs with optional filters."""
    try:
        filters = AuditLogFilterParams(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            service=service,
            status=status,
            skip=skip,
            limit=limit
        )
        repository = AuditLogRepository(db)
        service_instance = AuditLogService(repository)
        return await service_instance.list_logs(filters)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/resource/{resource_id}", tags=["audit-logs"])
async def get_resource_audit_history(
    resource_id: UUID,
    resource_type: str = Query(...),
    db: AsyncSession = Depends(get_session)
):
    """Get complete audit history for a resource."""
    try:
        repository = AuditLogRepository(db)
        service = AuditLogService(repository)
        return await service.get_resource_history(resource_id, resource_type)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/user/{actor_id}/activity", tags=["audit-logs"])
async def get_user_activity(
    actor_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get recent activity for a user."""
    try:
        repository = AuditLogRepository(db)
        service = AuditLogService(repository)
        logs = await service.get_user_activity(actor_id)
        return {"items": logs, "total": len(logs)}
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/stats", tags=["audit-logs"])
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_session)
):
    """Get audit statistics."""
    try:
        repository = AuditLogRepository(db)
        service = AuditLogService(repository)
        return await service.get_stats(days)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ============ Compliance Event Endpoints ============

@router.post("/compliance", response_model=ComplianceEventResponse, status_code=201, tags=["compliance"])
async def create_compliance_event(
    event_data: ComplianceEventCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new compliance event."""
    try:
        repository = ComplianceEventRepository(db)
        service = ComplianceEventService(repository)
        return await service.create_event(event_data)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/compliance/{event_id}", response_model=ComplianceEventResponse, tags=["compliance"])
async def get_compliance_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get compliance event by ID."""
    try:
        repository = ComplianceEventRepository(db)
        service = ComplianceEventService(repository)
        return await service.get_event(event_id)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/compliance", response_model=dict, tags=["compliance"])
async def list_compliance_events(
    severity: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    """List compliance events."""
    try:
        repository = ComplianceEventRepository(db)
        service = ComplianceEventService(repository)
        return await service.list_events(severity, event_type, skip, limit)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ============ Data Access Log Endpoints ============

@router.post("/data-access", response_model=DataAccessLogResponse, status_code=201, tags=["data-access"])
async def log_data_access(
    access_data: DataAccessLogCreate,
    db: AsyncSession = Depends(get_session)
):
    """Log a data access event."""
    try:
        repository = DataAccessLogRepository(db)
        service = DataAccessService(repository)
        return await service.log_access(access_data)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/data-access/unauthorized", tags=["data-access"])
async def get_unauthorized_accesses(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_session)
):
    """Get unauthorized data access attempts."""
    try:
        repository = DataAccessLogRepository(db)
        service = DataAccessService(repository)
        logs = await service.get_unauthorized_accesses(days, limit)
        return {"items": logs, "total": len(logs)}
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/data-access/summary", response_model=DataAccessSummary, tags=["data-access"])
async def get_data_access_summary(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_session)
):
    """Get data access summary."""
    try:
        repository = DataAccessLogRepository(db)
        service = DataAccessService(repository)
        return await service.get_summary(days)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/data-access/{log_id}", response_model=DataAccessLogResponse, tags=["data-access"])
async def get_data_access_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get data access log by ID."""
    try:
        repository = DataAccessLogRepository(db)
        service = DataAccessService(repository)
        return await service.get_log(log_id)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
