"""
Issue Service Logic.
Orchestrates repository operations and event publishing.
"""

from uuid import UUID
from typing import List, Optional, Any
from shared.events.schemas import (
    IssueCreated, 
    IssueUpdated, 
    IssueStatusChanged, 
    IssueDeleted
)
from shared.schemas import IssueCreate, IssueUpdate, IssueStatus
from src.repositories.issue_repository import IssueRepository
from src.events.publisher import EventPublisher
from src.domain.workflow import WorkflowService
from src.models.issue import IssueModel


class IssueService:
    """Service layer for Issue management."""

    def __init__(self, repo: IssueRepository, publisher: EventPublisher):
        self.repo = repo
        self.publisher = publisher

    async def create_issue(self, issue_create: IssueCreate) -> IssueModel:
        """Create an issue and publish event."""
        # Create in DB
        issue = await self.repo.create(issue_create)
        
        # Publish event
        # Note: In real app, we should handle transactions (outbox pattern)
        try:
            event = IssueCreated(
                issue_id=issue.id,
                project_id=issue.project_id,
                title=issue.title,
                creator_id=issue.creator_id,
                service="issue-service",
                data={
                    "priority": str(issue.priority),
                    "status": str(issue.status)
                }
            )
            self.publisher.publish(event)
        except Exception as e:
            # Log error but don't fail the request?
            # Or raise if critical. 
             pass
        
        return issue

    async def get_issue(self, issue_id: UUID) -> Optional[IssueModel]:
        """Get issue by ID."""
        return await self.repo.get(issue_id)

    async def list_issues(self, skip: int = 0, limit: int = 10) -> List[IssueModel]:
        """List issues."""
        return await self.repo.list(skip, limit)

    async def update_issue(self, issue_id: UUID, issue_update: IssueUpdate) -> Optional[IssueModel]:
        """Update issue and publish events."""
        # Get existing to check status change
        existing = await self.repo.get(issue_id)
        if not existing:
            return None
        
        old_status = existing.status
        
        # Check transition if status is being updated
        if issue_update.status and issue_update.status != existing.status:
             if not WorkflowService.is_transition_allowed(existing.status, issue_update.status):
                 raise ValueError(f"Invalid transition from {existing.status} to {issue_update.status}")

        updated = await self.repo.update(issue_id, issue_update)
        
        if updated:
            # Publish events
            try:
                # Status changed event
                if issue_update.status and str(issue_update.status.value) != str(old_status.value):
                    status_event = IssueStatusChanged(
                        issue_id=updated.id,
                        project_id=updated.project_id,
                        old_status=str(old_status.value),
                        new_status=str(updated.status.value),
                        changed_by=updated.creator_id, # FIXME: use context user
                        service="issue-service"
                    )
                    self.publisher.publish(status_event)
                
                # General update event
                changes = issue_update.model_dump(exclude_unset=True)
                if changes:
                    # Convert enums to values in changes dict if necessary
                    serialized_changes = {}
                    for k, v in changes.items():
                        if hasattr(v, 'value'):
                            serialized_changes[k] = str(v.value)
                        else:
                            serialized_changes[k] = str(v)

                    update_event = IssueUpdated(
                        issue_id=updated.id,
                        project_id=updated.project_id,
                        changes=serialized_changes,
                        service="issue-service"
                    )
                    self.publisher.publish(update_event)
            except Exception as e:
                # Log error in production
                pass
                
        return updated

    async def delete_issue(self, issue_id: UUID) -> bool:
        """Delete issue and publish event."""
        # Need to get project_id before delete to publish event
        issue = await self.repo.get(issue_id)
        if not issue:
            return False
            
        success = await self.repo.delete(issue_id)
        
        if success:
            try:
                event = IssueDeleted(
                    issue_id=issue_id,
                    project_id=issue.project_id,
                    service="issue-service"
                )
                self.publisher.publish(event)
            except Exception:
                pass
            
        return success
