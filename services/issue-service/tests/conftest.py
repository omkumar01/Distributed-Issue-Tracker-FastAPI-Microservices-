"""Issue Service test fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.repositories.issue_repository import IssueRepository
from src.services.issue_service import IssueService
from src.events.publisher import EventPublisher
from shared.schemas import IssueStatus, IssuePriority

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_publisher():
    return MagicMock(spec=EventPublisher)

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def issue_service(mock_repo, mock_publisher):
    return IssueService(mock_repo, mock_publisher)

@pytest.fixture
def sample_issue_id():
    return uuid4()

@pytest.fixture
def sample_project_id():
    return uuid4()

@pytest.fixture
def sample_creator_id():
    return uuid4()

@pytest.fixture
def sample_issue_model(sample_issue_id, sample_project_id, sample_creator_id):
    mock_issue = MagicMock()
    mock_issue.id = sample_issue_id
    mock_issue.project_id = sample_project_id
    mock_issue.creator_id = sample_creator_id
    mock_issue.title = "Sample Issue"
    mock_issue.description = "Sample Description"
    mock_issue.status = IssueStatus.TODO
    mock_issue.priority = IssuePriority.MEDIUM
    mock_issue.assignee_id = None
    mock_issue.created_at = datetime.utcnow()
    mock_issue.updated_at = datetime.utcnow()
    return mock_issue
