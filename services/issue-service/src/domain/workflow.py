"""
Workflow domain logic.
Defines valid status transitions and rules.
"""

from typing import Dict, List, Set
from shared.schemas import IssueStatus

# Valid transitions map
# Key: Current Status
# Value: Set of allowed Next Statuses
TRANSITIONS: Dict[IssueStatus, Set[IssueStatus]] = {
    IssueStatus.BACKLOG: {IssueStatus.TODO, IssueStatus.CLOSED},
    IssueStatus.TODO: {IssueStatus.BACKLOG, IssueStatus.IN_PROGRESS, IssueStatus.CLOSED},
    IssueStatus.IN_PROGRESS: {IssueStatus.TODO, IssueStatus.IN_REVIEW, IssueStatus.CLOSED},
    IssueStatus.IN_REVIEW: {IssueStatus.IN_PROGRESS, IssueStatus.DONE, IssueStatus.CLOSED},
    IssueStatus.DONE: {IssueStatus.IN_PROGRESS, IssueStatus.CLOSED, IssueStatus.IN_REVIEW}, # Re-open or close
    IssueStatus.CLOSED: {IssueStatus.BACKLOG, IssueStatus.TODO} # Re-open
}

class WorkflowService:
    """Service to handle workflow transitions."""

    @staticmethod
    def get_allowed_transitions(current_status: IssueStatus) -> Set[IssueStatus]:
        """Get allowed next statuses for a given status."""
        return TRANSITIONS.get(current_status, set())

    @staticmethod
    def is_transition_allowed(current_status: IssueStatus, new_status: IssueStatus) -> bool:
        """Check if a transition is allowed."""
        if current_status == new_status:
            return True
        allowed = WorkflowService.get_allowed_transitions(current_status)
        return new_status in allowed
