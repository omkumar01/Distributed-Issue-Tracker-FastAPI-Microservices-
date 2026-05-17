import pytest
from unittest.mock import patch

@pytest.mark.asyncio
@patch("src.api.users.publish_event")
async def test_create_user(mock_publish, client):
    response = await client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "full_name": "Test User"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    
    mock_publish.assert_called_once()
    assert mock_publish.call_args[0][0] == "user.created"

@pytest.mark.asyncio
async def test_create_team(client):
    response = await client.post("/api/v1/teams/", json={
        "name": "Backend Team"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Backend Team"
