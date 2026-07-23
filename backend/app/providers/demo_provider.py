"""Demo blockchain data provider with deterministic synthetic data.

Generates realistic-looking blockchain data based on address hashes.
The same address always produces the same data — crucial for testing and demos.
"""

import hashlib
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.blockchain import Chain, get_chain_info
from app.providers.base import (
    BlockchainProvider,
    ProviderAddressInfo,
    ProviderTransaction,
    TokenBalance,
)

# Mock USD prices for demo
DEMO_PRICES: dict[Chain, Decimal] = {
    Chain.BITCOIN: Decimal("67500.00"),
    Chain.ETHEREUM: Decimal("3450.00"),
    Chain.TRON: Decimal("0.125"),
    Chain.BNB: Decimal("580.00"),
    Chain.POLYGON: Decimal("0.72"),
    Chain.ARBITRUM: Decimal("3450.00"),
    Chain.OPTIMISM: Decimal("3450.00"),
    Chain.BASE: Decimal("3450.00"),
    Chain.SOLANA: Decimal("172.00"),
    Chain.LITECOIN: Decimal("82.00"),
    Chain.DOGECOIN: Decimal("0.135"),
}

# Token pools for each chain
CHAIN_TOKENS: dict[Chain, list[dict]] = {
    Chain.ETHEREUM: [
        {"symbol": "USDT", "name": "Tether", "price": 1.0},
        {"symbol": "USDC", "name": "USD Coin", "price": 1.0},
        {"symbol": "DAI", "name": "Dai", "price": 1.0},
        {"symbol": "LINK", "name": "Chainlink", "price": 15.50},
        {"symbol": "UNI", "name": "Uniswap", "price": 9.80},
        {"symbol": "AAVE", "name": "Aave", "price": 105.00},
        {"symbol": "WBTC", "name": "Wrapped Bitcoin", "price": 67500.00},
    ],
    Chain.BNB: [
        {"symbol": "BUSD", "name": "Binance USD", "price": 1.0},
        {"symbol": "CAKE", "name": "PancakeSwap", "price": 2.80},
        {"symbol": "XVS", "name": "Venus", "price": 8.50},
    ],
    Chain.POLYGON: [
        {"symbol": "USDT", "name": "Tether", "price": 1.0},
        {"symbol": "AAVE", "name": "Aave", "price": 105.00},
        {"symbol": "QUICK", "name": "QuickSwap", "price": 52.00},
    ],
    Chain.TRON: [
        {"symbol": "USDT", "name": "Tether (TRC20)", "price": 1.0},
        {"symbol": "USDD", "name": "Decentralized USD", "price": 1.0},
    ],
    Chain.SOLANA: [
        {"symbol": "USDC", "name": "USD Coin", "price": 1.0},
        {"symbol": "RAY", "name": "Raydium", "price": 1.85},
        {"symbol": "JTO", "name": "Jito", "price": 3.20},
    ],
}

# Counterparty address pools
EVM_COUNTERPARTIES = [
    "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",
    "0xdef1c0ded9bec7f1a1670819833240f027b25eff",
    "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
    "0x514910771af9ca656af840dff83e8264ecf986ca",
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "0x6b175474e89094c44da98b954eedeac495271d0f",
    "0x28c6c06298d514db089934071355e5743bf21d60",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549",
    "0x5041ed759dd4afc3a72b8192c143f72f4724081a",
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",
]

BTC_COUNTERPARTIES = [
    "3FHNBLobJnbCTFTVakh5TXmEneyf5PT61B",
    "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h",
    "1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF",
    "bc1qa5wkgaew2dkv56kc6hp3n0fvzrhpdf0ljdswe2",
    "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
    "1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ",
]


def _addr_seed(address: str) -> int:
    """Generate a deterministic seed from an address hash."""
    return int(hashlib.sha256(address.encode()).hexdigest(), 16)


def _addr_rng(address: str) -> random.Random:
    """Create a seeded random generator for deterministic demo data."""
    return random.Random(_addr_seed(address))


