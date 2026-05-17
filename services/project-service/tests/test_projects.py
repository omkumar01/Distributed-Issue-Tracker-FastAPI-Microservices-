import pytest
from unittest.mock import patch

@pytest.mark.asyncio
@patch("src.api.projects.publish_event")
async def test_create_project(mock_publish, client):
    response = await client.post("/api/v1/projects/", json={
        "name": "Test Project",
        "description": "Test Desc"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Desc"
    assert "id" in data
    
    mock_publish.assert_called_once()
    assert mock_publish.call_args[0][0] == "project.created"

@pytest.mark.asyncio
async def test_list_projects(client):
    # First create one
    await client.post("/api/v1/projects/", json={"name": "P1"})
    
    response = await client.get("/api/v1/projects/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == "P1"

@pytest.mark.asyncio
@patch("src.api.members.publish_event")
@patch("src.api.projects.publish_event")
async def test_add_member(mock_proj_pub, mock_mem_pub, client):
    # Create project
    proj_resp = await client.post("/api/v1/projects/", json={"name": "P2"})
    project_id = proj_resp.json()["id"]

    # Add member
    mem_resp = await client.post(f"/api/v1/projects/{project_id}/members", json={
        "user_id": "user123",
        "role": "admin"
    })
    
    assert mem_resp.status_code == 201
    assert mem_resp.json()["user_id"] == "user123"
    assert mem_resp.json()["role"] == "admin"
    
    mock_mem_pub.assert_called_once()
    
    # Test get members
    get_resp = await client.get(f"/api/v1/projects/{project_id}/members")
    assert len(get_resp.json()) == 1

@pytest.mark.asyncio
@patch("src.api.projects.publish_event")
async def test_permissions(mock_proj_pub, client):
    # Create project
    proj_resp = await client.post("/api/v1/projects/", json={"name": "P3"})
    project_id = proj_resp.json()["id"]

    # Add member (will just use direct DB or member endpoint)
    await client.post(f"/api/v1/projects/{project_id}/members", json={
        "user_id": "u99",
        "role": "viewer"
    })

    # Get permission
    perm_resp = await client.get(f"/api/v1/projects/{project_id}/permissions/u99")
    assert perm_resp.status_code == 200
    assert perm_resp.json()["role"] == "viewer"
