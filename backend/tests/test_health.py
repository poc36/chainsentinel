"""Health check endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    """Test that the health check endpoint returns 200 with healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_version(client):
    """Test that the health check returns the application version."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_docs_accessible(client):
    """Test that the OpenAPI docs are accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_schema(client):
    """Test that the OpenAPI schema is accessible."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == "ChainSentinel"
