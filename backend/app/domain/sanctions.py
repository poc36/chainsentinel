"""Sanctions list management — OFAC, EU, UK sanctions checking."""

import json
from dataclasses import dataclass
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SanctionsMatch:
    """Result of a sanctions list check.

    Attributes:
        is_sanctioned: Whether the address is on a sanctions list.
        lists: Names of matching sanctions lists.
        entity_name: Name of the sanctioned entity if known.
        program: Sanctions program (e.g., "CYBER2", "SDGT").
        details: Additional match details.
    """

    is_sanctioned: bool
    lists: list[str]
    entity_name: str | None = None
    program: str | None = None
    details: dict | None = None


# Sanctioned addresses (known OFAC-designated crypto addresses)
SANCTIONED_ADDRESSES: dict[str, dict] = {
    # Tornado Cash (OFAC designated Aug 2022)
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": {
        "entity": "Tornado Cash",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": {
        "entity": "Tornado Cash",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936": {
        "entity": "Tornado Cash",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": {
        "entity": "Tornado Cash",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    "0xa160cdab225685da1d56aa342ad8841c3b53f291": {
        "entity": "Tornado Cash",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    # Sinbad (OFAC designated Nov 2023)
    "0x722122df12d4e14e13ac3b6895a86e84145b6967": {
        "entity": "Sinbad.io",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    # Lazarus Group (North Korea)
    "0x098b716b8aaf21512996dc57eb0615e2383e2f96": {
        "entity": "Lazarus Group",
        "lists": ["OFAC", "EU_SANCTIONS", "UK_SANCTIONS"],
        "program": "DPRK",
    },
    "0xa0e1c89ef1a489c9c7de96311ed5ce5d32c20e4b": {
        "entity": "Lazarus Group",
        "lists": ["OFAC"],
        "program": "DPRK",
    },
    # Garantex (Russian exchange)
    "0x6f1ca141a28907f78ebaa64fb83a9088b02a8352": {
        "entity": "Garantex",
        "lists": ["OFAC", "EU_SANCTIONS"],
        "program": "RUSSIA-EO14024",
    },
    # Blender.io
    "0x5f6c97c6ad7bdd0ae7e0dd4ca33a4ed3fdabd4d7": {
        "entity": "Blender.io",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
    # Bitcoin sanctioned addresses
    "12QtD5BFwRsdNsAZY76UVE1xyCGNTojH9h": {
        "entity": "Lazarus Group (BTC)",
        "lists": ["OFAC"],
        "program": "DPRK",
    },
    "1KYiKJEfdJtap9QX2v9BXJMpz2SfU4pgZw": {
        "entity": "SamSam Ransomware",
        "lists": ["OFAC"],
        "program": "CYBER2",
    },
}


class SanctionsChecker:
    """Service for checking addresses against sanctions lists.

    Supports OFAC SDN, EU Consolidated, and UK HMT sanctions lists.
    Uses an in-memory hash set for O(1) lookups.
    """

    def __init__(self) -> None:
        self._addresses: dict[str, dict] = {}
        self._load_sanctions()

    def _load_sanctions(self) -> None:
        """Load sanctions data from embedded list and data files."""
        # Load embedded sanctioned addresses
        for addr, info in SANCTIONED_ADDRESSES.items():
            self._addresses[addr.lower()] = info

        # Try loading additional data files
        data_dir = Path(__file__).parent.parent.parent / "data" / "sanctions"
        for file_name in ["ofac_sdn.json", "eu_sanctions.json", "uk_sanctions.json"]:
            file_path = data_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        for entry in data.get("addresses", []):
                            self._addresses[entry["address"].lower()] = {
                                "entity": entry.get("entity", "Unknown"),
                                "lists": entry.get("lists", [file_name.split("_")[0].upper()]),
                                "program": entry.get("program"),
                            }
                    logger.info(
                        "sanctions_loaded",
                        file=file_name,
                        count=len(data.get("addresses", [])),
                    )
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning("sanctions_load_error", file=file_name, error=str(e))

        logger.info("sanctions_total_loaded", count=len(self._addresses))

    def check(self, address: str) -> SanctionsMatch:
        """Check an address against all sanctions lists.

        Args:
            address: Blockchain address to check.

        Returns:
            SanctionsMatch indicating whether the address is sanctioned.
        """
        addr_lower = address.lower()
        match_info = self._addresses.get(addr_lower)

        if match_info:
            return SanctionsMatch(
                is_sanctioned=True,
                lists=match_info.get("lists", ["UNKNOWN"]),
                entity_name=match_info.get("entity"),
                program=match_info.get("program"),
                details=match_info,
            )

        return SanctionsMatch(is_sanctioned=False, lists=[])

    def check_counterparties(self, addresses: list[str]) -> list[SanctionsMatch]:
        """Check multiple addresses for sanctions exposure.

        Args:
            addresses: List of blockchain addresses.

        Returns:
            List of SanctionsMatch for sanctioned addresses only.
        """
        matches = []
        for addr in addresses:
            result = self.check(addr)
            if result.is_sanctioned:
                matches.append(result)
        return matches

    @property
    def total_entries(self) -> int:
        """Total number of sanctioned addresses loaded."""
        return len(self._addresses)


# Singleton instance
_checker: SanctionsChecker | None = None


def get_sanctions_checker() -> SanctionsChecker:
    """Get or create the sanctions checker singleton.

    Returns:
        SanctionsChecker instance.
    """
    global _checker
    if _checker is None:
        _checker = SanctionsChecker()
    return _checker