class DemoProvider(BlockchainProvider):
    """Demo blockchain provider generating realistic synthetic data.

    Data is deterministic: the same address always produces the same results.
    This enables consistent testing and demo presentations.
    """

    async def get_address_info(self, address: str, chain: Chain) -> ProviderAddressInfo:
        """Generate synthetic address info based on address hash."""
        rng = _addr_rng(address)
        price = DEMO_PRICES.get(chain, Decimal("1.0"))

        # Generate balance based on address characteristics
        balance_tier = rng.choices(
            [0, 1, 2, 3, 4],
            weights=[5, 30, 40, 20, 5],
            k=1,
        )[0]
        balance_ranges = [
            (Decimal("0"), Decimal("0.01")),
            (Decimal("0.01"), Decimal("1")),
            (Decimal("1"), Decimal("100")),
            (Decimal("100"), Decimal("10000")),
            (Decimal("10000"), Decimal("500000")),
        ]
        low, high = balance_ranges[balance_tier]
        balance = Decimal(str(round(rng.uniform(float(low), float(high)), 6)))
        balance_usd = round(balance * price, 2)

        tx_count = rng.randint(5, 2000)
        days_active = rng.randint(30, 1800)
        first_seen = datetime.now(UTC) - timedelta(days=days_active)
        last_seen = datetime.now(UTC) - timedelta(hours=rng.randint(1, 72))

        token_balances = await self.get_token_balances(address, chain)

        return ProviderAddressInfo(
            address=address,
            chain=chain,
            balance=balance,
            balance_usd=balance_usd,
            tx_count=tx_count,
            is_contract=rng.random() < 0.1,
            first_seen=first_seen,
            last_seen=last_seen,
            token_balances=token_balances,
        )

    async def get_transactions(
        self,
        address: str,
        chain: Chain,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProviderTransaction]:
        """Generate synthetic transactions for the given address."""
        rng = _addr_rng(address + str(offset))
        chain_info = get_chain_info(chain)
        price = DEMO_PRICES.get(chain, Decimal("1.0"))
        transactions: list[ProviderTransaction] = []

        is_evm = chain_info.is_evm
        counterparties = EVM_COUNTERPARTIES if is_evm else BTC_COUNTERPARTIES

        now = datetime.now(UTC)

        for i in range(min(limit, 50)):
            is_outgoing = rng.random() < 0.45
            amount = Decimal(str(round(rng.uniform(0.001, 50.0), 6)))
            amount_usd = round(amount * price, 2)
            fee = Decimal(str(round(rng.uniform(0.0001, 0.02), 6)))
            fee_usd = round(fee * price, 2)

            counterparty = rng.choice(counterparties)
            block_time = now - timedelta(
                hours=rng.randint(1, 4320),
                minutes=rng.randint(0, 59),
            )

            # Determine token
            native = chain_info.symbol
            tokens_pool = CHAIN_TOKENS.get(chain, [])
            if tokens_pool and rng.random() < 0.3:
                token_info = rng.choice(tokens_pool)
                token = token_info["symbol"]
                # Adjust amount for token
                amount = Decimal(str(round(rng.uniform(10, 50000), 2)))
                amount_usd = round(amount * Decimal(str(token_info["price"])), 2)
            else:
                token = native

            tx_hash = hashlib.sha256(f"{address}{i}{offset}{counterparty}".encode()).hexdigest()
            if is_evm:
                tx_hash = "0x" + tx_hash

            tx_types = ["transfer", "swap", "contract_call", "transfer"]
            tx_type = rng.choice(tx_types)

            transactions.append(
                ProviderTransaction(
                    tx_hash=tx_hash,
                    chain=chain,
                    from_address=address if is_outgoing else counterparty,
                    to_address=counterparty if is_outgoing else address,
                    amount=amount,
                    amount_usd=amount_usd,
                    token=token,
                    fee=fee,
                    fee_usd=fee_usd,
                    block_number=rng.randint(15000000, 20000000),
                    block_time=block_time,
                    status="confirmed",
                    tx_type=tx_type,
                )
            )

        # Sort by block time descending
        transactions.sort(key=lambda t: t.block_time or now, reverse=True)
        return transactions

    async def get_token_balances(self, address: str, chain: Chain) -> list[TokenBalance]:
        """Generate synthetic token balances."""
        rng = _addr_rng(address + "tokens")
        tokens_pool = CHAIN_TOKENS.get(chain, [])

        if not tokens_pool:
            return []

        num_tokens = rng.randint(0, min(5, len(tokens_pool)))
        selected = rng.sample(tokens_pool, num_tokens)
        balances: list[TokenBalance] = []

        for token in selected:
            balance = Decimal(str(round(rng.uniform(1, 100000), 2)))
            balances.append(
                TokenBalance(
                    token_symbol=token["symbol"],
                    token_name=token["name"],
                    balance=balance,
                    balance_usd=round(balance * Decimal(str(token["price"])), 2),
                )
            )

        return balances

    async def get_price_usd(self, chain: Chain) -> Decimal:
        """Return mock USD price for the chain's native currency."""
        return DEMO_PRICES.get(chain, Decimal("1.0"))
