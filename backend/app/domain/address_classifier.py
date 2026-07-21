"""Address type classification logic."""

from dataclasses import dataclass
from app.domain.blockchain import Chain


@dataclass
class AddressClassification:
    """Result of address type classification.

    Attributes:
        address_type: Detected type (eoa, contract, multisig, exchange, defi, bridge, mixer).
        confidence: Confidence level (0-1).
        label: Human-readable label if known entity.
        entity_name: Known entity name.
    """

    address_type: str
    confidence: float
    label: str | None = None
    entity_name: str | None = None


# Known exchange addresses (subset for demo)
KNOWN_EXCHANGES: dict[str, str] = {
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance Hot Wallet",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance Hot Wallet 2",
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance Hot Wallet 3",
    "0x56eddb7aa87536c09ccc2793473599fd21a8b17f": "Binance Hot Wallet 14",
    "0x5041ed759dd4afc3a72b8192c143f72f4724081a": "OKX",
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase",
    "0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43": "Coinbase 2",
    "0xe3114084b730C6a3B34b1e841c2b8D8336F89B2B": "Gate.io",
    "0xd24400ae8bfebb18ca49be86258a3c749cf46853": "Gemini",
    "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13": "Kraken",
    "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "Kraken 2",
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa": "Satoshi Nakamoto (Genesis)",
    "3FHNBLobJnbCTFTVakh5TXmEneyf5PT61B": "Binance BTC Cold",
    "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h": "Binance BTC Hot",
    "TLyqzVGLV1srkB7dToTAEQgDSFPny3M2he": "Binance TRX",
}

# Known mixer/privacy addresses
KNOWN_MIXERS: dict[str, str] = {
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash Router",
    "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": "Tornado Cash 0.1 ETH",
    "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936": "Tornado Cash 1 ETH",
    "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": "Tornado Cash 10 ETH",
    "0xa160cdab225685da1d56aa342ad8841c3b53f291": "Tornado Cash 100 ETH",
}

# Known DeFi protocols
KNOWN_DEFI: dict[str, str] = {
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2 Router",
    "0xe592427a0aece92de3edee1f18e0157c05861564": "Uniswap V3 Router",
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": "Uniswap V3 Router 2",
    "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f": "SushiSwap Router",
    "0x1111111254fb6c44bAC0beD2854e76F90643097d": "1inch V4 Router",
}


def classify_address(address: str, chain: Chain) -> AddressClassification:
    """Classify a blockchain address type.

    Checks against known entity databases and applies heuristics
    to determine the address type.

    Args:
        address: The blockchain address.
        chain: The blockchain network.

    Returns:
        AddressClassification with type and confidence.
    """
    addr_lower = address.lower()

    # Check known exchanges
    if addr_lower in KNOWN_EXCHANGES or address in KNOWN_EXCHANGES:
        label = KNOWN_EXCHANGES.get(addr_lower) or KNOWN_EXCHANGES.get(address, "Exchange")
        return AddressClassification(
            address_type="exchange",
            confidence=0.99,
            label=label,
            entity_name=label.split(" ")[0] if label else None,
        )

    # Check known mixers
    if addr_lower in KNOWN_MIXERS:
        label = KNOWN_MIXERS[addr_lower]
        return AddressClassification(
            address_type="mixer",
            confidence=0.99,
            label=label,
            entity_name="Tornado Cash" if "Tornado" in label else "Unknown Mixer",
        )

    # Check known DeFi
    if addr_lower in KNOWN_DEFI:
        label = KNOWN_DEFI[addr_lower]
        return AddressClassification(
            address_type="defi",
            confidence=0.95,
            label=label,
            entity_name=label.split(" ")[0] if label else None,
        )

    # Default: EOA for most chains
    if chain in (Chain.BITCOIN, Chain.LITECOIN, Chain.DOGECOIN):
        return AddressClassification(
            address_type="utxo_address",
            confidence=0.7,
        )

    return AddressClassification(
        address_type="eoa",
        confidence=0.6,
    )
