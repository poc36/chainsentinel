"""Provider factory for creating blockchain data providers."""

from app.config import get_settings
from app.core.logging import get_logger
from app.providers.base import BlockchainProvider
from app.providers.demo_provider import DemoProvider

logger = get_logger(__name__)


def create_provider() -> BlockchainProvider:
    """Create a blockchain provider based on application settings.

    Returns:
        BlockchainProvider instance (Demo or Live).
    """
    settings = get_settings()

    if settings.provider_mode == "demo":
        logger.info("provider_created", mode="demo")
        return DemoProvider()

    # For live mode, could instantiate real providers here
    # For now, fallback to demo
    logger.warning("provider_fallback_to_demo", requested_mode=settings.provider_mode)
    return DemoProvider()


# Singleton provider instance
_provider: BlockchainProvider | None = None


def get_provider() -> BlockchainProvider:
    """Get or create the singleton blockchain provider.

    Returns:
        BlockchainProvider instance.
    """
    global _provider
    if _provider is None:
        _provider = create_provider()
    return _provider
