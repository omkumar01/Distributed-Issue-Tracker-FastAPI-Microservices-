"""Mocked API tests for issue service."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.main import app
from src.routers.issue_router import get_service
from shared.schemas import IssueStatus, IssuePriority, IssueResponse

client = TestClient(app)

@pytest.fixture
def mock_issue_service():
    mock = AsyncMock()
    app.dependency_overrides[get_service] = lambda: mock
    yield mock
    app.dependency_overrides.clear()

def test_create_issue(mock_issue_service):
    """Test create issue endpoint."""
    issue_id = uuid4()
    mock_issue_service.create_issue.return_value = {
        "id": issue_id,
        "project_id": uuid4(),
        "creator_id": uuid4(),
        "title": "Test Issue",
        "description": "Desc",
        "status": IssueStatus.TODO,
        "priority": IssuePriority.MEDIUM,
        "assignee_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    response = client.post("/api/v1/issues", json={
        "project_id": str(uuid4()),
        "creator_id": str(uuid4()),
        "title": "Test Issue",
        "description": "Desc"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Issue"

def test_list_issues(mock_issue_service):
    """Test listing issues."""
    mock_issue_service.list_issues.return_value = []
    
    response = client.get("/api/v1/issues")
    assert response.status_code == 200
    assert response.json() == []

def test_get_issue(mock_issue_service):
    """Test get issue by ID."""
    issue_id = uuid4()
    mock_issue_service.get_issue.return_value = {
        "id": issue_id,
        "title": "Found Issue",
        "status": IssueStatus.TODO,
        "priority": IssuePriority.MEDIUM,
        "project_id": uuid4(),
        "creator_id": uuid4(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    response = client.get(f"/api/v1/issues/{issue_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Found Issue"

def test_get_issue_not_found(mock_issue_service):
    """Test get issue not found."""
    mock_issue_service.get_issue.return_value = None
    
    response = client.get(f"/api/v1/issues/{uuid4()}")
    assert response.status_code == 404

def test_update_issue(mock_issue_service):
    """Test update issue endpoint."""
    issue_id = uuid4()
    mock_issue_service.update_issue.return_value = {
        "id": issue_id,
        "title": "Updated Issue",
        "status": IssueStatus.IN_PROGRESS,
        "priority": IssuePriority.MEDIUM,
        "project_id": uuid4(),
        "creator_id": uuid4(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    response = client.put(f"/api/v1/issues/{issue_id}", json={"title": "Updated Issue", "status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Issue"

def test_delete_issue(mock_issue_service):
    """Test delete issue endpoint."""
    mock_issue_service.delete_issue.return_value = True
    
    response = client.delete(f"/api/v1/issues/{uuid4()}")
    assert response.status_code == 204

def test_transition_issue(mock_issue_service):
    """Test transition issue endpoint."""
    issue_id = uuid4()
    mock_issue_service.update_issue.return_value = {
        "id": issue_id,
        "status": IssueStatus.DONE,
        "title": "Done Issue",
        "priority": IssuePriority.MEDIUM,
        "project_id": uuid4(),
        "creator_id": uuid4(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    response = client.post(f"/api/v1/issues/{issue_id}/transition", params={"new_status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_workflow_transitions():
    """Test workflow transitions endpoint."""
    response = client.get("/api/v1/workflow/transitions", params={"current_status": "todo"})
    assert response.status_code == 200
    transitions = response.json()
    assert "in_progress" in transitions
    assert "done" not in transitions
