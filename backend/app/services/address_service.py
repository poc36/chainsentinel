"""Address analysis service — core analysis pipeline."""

from datetime import datetime, timezone
from decimal import Decimal
from collections import Counter

from app.domain.blockchain import Chain, detect_chain, validate_address, get_chain_info
from app.domain.address_classifier import classify_address
from app.providers.base import ProviderTransaction
from app.providers.factory import get_provider
from app.schemas.address import (
    AddressFullAnalysis,
    AddressProfileResponse,
    TransactionResponse,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AddressService:
    """Service for comprehensive blockchain address analysis.

    Orchestrates the full analysis pipeline:
    1. Chain detection and validation
    2. Balance and transaction data fetching
    3. Statistical computation
    4. Activity pattern analysis
    """

    async def analyze(
        self,
        address: str,
        chain_hint: str | None = None,
        depth: int = 1,
    ) -> AddressProfileResponse:
        """Perform full address analysis.

        Args:
            address: Blockchain address to analyze.
            chain_hint: Optional chain hint to skip auto-detection.
            depth: Analysis depth for graph exploration.

        Returns:
            Complete address profile with all computed metrics.

        Raises:
            ValueError: If address format is invalid or chain unknown.
        """
        # Step 1: Detect chain
        if chain_hint:
            chain = Chain(chain_hint)
        else:
            chain = detect_chain(address)
            if chain is None:
                raise ValueError(f"Could not detect blockchain for address: {address}")

        # Step 2: Validate
        if not validate_address(address, chain):
            raise ValueError(f"Invalid {chain} address format: {address}")

        logger.info("address_analysis_started", address=address[:12], chain=chain)

        # Step 3: Fetch data from provider
        provider = get_provider()
        addr_info = await provider.get_address_info(address, chain)
        transactions = await provider.get_transactions(address, chain, limit=50)

        # Step 4: Classify address
        classification = classify_address(address, chain)

        # Step 5: Compute statistics
        stats = self._compute_statistics(address, transactions)
        activity = self._compute_activity_patterns(transactions)

        # Step 6: Build profile
        chain_info = get_chain_info(chain)
        total_tx = addr_info.tx_count

        profile = AddressProfileResponse(
            id=__import__("uuid").uuid4(),
            address=address,
            chain=chain,
            address_type=classification.address_type,
            is_valid=True,
            balance_native=addr_info.balance,
            balance_usd=addr_info.balance_usd,
            tx_in_count=stats["tx_in_count"],
            tx_out_count=stats["tx_out_count"],
            total_tx_count=total_tx,
            first_seen=addr_info.first_seen,
            last_seen=addr_info.last_seen,
            avg_tx_value=stats["avg_tx_value"],
            max_tx_value=stats["max_tx_value"],
            min_tx_value=stats["min_tx_value"],
            unique_counterparties=stats["unique_counterparties"],
            most_active_hours=activity["most_active_hours"],
            most_active_days=activity["most_active_days"],
            avg_holding_time_hours=stats["avg_holding_time"],
            balance_change_30d=stats["balance_change_30d"],
            activity_trend=activity["trend"],
            label=classification.label,
            entity_type=classification.address_type,
            analyzed_at=datetime.now(timezone.utc),
        )

        logger.info(
            "address_analysis_completed",
            address=address[:12],
            chain=chain,
            risk_factors_count=0,
        )

        return profile

    def _compute_statistics(
        self,
        address: str,
        transactions: list[ProviderTransaction],
    ) -> dict:
        """Compute transaction statistics.

        Args:
            address: The analyzed address.
            transactions: List of transactions.

        Returns:
            Dictionary with computed stats.
        """
        if not transactions:
            return {
                "tx_in_count": 0,
                "tx_out_count": 0,
                "avg_tx_value": Decimal("0"),
                "max_tx_value": Decimal("0"),
                "min_tx_value": Decimal("0"),
                "unique_counterparties": 0,
                "avg_holding_time": Decimal("0"),
                "balance_change_30d": Decimal("0"),
            }

        addr_lower = address.lower()
        incoming = [t for t in transactions if t.to_address.lower() == addr_lower]
        outgoing = [t for t in transactions if t.from_address.lower() == addr_lower]

        all_amounts = [t.amount_usd for t in transactions if t.amount_usd > 0]
        counterparties: set[str] = set()
        for t in transactions:
            if t.from_address.lower() != addr_lower:
                counterparties.add(t.from_address.lower())
            if t.to_address.lower() != addr_lower:
                counterparties.add(t.to_address.lower())

        avg_value = (
            sum(all_amounts) / len(all_amounts) if all_amounts else Decimal("0")
        )
        max_value = max(all_amounts) if all_amounts else Decimal("0")
        min_value = min(all_amounts) if all_amounts else Decimal("0")

        # Estimate average holding time
        holding_times: list[float] = []
        sorted_txs = sorted(
            transactions, key=lambda t: t.block_time or datetime.min.replace(tzinfo=timezone.utc)
        )
        for i in range(len(sorted_txs) - 1):
            if sorted_txs[i].block_time and sorted_txs[i + 1].block_time:
                delta = sorted_txs[i + 1].block_time - sorted_txs[i].block_time
                holding_times.append(delta.total_seconds() / 3600)

        avg_holding = (
            Decimal(str(round(sum(holding_times) / len(holding_times), 2)))
            if holding_times
            else Decimal("0")
        )

        # Balance change over last 30 days
        now = datetime.now(timezone.utc)
        recent_in = sum(
            t.amount_usd
            for t in incoming
            if t.block_time and (now - t.block_time).days <= 30
        )
        recent_out = sum(
            t.amount_usd
            for t in outgoing
            if t.block_time and (now - t.block_time).days <= 30
        )
        balance_change = recent_in - recent_out

        return {
            "tx_in_count": len(incoming),
            "tx_out_count": len(outgoing),
            "avg_tx_value": round(avg_value, 2),
            "max_tx_value": round(max_value, 2),
            "min_tx_value": round(min_value, 2),
            "unique_counterparties": len(counterparties),
            "avg_holding_time": avg_holding,
            "balance_change_30d": round(balance_change, 2),
        }

    def _compute_activity_patterns(
        self,
        transactions: list[ProviderTransaction],
    ) -> dict:
        """Compute activity pattern analysis.

        Args:
            transactions: List of transactions.

        Returns:
            Dictionary with activity patterns.
        """
        if not transactions:
            return {
                "most_active_hours": [],
                "most_active_days": [],
                "trend": "unknown",
            }

        hour_counter: Counter[int] = Counter()
        day_counter: Counter[str] = Counter()
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for tx in transactions:
            if tx.block_time:
                hour_counter[tx.block_time.hour] += 1
                day_counter[day_names[tx.block_time.weekday()]] += 1

        # Top 3 most active hours
        active_hours = [h for h, _ in hour_counter.most_common(3)]

        # Top 3 most active days
        active_days = [d for d, _ in day_counter.most_common(3)]

        # Activity trend
        now = datetime.now(timezone.utc)
        recent_txs = [
            t for t in transactions
            if t.block_time and (now - t.block_time).days <= 30
        ]
        older_txs = [
            t for t in transactions
            if t.block_time and 30 < (now - t.block_time).days <= 60
        ]

        if len(recent_txs) > len(older_txs) * 1.2:
            trend = "increasing"
        elif len(recent_txs) < len(older_txs) * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "most_active_hours": active_hours,
            "most_active_days": active_days,
            "trend": trend,
        }

    def transactions_to_response(
        self,
        transactions: list[ProviderTransaction],
    ) -> list[TransactionResponse]:
        """Convert provider transactions to response schema.

        Args:
            transactions: Provider transaction objects.

        Returns:
            List of TransactionResponse schemas.
        """
        return [
            TransactionResponse(
                id=__import__("uuid").uuid4(),
                tx_hash=tx.tx_hash,
                chain=tx.chain,
                from_address=tx.from_address,
                to_address=tx.to_address,
                amount=tx.amount,
                amount_usd=tx.amount_usd,
                token=tx.token,
                fee=tx.fee,
                fee_usd=tx.fee_usd,
                block_number=tx.block_number,
                block_time=tx.block_time,
                status=tx.status,
                tx_type=tx.tx_type,
            )
            for tx in transactions
        ]
