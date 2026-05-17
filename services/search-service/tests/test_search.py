import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from src.main import app

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
@patch("src.api.search.async_es_client.search", new_callable=AsyncMock)
async def test_search_endpoint(mock_search, client):
    # Mock the ES response
    mock_search.return_value = {
        "hits": {
            "hits": [
                {
                    "_index": "issues",
                    "_source": {
                        "id": "ISS-123",
                        "title": "Critical Bug",
                        "description": "Fix the parser."
                    }
                }
            ]
        }
    }
    
    response = await client.get("/api/v1/search/?q=parser")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == "ISS-123"
    assert results[0]["_index"] == "issues"

@pytest.mark.asyncio
@patch("src.main.async_es_client.ping", new_callable=AsyncMock)
async def test_healthcheck(mock_ping, client):
    mock_ping.return_value = True
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
