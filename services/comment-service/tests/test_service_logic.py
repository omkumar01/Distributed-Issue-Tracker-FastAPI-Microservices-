"""Tests for CommentService business logic."""

import pytest
from uuid import uuid4
from fastapi import HTTPException

from src.schemas.comment import CommentCreate, CommentUpdate
from shared.events.schemas import CommentCreated, CommentUpdated, CommentDeleted

@pytest.mark.asyncio
async def test_create_comment(comment_service, mock_repo, mock_publisher, sample_issue_id, sample_author_id, sample_comment_model):
    """Test creating a new comment."""
    create_data = CommentCreate(
        issue_id=sample_issue_id,
        content="New comment content"
    )
    
    mock_repo.create.return_value = sample_comment_model
    
    result = await comment_service.create_comment(create_data, sample_author_id)
    
    # Verify repository was called
    mock_repo.create.assert_called_once_with(create_data, sample_author_id)
    
    # Verify event was published
    mock_publisher.publish.assert_called_once()
    event_arg = mock_publisher.publish.call_args[0][0]
    assert isinstance(event_arg, CommentCreated)
    assert event_arg.issue_id == sample_issue_id
    assert event_arg.author_id == sample_author_id
    
    # Verify result
    assert result == sample_comment_model

@pytest.mark.asyncio
async def test_update_comment_success(comment_service, mock_repo, mock_publisher, sample_comment_model):
    """Test successful comment update."""
    update_data = CommentUpdate(
        content="Updated comment content"
    )
    
    mock_repo.get_by_id.return_value = sample_comment_model
    mock_repo.update.return_value = sample_comment_model
    
    result = await comment_service.update_comment(
        sample_comment_model.id, 
        update_data, 
        sample_comment_model.author_id
    )
    
    mock_repo.get_by_id.assert_called_once_with(sample_comment_model.id)
    mock_repo.update.assert_called_once_with(sample_comment_model, update_data)
    
    mock_publisher.publish.assert_called_once()
    event_arg = mock_publisher.publish.call_args[0][0]
    assert isinstance(event_arg, CommentUpdated)
    
    assert result == sample_comment_model

@pytest.mark.asyncio
async def test_update_comment_not_found(comment_service, mock_repo, sample_comment_id):
    """Test updating a non-existent comment."""
    update_data = CommentUpdate(content="Update")
    mock_repo.get_by_id.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await comment_service.update_comment(sample_comment_id, update_data, uuid4())
        
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_update_comment_unauthorized(comment_service, mock_repo, sample_comment_model):
    """Test updating a comment by someone other than the author."""
    update_data = CommentUpdate(content="Update")
    mock_repo.get_by_id.return_value = sample_comment_model
    
    wrong_user_id = uuid4()
    
    with pytest.raises(HTTPException) as exc_info:
        await comment_service.update_comment(sample_comment_model.id, update_data, wrong_user_id)
        
    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_delete_comment_success(comment_service, mock_repo, mock_publisher, sample_comment_model):
    """Test successful comment deletion."""
    mock_repo.get_by_id.return_value = sample_comment_model
    mock_repo.delete.return_value = True
    
    result = await comment_service.delete_comment(sample_comment_model.id, sample_comment_model.author_id)
    
    mock_repo.delete.assert_called_once_with(sample_comment_model.id)
    mock_publisher.publish.assert_called_once()
    event_arg = mock_publisher.publish.call_args[0][0]
    assert isinstance(event_arg, CommentDeleted)
    assert result is True
