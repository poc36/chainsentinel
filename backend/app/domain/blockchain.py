"""Blockchain network definitions, address validation, and chain detection."""

import re
from dataclasses import dataclass
from enum import StrEnum


class Chain(StrEnum):
    """Supported blockchain networks."""

    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    TRON = "tron"
    BNB = "bnb"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    SOLANA = "solana"
    LITECOIN = "litecoin"
    DOGECOIN = "dogecoin"


@dataclass(frozen=True)
class ChainInfo:
    """Metadata for a blockchain network."""

    chain: Chain
    name: str
    symbol: str
    address_regex: str
    explorer_url: str
    decimals: int = 18
    is_evm: bool = False


# Chain registry with address format patterns
CHAIN_REGISTRY: dict[Chain, ChainInfo] = {
    Chain.BITCOIN: ChainInfo(
        chain=Chain.BITCOIN,
        name="Bitcoin",
        symbol="BTC",
        address_regex=r"^(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{25,90})$",
        explorer_url="https://blockstream.info/tx/",
        decimals=8,
    ),
    Chain.ETHEREUM: ChainInfo(
        chain=Chain.ETHEREUM,
        name="Ethereum",
        symbol="ETH",
        address_regex=r"^0x[a-fA-F0-9]{40}$",
        explorer_url="https://etherscan.io/tx/",
        is_evm=True,
    ),
    Chain.TRON: ChainInfo(
        chain=Chain.TRON,
        name="Tron",
        symbol="TRX",
        address_regex=r"^T[a-zA-Z0-9]{33}$",
        explorer_url="https://tronscan.org/#/transaction/",
        decimals=6,
    ),
    Chain.BNB: ChainInfo(
        chain=Chain.BNB,
        name="BNB Chain",
        symbol="BNB",
        address_regex=r"^0x[a-fA-F0-9]{40}$",
        explorer_url="https://bscscan.com/tx/",
        is_evm=True,
    ),
    Chain.POLYGON: ChainInfo(
        chain=Chain.POLYGON,
        name="Polygon",
        symbol="MATIC",
        address_regex=r"^0x[a-fA-F0-9]{40}$",
        explorer_url="https://polygonscan.com/tx/",
        is_evm=True,
    ),
    Chain.ARBITRUM: ChainInfo(
        chain=Chain.ARBITRUM,
        name="Arbitrum",
        symbol="ETH",
        address_regex=r"^0x[a-fA-F0-9]{40}$",
        explorer_url="https://arbiscan.io/tx/",
        is_evm=True,
    ),
    Chain.OPTIMISM: ChainInfo(
        chain=Chain.OPTIMISM,
        name="Optimism",
        symbol="ETH",
        address_regex=r"^0x[a-fA-F0-9]{40}$",
        explorer_url="https://optimistic.etherscan.io/tx/",
        is_evm=True,
    ),
    Chain.BASE: ChainInfo(
        chain=Chain.BASE,
        name="Base",
        symbol="ETH",
        address_regex=r"^0x[a-fA-F0-9]{40}$",
        explorer_url="https://basescan.org/tx/",
        is_evm=True,
    ),
    Chain.SOLANA: ChainInfo(
        chain=Chain.SOLANA,
        name="Solana",
        symbol="SOL",
        address_regex=r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
        explorer_url="https://solscan.io/tx/",
        decimals=9,
    ),
    Chain.LITECOIN: ChainInfo(
        chain=Chain.LITECOIN,
        name="Litecoin",
        symbol="LTC",
        address_regex=r"^(L[a-km-zA-HJ-NP-Z1-9]{26,33}|M[a-km-zA-HJ-NP-Z1-9]{26,33}|ltc1[a-z0-9]{25,90})$",
        explorer_url="https://litecoinspace.org/tx/",
        decimals=8,
    ),
    Chain.DOGECOIN: ChainInfo(
        chain=Chain.DOGECOIN,
        name="Dogecoin",
        symbol="DOGE",
        address_regex=r"^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32}$",
        explorer_url="https://dogechain.info/tx/",
        decimals=8,
    ),
}


def validate_address(address: str, chain: Chain) -> bool:
    """Validate a blockchain address format for a specific chain.

    Args:
        address: The blockchain address to validate.
        chain: The target blockchain network.

    Returns:
        True if the address format is valid for the specified chain.
    """
    chain_info = CHAIN_REGISTRY.get(chain)
    if not chain_info:
        return False
    return bool(re.match(chain_info.address_regex, address))


def detect_chain(address: str) -> Chain | None:
    """Auto-detect the blockchain network from address format.

    Uses a priority-based matching strategy:
    1. Tron (T prefix, fixed length) — checked first to avoid Solana false match
    2. Bitcoin (1/3/bc1 prefix)
    3. Litecoin (L/M/ltc1 prefix)
    4. Dogecoin (D prefix)
    5. Solana (base58, 32-44 chars)
    6. EVM chains default to Ethereum (0x prefix)

    Args:
        address: The blockchain address.

    Returns:
        Detected Chain or None if unrecognizable.
    """
    if not address or len(address) < 10:
        return None

    # Tron: T prefix + 33 chars
    if address.startswith("T") and len(address) == 34 and validate_address(address, Chain.TRON):
        return Chain.TRON

    # Bitcoin: 1xx, 3xx, bc1xx
    if address.startswith(("1", "3", "bc1")) and validate_address(address, Chain.BITCOIN):
        return Chain.BITCOIN

    # Litecoin: L, M, ltc1
    if address.startswith(("L", "M", "ltc1")) and validate_address(address, Chain.LITECOIN):
        return Chain.LITECOIN

    # Dogecoin: D prefix
    if address.startswith("D") and len(address) == 34 and validate_address(address, Chain.DOGECOIN):
        return Chain.DOGECOIN

    # EVM chains: 0x prefix — default to Ethereum
    if address.startswith("0x") and len(address) == 42 and validate_address(address, Chain.ETHEREUM):
        return Chain.ETHEREUM

    # Solana: base58, 32-44 chars (checked last)
    if 32 <= len(address) <= 44 and not address.startswith("0x") and validate_address(address, Chain.SOLANA):
        return Chain.SOLANA

    return None


def get_chain_info(chain: Chain) -> ChainInfo:
    """Get metadata for a blockchain network.

    Args:
        chain: The blockchain network.

    Returns:
        ChainInfo with network metadata.

    Raises:
        ValueError: If chain is not supported.
    """
    info = CHAIN_REGISTRY.get(chain)
    if not info:
        raise ValueError(f"Unsupported chain: {chain}")
    return info


def get_all_chains() -> list[ChainInfo]:
    """Get metadata for all supported chains.

    Returns:
        List of ChainInfo for all supported networks.
    """
    return list(CHAIN_REGISTRY.values())
