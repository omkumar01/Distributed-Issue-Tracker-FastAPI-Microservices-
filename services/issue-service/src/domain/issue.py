"""
Issue Aggregate Domain Logic.
Handles business rules for the Issue entity.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from shared.schemas import IssueStatus, IssuePriority
from src.domain.workflow import WorkflowService
from src.domain.sla import SLAService

class IssueAggregate:
    """
    Domain aggregate for Issue.
    Encapsulates business logic, validation, and invariants.
    """

    def __init__(
        self,
        id: UUID,
        project_id: UUID,
        creator_id: UUID,
        title: str,
        description: Optional[str] = None,
        status: IssueStatus = IssueStatus.TODO,
        priority: IssuePriority = IssuePriority.MEDIUM,
        assignee_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.project_id = project_id
        self.creator_id = creator_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.assignee_id = assignee_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_details(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[IssuePriority] = None,
        assignee_id: Optional[UUID] = None
    ) -> None:
        """Update issue details."""
        if title:
            self.title = title
        if description is not None:
            self.description = description
        if priority:
            self.priority = priority
        if assignee_id is not None:
            self.assignee_id = assignee_id
        
        self.updated_at = datetime.utcnow()

    def transition_status(self, new_status: IssueStatus) -> None:
        """
        Transition issue to a new status.
        Raises ValueError if transition is invalid.
        """
        if not WorkflowService.is_transition_allowed(self.status, new_status):
            raise ValueError(f"Invalid transition from {self.status} to {new_status}")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def get_sla_due_date(self) -> datetime:
        """Calculate the SLA due date based on creation time and priority."""
        sla_delta = SLAService.get_expected_resolution_time(self.priority)
        return self.created_at + sla_delta

    def is_overdue(self) -> bool:
        """Check if the issue is past its SLA due date."""
        if self.status in [IssueStatus.DONE, IssueStatus.CLOSED]:
            return False
        return datetime.utcnow() > self.get_sla_due_date()

    def assign_to(self, user_id: UUID) -> None:
        """Assign issue to a user."""
        self.assignee_id = user_id
        self.updated_at = datetime.utcnow()

    def unassign(self) -> None:
        """Remove assignee."""
        self.assignee_id = None
        self.updated_at = datetime.utcnow()
