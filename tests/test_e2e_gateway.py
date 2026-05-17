import pytest
from httpx import AsyncClient
import asyncio

# This requires docker-compose to be running!
GATEWAY_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_gateway_health():
    async with AsyncClient(base_url=GATEWAY_URL) as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_gateway_services():
    async with AsyncClient(base_url=GATEWAY_URL) as client:
        resp = await client.get("/services")
        assert resp.status_code == 200
        services = resp.json().get("services", [])
        assert len(services) > 0

@pytest.mark.asyncio
async def test_create_user_via_gateway():
    async with AsyncClient(base_url=GATEWAY_URL) as client:
        # Route logic: /api/v1/users is handled by user-service
        resp = await client.post("/api/v1/users/", json={
            "email": "e2e@example.com",
            "full_name": "E2E User"
        })
        # Could fail if DB is down or already exists, handle gracefully
        assert resp.status_code in [201, 400], f"Failed with {resp.status_code}: {resp.text}"
        
        if resp.status_code == 201:
            assert resp.json()["email"] == "e2e@example.com"
