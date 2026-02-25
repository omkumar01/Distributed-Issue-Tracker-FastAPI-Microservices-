"""Comment Service test fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.repositories.comment_repository import CommentRepository
from src.services.comment_service import CommentService
from src.events.publisher import EventPublisher
from src.models.comment import CommentModel

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_publisher():
    return MagicMock(spec=EventPublisher)

@pytest.fixture
def mock_repo():
    return AsyncMock(spec=CommentRepository)

@pytest.fixture
def comment_service(mock_repo, mock_publisher):
    return CommentService(mock_repo, mock_publisher)

@pytest.fixture
def sample_comment_id():
    return uuid4()

@pytest.fixture
def sample_issue_id():
    return uuid4()

@pytest.fixture
def sample_author_id():
    return uuid4()

@pytest.fixture
def sample_comment_model(sample_comment_id, sample_issue_id, sample_author_id):
    mock_comment = MagicMock(spec=CommentModel)
    mock_comment.id = sample_comment_id
    mock_comment.issue_id = sample_issue_id
    mock_comment.author_id = sample_author_id
    mock_comment.content = "Sample Comment"
    mock_comment.mentions = []
    mock_comment.is_edited = False
    mock_comment.created_at = datetime.utcnow()
    mock_comment.updated_at = datetime.utcnow()
    return mock_comment
