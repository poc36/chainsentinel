"""Test configuration and fixtures for ChainSentinel backend tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def app():
    """Create a test app instance with mocked infrastructure."""
    # Explicitly import submodules first to ensure they are registered in app.core
    import app.core.database
    import app.core.redis

    # Patch heavy infrastructure before importing app
    with (
        patch("app.core.database.engine") as mock_engine,
        patch("app.core.redis.redis_client") as mock_redis,
    ):
        # Mock engine.begin() context manager for lifespan startup
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_engine.dispose = AsyncMock()

        # Mock redis close
        mock_redis.close = AsyncMock()
        mock_redis.aclose = AsyncMock()

        from app.main import create_app

        test_app = create_app()
        yield test_app


@pytest.fixture
async def client(app):
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
