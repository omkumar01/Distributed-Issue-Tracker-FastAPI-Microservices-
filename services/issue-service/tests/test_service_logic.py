"""Unit tests for domain logic."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from shared.schemas import IssueStatus, IssuePriority
from src.domain.issue import IssueAggregate
from src.domain.workflow import WorkflowService
from src.domain.sla import SLAService

def test_workflow_transitions_exhaustive():
    """Test workflow transitions for all common paths."""
    # Valid transitions from TODO
    assert WorkflowService.is_transition_allowed(IssueStatus.TODO, IssueStatus.IN_PROGRESS)
    assert WorkflowService.is_transition_allowed(IssueStatus.TODO, IssueStatus.CLOSED)
    # Invalid transitions from TODO
    assert not WorkflowService.is_transition_allowed(IssueStatus.TODO, IssueStatus.DONE)
    assert not WorkflowService.is_transition_allowed(IssueStatus.TODO, IssueStatus.IN_REVIEW)

    # From IN_PROGRESS
    assert WorkflowService.is_transition_allowed(IssueStatus.IN_PROGRESS, IssueStatus.IN_REVIEW)
    assert WorkflowService.is_transition_allowed(IssueStatus.IN_PROGRESS, IssueStatus.TODO)
    assert WorkflowService.is_transition_allowed(IssueStatus.IN_PROGRESS, IssueStatus.CLOSED)
    assert not WorkflowService.is_transition_allowed(IssueStatus.IN_PROGRESS, IssueStatus.DONE)

    # From IN_REVIEW
    assert WorkflowService.is_transition_allowed(IssueStatus.IN_REVIEW, IssueStatus.DONE)
    assert WorkflowService.is_transition_allowed(IssueStatus.IN_REVIEW, IssueStatus.IN_PROGRESS)
    
    # From DONE
    assert WorkflowService.is_transition_allowed(IssueStatus.DONE, IssueStatus.IN_PROGRESS)
    assert WorkflowService.is_transition_allowed(IssueStatus.DONE, IssueStatus.CLOSED)

def test_sla_calculation_all_priorities():
    """Test SLA calculation for all defined priorities."""
    assert SLAService.get_sla_hours(IssuePriority.URGENT) == 4
    assert SLAService.get_sla_hours(IssuePriority.HIGH) == 24
    assert SLAService.get_sla_hours(IssuePriority.MEDIUM) == 72
    assert SLAService.get_sla_hours(IssuePriority.LOW) == 168

def test_issue_creation():
    """Test issue creation in aggregate."""
    project_id = uuid4()
    creator_id = uuid4()
    issue = IssueAggregate(
        id=uuid4(),
        project_id=project_id,
        creator_id=creator_id,
        title="Test Issue",
        priority=IssuePriority.HIGH
    )
    assert issue.status == IssueStatus.TODO
    assert issue.priority == IssuePriority.HIGH
    assert issue.project_id == project_id
    assert issue.created_at is not None

def test_issue_transition_chain():
    """Test a valid chain of issue status transitions."""
    issue = IssueAggregate(
        id=uuid4(),
        project_id=uuid4(),
        creator_id=uuid4(),
        title="Test Issue"
    )
    # TODO -> IN_PROGRESS -> IN_REVIEW -> DONE -> CLOSED
    issue.transition_status(IssueStatus.IN_PROGRESS)
    assert issue.status == IssueStatus.IN_PROGRESS
    
    issue.transition_status(IssueStatus.IN_REVIEW)
    assert issue.status == IssueStatus.IN_REVIEW
    
    issue.transition_status(IssueStatus.DONE)
    assert issue.status == IssueStatus.DONE
    
    issue.transition_status(IssueStatus.CLOSED)
    assert issue.status == IssueStatus.CLOSED

def test_issue_invalid_transition_raises():
    """Test that invalid transition in aggregate raises ValueError."""
    issue = IssueAggregate(
        id=uuid4(),
        project_id=uuid4(),
        creator_id=uuid4(),
        title="Test Issue"
    )
    with pytest.raises(ValueError, match="Invalid transition"):
        issue.transition_status(IssueStatus.DONE)

def test_issue_overdue_and_not_overdue():
    """Test overdue calculation for different scenarios."""
    # Overdue urgent issue
    past_date = datetime.utcnow() - timedelta(hours=5)
    issue_urgent = IssueAggregate(
        id=uuid4(),
        project_id=uuid4(),
        creator_id=uuid4(),
        title="Urgent Issue",
        priority=IssuePriority.URGENT, # 4 hours SLA
        created_at=past_date
    )
    assert issue_urgent.is_overdue()

    # Not overdue urgent issue
    recent_date = datetime.utcnow() - timedelta(hours=2)
    issue_recent = IssueAggregate(
        id=uuid4(),
        project_id=uuid4(),
        creator_id=uuid4(),
        title="Recent Issue",
        priority=IssuePriority.URGENT,
        created_at=recent_date
    )
    assert not issue_recent.is_overdue()

    # Closed issue should not be overdue regardless of time
    issue_urgent.transition_status(IssueStatus.CLOSED)
    assert not issue_urgent.is_overdue()
