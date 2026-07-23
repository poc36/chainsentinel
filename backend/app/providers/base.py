"""Abstract blockchain data provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.blockchain import Chain


@dataclass
class ProviderAddressInfo:
    """Raw address information from a blockchain provider.

    Attributes:
        address: The blockchain address.
        chain: The blockchain network.
        balance: Balance in native currency.
        balance_usd: Balance in USD.
        tx_count: Total transaction count.
        is_contract: Whether address is a smart contract.
        first_seen: First on-chain activity.
        last_seen: Last on-chain activity.
        token_balances: List of token balances.
    """

    address: str
    chain: Chain
    balance: Decimal = Decimal("0")
    balance_usd: Decimal = Decimal("0")
    tx_count: int = 0
    is_contract: bool = False
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    token_balances: list["TokenBalance"] = field(default_factory=list)


@dataclass
class TokenBalance:
    """Token balance for an address."""

    token_symbol: str
    token_name: str
    balance: Decimal
    balance_usd: Decimal
    contract_address: str | None = None


@dataclass
class ProviderTransaction:
    """Raw transaction data from a blockchain provider.

    Attributes:
        tx_hash: Transaction hash.
        chain: Blockchain network.
        from_address: Sender address.
        to_address: Receiver address.
        amount: Amount in native currency.
        amount_usd: Amount in USD.
        token: Token symbol.
        fee: Transaction fee.
        fee_usd: Fee in USD.
        block_number: Block number.
        block_time: Block timestamp.
        status: Transaction status.
        tx_type: Transaction type.
    """

    tx_hash: str
    chain: Chain
    from_address: str
    to_address: str
    amount: Decimal = Decimal("0")
    amount_usd: Decimal = Decimal("0")
    token: str = "ETH"
    fee: Decimal = Decimal("0")
    fee_usd: Decimal = Decimal("0")
    block_number: int = 0
    block_time: datetime | None = None
    status: str = "confirmed"
    tx_type: str = "transfer"


class BlockchainProvider(ABC):
    """Abstract interface for blockchain data providers.

    Implementations:
    - DemoProvider: Generates deterministic synthetic data for demo/testing.
    - EthereumProvider: Fetches real data from Etherscan/Alchemy.
    - BitcoinProvider: Fetches real data from Blockstream.
    """

    @abstractmethod
    async def get_address_info(self, address: str, chain: Chain) -> ProviderAddressInfo:
        """Fetch address information from the blockchain.

        Args:
            address: The blockchain address.
            chain: The blockchain network.

        Returns:
            ProviderAddressInfo with balance, tx count, etc.
        """
        ...

    @abstractmethod
    async def get_transactions(
        self,
        address: str,
        chain: Chain,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProviderTransaction]:
        """Fetch transactions for an address.

        Args:
            address: The blockchain address.
            chain: The blockchain network.
            limit: Max number of transactions to fetch.
            offset: Pagination offset.

        Returns:
            List of ProviderTransaction objects.
        """
        ...

    @abstractmethod
    async def get_token_balances(self, address: str, chain: Chain) -> list[TokenBalance]:
        """Fetch token balances for an address.

        Args:
            address: The blockchain address.
            chain: The blockchain network.

        Returns:
            List of TokenBalance objects.
        """
        ...

    @abstractmethod
    async def get_price_usd(self, chain: Chain) -> Decimal:
        """Get current price of the chain's native currency in USD.

        Args:
            chain: The blockchain network.

        Returns:
            Price in USD.
        """
        ...
