"""
Integration tests for health checks.
"""

import pytest


@pytest.mark.integration
async def test_auth_service_health(async_client):
    """Test auth service health check endpoint."""
    # response = await async_client.get("http://localhost:8001/health")
    # assert response.status_code == 200
    # assert response.json()["status"] == "healthy"
    pass


@pytest.mark.integration
async def test_user_service_health(async_client):
    """Test user service health check endpoint."""
    pass


@pytest.mark.integration
async def test_project_service_health(async_client):
    """Test project service health check endpoint."""
    pass


@pytest.mark.integration
async def test_issue_service_health(async_client):
    """Test issue service health check endpoint."""
    pass
