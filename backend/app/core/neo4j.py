"""Neo4j driver configuration for graph database operations."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

_driver: AsyncDriver | None = None


async def get_neo4j_driver() -> AsyncDriver:
    """Get or create the Neo4j async driver.

    Returns:
        AsyncDriver: Neo4j async driver instance.
    """
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_pool_size=50,
        )
        logger.info("neo4j_driver_created", uri=settings.neo4j_uri)
    return _driver


async def close_neo4j_driver() -> None:
    """Close the Neo4j driver connection."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
        logger.info("neo4j_driver_closed")


@asynccontextmanager
async def get_neo4j_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for Neo4j sessions.

    Yields:
        AsyncSession: Neo4j session for running queries.
    """
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        yield session


async def run_query(
    query: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a Cypher query and return results.

    Args:
        query: Cypher query string.
        parameters: Query parameters.

    Returns:
        List of result records as dictionaries.
    """
    async with get_neo4j_session() as session:
        result = await session.run(query, parameters or {})
        records = await result.data()
        return records


async def run_write_query(
    query: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a write Cypher query within a transaction.

    Args:
        query: Cypher write query string.
        parameters: Query parameters.

    Returns:
        List of result records as dictionaries.
    """
    async with get_neo4j_session() as session:

        async def _write_tx(tx: Any) -> list[dict[str, Any]]:
            result = await tx.run(query, parameters or {})
            return await result.data()

        return await session.execute_write(_write_tx)
