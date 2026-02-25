"""Unit tests for Issue Repository."""

import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.repositories.issue_repository import IssueRepository
from shared.schemas import IssueCreate, IssueUpdate, IssueStatus, IssuePriority

@pytest.mark.asyncio
async def test_create_issue(mock_db, sample_project_id, sample_creator_id):
    repo = IssueRepository(mock_db)
    issue_create = IssueCreate(
        project_id=sample_project_id,
        creator_id=sample_creator_id,
        title="Repo Test Issue",
        description="Repo Test Description",
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM
    )
    
    await repo.create(issue_create)
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_get_issue(mock_db, sample_issue_model):
    repo = IssueRepository(mock_db)
    
    # Mock result
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = sample_issue_model
    mock_db.execute.return_value = mock_result
    
    result = await repo.get(sample_issue_model.id)
    
    assert result == sample_issue_model
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_list_issues(mock_db, sample_issue_model):
    repo = IssueRepository(mock_db)
    
    # Mock result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_issue_model]
    mock_db.execute.return_value = mock_result
    
    result = await repo.list(skip=0, limit=10)
    
    assert len(result) == 1
    assert result[0] == sample_issue_model

@pytest.mark.asyncio
async def test_update_issue(mock_db, sample_issue_model):
    repo = IssueRepository(mock_db)
    
    # Mock get
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = sample_issue_model
    mock_db.execute.return_value = mock_result
    
    issue_update = IssueUpdate(title="Updated Title")
    result = await repo.update(sample_issue_model.id, issue_update)
    
    assert result.title == "Updated Title"
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_issue(mock_db, sample_issue_model):
    repo = IssueRepository(mock_db)
    
    # Mock get
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = sample_issue_model
    mock_db.execute.return_value = mock_result
    
    result = await repo.delete(sample_issue_model.id)
    
    assert result is True
    mock_db.delete.assert_called_once_with(sample_issue_model)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_issue_not_found(mock_db):
    repo = IssueRepository(mock_db)
    
    # Mock get returns None
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result
    
    result = await repo.delete(uuid4())
    
    assert result is False
    mock_db.delete.assert_not_called()
