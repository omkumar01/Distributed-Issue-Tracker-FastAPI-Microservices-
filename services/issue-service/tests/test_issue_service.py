"""Unit tests for Issue Service logic."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.services.issue_service import IssueService
from shared.schemas import IssueCreate, IssueStatus, IssuePriority, IssueUpdate

@pytest.mark.asyncio
async def test_create_issue_publishes_event(issue_service, mock_repo, mock_publisher, sample_project_id, sample_creator_id):
    """Test that creating an issue publishes an event."""
    issue_create = IssueCreate(
        project_id=sample_project_id,
        creator_id=sample_creator_id,
        title="Test Issue",
        priority=IssuePriority.HIGH,
        description="Test Description"
    )
    
    # Mock repo response
    mock_issue = MagicMock()
    mock_issue.id = uuid4()
    mock_issue.project_id = sample_project_id
    mock_issue.creator_id = sample_creator_id
    mock_issue.title = issue_create.title
    mock_issue.description = issue_create.description
    mock_issue.status = IssueStatus.TODO
    mock_issue.priority = issue_create.priority
    
    mock_repo.create.return_value = mock_issue
    
    # Act
    result = await issue_service.create_issue(issue_create)
    
    # Assert
    assert result.title == "Test Issue"
    mock_repo.create.assert_called_once()
    mock_publisher.publish.assert_called_once()
    
    # Check event
    event = mock_publisher.publish.call_args[0][0]
    assert event.event_type == "issue.created"
    assert event.issue_id == mock_issue.id

@pytest.mark.asyncio
async def test_update_issue_status_transition(issue_service, mock_repo, mock_publisher, sample_issue_model):
    """Test status transition logic and event publishing."""
    issue_id = sample_issue_model.id
    sample_issue_model.status = IssueStatus.TODO
    
    mock_repo.get.return_value = sample_issue_model
    
    # Mock updated issue (IN_PROGRESS)
    updated_issue_obj = MagicMock()
    updated_issue_obj.id = issue_id
    updated_issue_obj.status = IssueStatus.IN_PROGRESS
    updated_issue_obj.project_id = sample_issue_model.project_id
    updated_issue_obj.creator_id = sample_issue_model.creator_id
    
    mock_repo.update.return_value = updated_issue_obj
    
    # Act: Update status to IN_PROGRESS
    update_data = IssueUpdate(status=IssueStatus.IN_PROGRESS)
    result = await issue_service.update_issue(issue_id, update_data)
    
    # Assert
    assert result.status == IssueStatus.IN_PROGRESS
    
    # Check events - should publish status changed and general update
    assert mock_publisher.publish.call_count >= 1
    events = [call[0][0].event_type for call in mock_publisher.publish.call_args_list]
    assert "issue.status_changed" in events
    assert "issue.updated" in events

@pytest.mark.asyncio
async def test_invalid_transition(issue_service, mock_repo, sample_issue_model):
    """Test that invalid transition raises error."""
    issue_id = sample_issue_model.id
    sample_issue_model.status = IssueStatus.TODO
    mock_repo.get.return_value = sample_issue_model
    
    # Act: Try to transition to DONE (invalid from TODO)
    with pytest.raises(ValueError, match="Invalid transition"):
        await issue_service.update_issue(issue_id, IssueUpdate(status=IssueStatus.DONE))

@pytest.mark.asyncio
async def test_get_issue(issue_service, mock_repo, sample_issue_model):
    """Test get_issue."""
    mock_repo.get.return_value = sample_issue_model
    
    result = await issue_service.get_issue(sample_issue_model.id)
    assert result == sample_issue_model
    mock_repo.get.assert_called_once_with(sample_issue_model.id)

@pytest.mark.asyncio
async def test_list_issues(issue_service, mock_repo, sample_issue_model):
    """Test list_issues."""
    mock_repo.list.return_value = [sample_issue_model]
    
    result = await issue_service.list_issues(skip=0, limit=5)
    assert len(result) == 1
    assert result[0] == sample_issue_model
    mock_repo.list.assert_called_once_with(0, 5)

@pytest.mark.asyncio
async def test_delete_issue(issue_service, mock_repo, mock_publisher, sample_issue_model):
    """Test delete_issue and event publishing."""
    mock_repo.get.return_value = sample_issue_model
    mock_repo.delete.return_value = True
    
    result = await issue_service.delete_issue(sample_issue_model.id)
    
    assert result is True
    mock_repo.delete.assert_called_once_with(sample_issue_model.id)
    
    # Verify event
    mock_publisher.publish.assert_called_once()
    event = mock_publisher.publish.call_args[0][0]
    assert event.event_type == "issue.deleted"
    assert event.issue_id == sample_issue_model.id

@pytest.mark.asyncio
async def test_delete_issue_not_found(issue_service, mock_repo, mock_publisher):
    """Test delete_issue when not found."""
    mock_repo.get.return_value = None
    
    result = await issue_service.delete_issue(uuid4())
    
    assert result is False
    mock_repo.delete.assert_not_called()
    mock_publisher.publish.assert_not_called()
