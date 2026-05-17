import pytest
from unittest.mock import patch
from src.consumers.issue_events import process_issue_event
from src.consumers.comment_events import process_comment_event

@patch("src.consumers.issue_events.send_email")
@patch("src.consumers.issue_events.send_in_app")
def test_process_issue_event(mock_send_in_app, mock_send_email):
    event_data = {
        "event_type": "issue.created",
        "issue_id": "ISSUE-123",
        "user_id": "user-1"
    }
    
    # Run the celery task synchronously using .apply()
    result = process_issue_event.apply(args=[event_data])
    
    assert result.status == "SUCCESS"
    assert result.result["status"] == "success"
    mock_send_email.assert_called_once()
    mock_send_in_app.assert_called_once()


@patch("src.consumers.comment_events.send_email")
@patch("src.consumers.comment_events.send_in_app")
def test_process_comment_event(mock_send_in_app, mock_send_email):
    event_data = {
        "event_type": "comment.created",
        "issue_id": "ISSUE-123",
        "mentions": ["user-1", "user-2"]
    }
    
    result = process_comment_event.apply(args=[event_data])
    
    assert result.status == "SUCCESS"
    assert result.result["status"] == "success"
    assert mock_send_email.call_count == 2
    assert mock_send_in_app.call_count == 2
