"""Audit Service - Database models."""

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

Base = declarative_base()


class AuditLog(Base):
    """Audit log entry model."""
    
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Actor & Action
    actor_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    
    # Resource
    resource_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    
    # Change tracking
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)
    
    # Status and details
    status = Column(String(50), default="success", nullable=False)  # success, failure, warning
    error_message = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    service = Column(String(100), nullable=False, index=True)
    
    # Related IDs for context
    project_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    issue_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_actor_action', 'actor_id', 'action'),
        Index('idx_resource_type', 'resource_type', 'resource_id'),
        Index('idx_service_created', 'service', 'created_at'),
        Index('idx_project_created', 'project_id', 'created_at'),
    )


class ComplianceEvent(Base):
    """Compliance-related events for regulatory requirements."""
    
    __tablename__ = "compliance_events"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), default="info", nullable=False)  # critical, high, medium, low, info
    
    # Who did what
    actor_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    
    # Resource affected
    resource_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    resource_type = Column(String(100), nullable=True)
    
    # Details
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Retention & status
    is_deleted = Column(Boolean, default=False, nullable=False)
    retention_days = Column(String(50), default="permanent")  # Number of days or "permanent"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    __table_args__ = (
        Index('idx_event_type_severity', 'event_type', 'severity'),
        Index('idx_actor_event', 'actor_id', 'event_type'),
    )


class DataAccessLog(Base):
    """Track sensitive data access for security and compliance."""
    
    __tablename__ = "data_access_logs"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Who accessed
    actor_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    
    # What was accessed
    resource_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    fields_accessed = Column(JSON, nullable=True)  # List of field names accessed
    
    # How it was accessed
    access_method = Column(String(50), nullable=False)  # api, batch, internal, export
    operation = Column(String(50), nullable=False)  # read, update, delete, export
    
    # Context
    ip_address = Column(String(45), nullable=True)
    purpose = Column(String(255), nullable=True)
    
    # Status
    was_authorized = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_actor_resource', 'actor_id', 'resource_id'),
        Index('idx_resource_accessed', 'resource_type', 'accessed_at'),
    )
