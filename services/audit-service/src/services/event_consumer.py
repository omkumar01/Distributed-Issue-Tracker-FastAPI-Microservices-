"""Event consumer for Audit Service."""

import asyncio
import json
import logging
from typing import Callable, Dict, Any
from uuid import uuid4
import pika
from pika.adapters.asyncio_connection import AsyncioConnection

from src.repositories.audit_repository import AuditLogRepository, ComplianceEventRepository
from src.schemas.audit import (
    AuditLogCreate, ComplianceEventCreate, AuditStatusEnum
)
from shared.events.schemas import (
    UserCreated, UserUpdated, UserDeleted,
    ProjectCreated, ProjectUpdated, ProjectDeleted,
    IssueCreated, IssueUpdated, IssueStatusChanged, IssueDeleted,
    CommentCreated, CommentUpdated, CommentDeleted,
    AuditEvent
)
from shared.core import get_settings

logger = logging.getLogger(__name__)


class AuditEventConsumer:
    """Consume events from RabbitMQ and create audit logs."""
    
    def __init__(self, repo: AuditLogRepository, settings):
        self.repo = repo
        self.settings = settings
        self.connection = None
        self.channel = None
        self.handlers: Dict[str, Callable] = {
            "user.created": self.handle_user_created,
            "user.updated": self.handle_user_updated,
            "user.deleted": self.handle_user_deleted,
            "project.created": self.handle_project_created,
            "project.updated": self.handle_project_updated,
            "project.deleted": self.handle_project_deleted,
            "issue.created": self.handle_issue_created,
            "issue.updated": self.handle_issue_updated,
            "issue.status_changed": self.handle_issue_status_changed,
            "issue.deleted": self.handle_issue_deleted,
            "comment.created": self.handle_comment_created,
            "comment.updated": self.handle_comment_updated,
            "comment.deleted": self.handle_comment_deleted,
            "audit.event": self.handle_audit_event,
        }
    
    async def connect(self):
        """Connect to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                self.settings.RABBITMQ_USER,
                self.settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=self.settings.RABBITMQ_HOST,
                port=self.settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = AsyncioConnection(
                parameters,
                on_open_callback=self.on_connection_open
            )
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def on_connection_open(self, connection):
        """Handle connection open."""
        logger.info("RabbitMQ connection opened")
        self.channel = connection.channel(on_open_callback=self.on_channel_open)
    
    async def on_channel_open(self, channel):
        """Handle channel open."""
        logger.info("RabbitMQ channel opened")
        
        # Declare exchange and queues
        channel.exchange_declare('audit.events', 'topic', durable=True)
        
        # Create queue for audit service
        channel.queue_declare('audit-service-queue', durable=True)
        
        # Bind routing keys
        routing_keys = [
            'user.*',
            'project.*',
            'issue.*',
            'comment.*',
            'audit.*'
        ]
        
        for key in routing_keys:
            channel.queue_bind('audit-service-queue', 'audit.events', key)
        
        # Start consuming
        channel.basic_consume(
            'audit-service-queue',
            on_message_callback=self.on_message
        )
        logger.info("Audit service consumer started")
    
    async def on_message(self, channel, method, properties, body):
        """Handle incoming message."""
        try:
            message = json.loads(body)
            event_type = message.get("event_type")
            
            handler = self.handlers.get(event_type)
            if handler:
                await handler(message)
            else:
                logger.warning(f"No handler for event type: {event_type}")
            
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    # ============ Event Handlers ============
    
    async def handle_user_created(self, event: Dict[str, Any]):
        """Handle user.created event."""
        log_data = AuditLogCreate(
            actor_id=event.get("user_id"),
            action="create",
            resource_id=event.get("user_id"),
            resource_type="user",
            new_values=event.get("data", {}),
            status=AuditStatusEnum.SUCCESS,
            service=event.get("service", "user-service")
        )
        await self.repo.create(log_data)
        logger.info(f"Logged user creation: {event.get('user_id')}")
    
    async def handle_user_updated(self, event: Dict[str, Any]):
        """Handle user.updated event."""
        log_data = AuditLogCreate(
            actor_id=event.get("user_id"),
            action="update",
            resource_id=event.get("user_id"),
            resource_type="user",
            changes=event.get("changes", {}),
            status=AuditStatusEnum.SUCCESS,
            service=event.get("service", "user-service")
        )
        await self.repo.create(log_data)
    
    async def handle_user_deleted(self, event: Dict[str, Any]):
        """Handle user.deleted event."""
        log_data = AuditLogCreate(
            actor_id=event.get("user_id"),
            action="delete",
            resource_id=event.get("user_id"),
            resource_type="user",
            status=AuditStatusEnum.SUCCESS,
            service=event.get("service", "user-service")
        )
        await self.repo.create(log_data)
    
    async def handle_project_created(self, event: Dict[str, Any]):
        """Handle project.created event."""
        log_data = AuditLogCreate(
            actor_id=event.get("owner_id"),
            action="create",
            resource_id=event.get("project_id"),
            resource_type="project",
            new_values=event.get("data", {}),
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            service=event.get("service", "project-service")
        )
        await self.repo.create(log_data)
    
    async def handle_project_updated(self, event: Dict[str, Any]):
        """Handle project.updated event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id"),
            action="update",
            resource_id=event.get("project_id"),
            resource_type="project",
            changes=event.get("changes", {}),
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            service=event.get("service", "project-service")
        )
        await self.repo.create(log_data)
    
    async def handle_project_deleted(self, event: Dict[str, Any]):
        """Handle project.deleted event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id"),
            action="delete",
            resource_id=event.get("project_id"),
            resource_type="project",
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            service=event.get("service", "project-service")
        )
        await self.repo.create(log_data)
    
    async def handle_issue_created(self, event: Dict[str, Any]):
        """Handle issue.created event."""
        log_data = AuditLogCreate(
            actor_id=event.get("creator_id"),
            action="create",
            resource_id=event.get("issue_id"),
            resource_type="issue",
            new_values=event.get("data", {}),
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            issue_id=event.get("issue_id"),
            service=event.get("service", "issue-service")
        )
        await self.repo.create(log_data)
    
    async def handle_issue_updated(self, event: Dict[str, Any]):
        """Handle issue.updated event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id"),
            action="update",
            resource_id=event.get("issue_id"),
            resource_type="issue",
            changes=event.get("changes", {}),
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            issue_id=event.get("issue_id"),
            service=event.get("service", "issue-service")
        )
        await self.repo.create(log_data)
    
    async def handle_issue_status_changed(self, event: Dict[str, Any]):
        """Handle issue.status_changed event."""
        log_data = AuditLogCreate(
            actor_id=event.get("changed_by"),
            action="update",
            resource_id=event.get("issue_id"),
            resource_type="issue",
            changes={
                "status": {
                    "old": event.get("old_status"),
                    "new": event.get("new_status")
                }
            },
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            issue_id=event.get("issue_id"),
            service=event.get("service", "issue-service")
        )
        await self.repo.create(log_data)
    
    async def handle_issue_deleted(self, event: Dict[str, Any]):
        """Handle issue.deleted event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id"),
            action="delete",
            resource_id=event.get("issue_id"),
            resource_type="issue",
            status=AuditStatusEnum.SUCCESS,
            project_id=event.get("project_id"),
            issue_id=event.get("issue_id"),
            service=event.get("service", "issue-service")
        )
        await self.repo.create(log_data)
    
    async def handle_comment_created(self, event: Dict[str, Any]):
        """Handle comment.created event."""
        log_data = AuditLogCreate(
            actor_id=event.get("author_id"),
            action="create",
            resource_id=event.get("comment_id"),
            resource_type="comment",
            new_values={"content": event.get("content")},
            status=AuditStatusEnum.SUCCESS,
            issue_id=event.get("issue_id"),
            service=event.get("service", "comment-service")
        )
        await self.repo.create(log_data)
    
    async def handle_comment_updated(self, event: Dict[str, Any]):
        """Handle comment.updated event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id"),
            action="update",
            resource_id=event.get("comment_id"),
            resource_type="comment",
            changes=event.get("changes", {}),
            status=AuditStatusEnum.SUCCESS,
            issue_id=event.get("issue_id"),
            service=event.get("service", "comment-service")
        )
        await self.repo.create(log_data)
    
    async def handle_comment_deleted(self, event: Dict[str, Any]):
        """Handle comment.deleted event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id"),
            action="delete",
            resource_id=event.get("comment_id"),
            resource_type="comment",
            status=AuditStatusEnum.SUCCESS,
            issue_id=event.get("issue_id"),
            service=event.get("service", "comment-service")
        )
        await self.repo.create(log_data)
    
    async def handle_audit_event(self, event: Dict[str, Any]):
        """Handle generic audit.event."""
        log_data = AuditLogCreate(
            actor_id=event.get("actor_id") or uuid4(), # Fallback for tests/incomplete events
            action=event.get("action", "custom"),
            resource_id=event.get("resource_id") or uuid4(),
            resource_type=event.get("resource_type", "generic"),
            changes=event.get("changes"),
            status=AuditStatusEnum.SUCCESS,
            service=event.get("service", "audit-service")
        )
        await self.repo.create(log_data)
    
    async def close(self):
        """Close connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Closed RabbitMQ connection")
