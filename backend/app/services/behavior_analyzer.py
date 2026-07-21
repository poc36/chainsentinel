"""Behavioral analysis service — pattern recognition and anomaly detection."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from collections import Counter

from app.providers.base import ProviderTransaction
from app.schemas.address import BehaviorAnalysisResponse, BehaviorFlag
from app.core.logging import get_logger

logger = get_logger(__name__)


class BehaviorAnalyzer:
    """Service for detecting behavioral patterns in transaction data.

    Analyzes transaction history to identify:
    - Anomalous transfers
    - Repeating patterns
    - Unusual timing
    - Suspicious splitting
    - Rapid withdrawals
    - Fund concentration
    - Exchange-like behavior
    """

    async def analyze(
        self,
        address: str,
        transactions: list[ProviderTransaction],
    ) -> BehaviorAnalysisResponse:
        """Perform comprehensive behavioral analysis.

        Args:
            address: The analyzed address.
            transactions: Transaction history.

        Returns:
            BehaviorAnalysisResponse with detected patterns.
        """
        addr_lower = address.lower()
        incoming = [t for t in transactions if t.to_address.lower() == addr_lower]
        outgoing = [t for t in transactions if t.from_address.lower() == addr_lower]
        flags: list[BehaviorFlag] = []

        # 1. Anomalous transfers
        anomalous_count = self._detect_anomalous_transfers(transactions)
        if anomalous_count > 0:
            flags.append(BehaviorFlag(
                code="ANOMALOUS_TRANSFERS",
                name="Anomalous Transfers",
                severity="medium",
                description=f"{anomalous_count} transfers deviate significantly from average",
                evidence={"count": anomalous_count},
            ))

        # 2. Repeating patterns
        patterns = self._detect_repeating_patterns(transactions)
        if patterns:
            flags.append(BehaviorFlag(
                code="REPEATING_PATTERNS",
                name="Repeating Transaction Patterns",
                severity="medium",
                description=f"Detected {len(patterns)} repeating patterns",
                evidence={"patterns": patterns},
            ))

        # 3. Unusual timing
        unusual_timing = self._detect_unusual_timing(transactions)
        if unusual_timing:
            flags.append(BehaviorFlag(
                code="UNUSUAL_TIMING",
                name="Unusual Activity Timing",
                severity="low",
                description="Majority of activity during unusual hours (midnight-5am UTC)",
                evidence={"night_percentage": unusual_timing},
            ))

        # 4. New counterparties
        new_cp_count = self._count_new_counterparties(address, transactions)

        # 5. Suspicious splitting
        suspicious_split = self._detect_splitting(outgoing)
        if suspicious_split:
            flags.append(BehaviorFlag(
                code="SUSPICIOUS_SPLITTING",
                name="Suspicious Fund Splitting",
                severity="high",
                description="Large incoming amounts immediately split into smaller outgoing txs",
                evidence=suspicious_split,
            ))

        # 6. Rapid withdrawal
        rapid = self._detect_rapid_withdrawal(incoming, outgoing)
        if rapid:
            flags.append(BehaviorFlag(
                code="RAPID_WITHDRAWAL",
                name="Rapid Fund Withdrawal",
                severity="high",
                description="Funds withdrawn within minutes of receipt",
                evidence=rapid,
            ))

        # 7. Fund concentration
        concentration = self._calculate_concentration(incoming)

        # 8. Exchange-like behavior
        probable_exchange = self._detect_exchange_behavior(incoming, outgoing)
        if probable_exchange:
            flags.append(BehaviorFlag(
                code="EXCHANGE_BEHAVIOR",
                name="Exchange-like Behavior",
                severity="low",
                description="Activity pattern resembles a centralized exchange",
            ))

        # 9. Same owner probability
        same_owner_prob = self._estimate_same_owner(transactions)

        return BehaviorAnalysisResponse(
            flags=flags,
            anomalous_transfers=anomalous_count,
            repeating_patterns=patterns,
            unusual_timing=unusual_timing > 50,
            new_counterparties=new_cp_count,
            suspicious_splitting=bool(suspicious_split),
            rapid_withdrawal=bool(rapid),
            fund_concentration=concentration,
            cluster_size=self._estimate_cluster_size(transactions),
            probable_exchange=probable_exchange,
            same_owner_probability=same_owner_prob,
        )

    def _detect_anomalous_transfers(
        self, transactions: list[ProviderTransaction]
    ) -> int:
        """Count transactions that deviate >3x from mean."""
        amounts = [float(t.amount_usd) for t in transactions if t.amount_usd > 0]
        if len(amounts) < 5:
            return 0
        avg = sum(amounts) / len(amounts)
        if avg == 0:
            return 0
        return sum(1 for a in amounts if a > avg * 3 or a < avg * 0.1)

    def _detect_repeating_patterns(
        self, transactions: list[ProviderTransaction]
    ) -> list[str]:
        """Detect repeating amount/timing patterns."""
        patterns: list[str] = []

        # Check for repeating amounts
        amount_counter: Counter[str] = Counter()
        for tx in transactions:
            rounded = str(round(float(tx.amount_usd), 0))
            amount_counter[rounded] += 1

        for amount, count in amount_counter.most_common(3):
            if count >= 3 and float(amount) > 10:
                patterns.append(f"Amount ${amount} appears {count} times")

        # Check for regular intervals
        sorted_txs = sorted(
            [t for t in transactions if t.block_time],
            key=lambda t: t.block_time,  # type: ignore
        )
        if len(sorted_txs) >= 5:
            intervals = []
            for i in range(len(sorted_txs) - 1):
                delta = (sorted_txs[i + 1].block_time - sorted_txs[i].block_time).total_seconds()  # type: ignore
                intervals.append(delta)

            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                consistent = sum(
                    1 for i in intervals if abs(i - avg_interval) < avg_interval * 0.3
                )
                if consistent > len(intervals) * 0.6 and avg_interval > 60:
                    hours = avg_interval / 3600
                    patterns.append(f"Regular interval pattern (~{hours:.1f}h between txs)")

        return patterns

    def _detect_unusual_timing(
        self, transactions: list[ProviderTransaction]
    ) -> float:
        """Return percentage of transactions occurring during unusual hours."""
        timed_txs = [t for t in transactions if t.block_time]
        if not timed_txs:
            return 0.0

        night_txs = sum(1 for t in timed_txs if 0 <= t.block_time.hour <= 5)  # type: ignore
        return round((night_txs / len(timed_txs)) * 100, 1)

    def _count_new_counterparties(
        self, address: str, transactions: list[ProviderTransaction]
    ) -> int:
        """Count counterparties appearing only in the last 7 days."""
        addr_lower = address.lower()
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=7)

        recent_cps: set[str] = set()
        old_cps: set[str] = set()

        for tx in transactions:
            cp = tx.to_address if tx.from_address.lower() == addr_lower else tx.from_address
            if tx.block_time and tx.block_time > cutoff:
                recent_cps.add(cp.lower())
            else:
                old_cps.add(cp.lower())

        return len(recent_cps - old_cps)

    def _detect_splitting(
        self, outgoing: list[ProviderTransaction]
    ) -> dict | None:
        """Detect fund splitting patterns."""
        if len(outgoing) < 4:
            return None

        sorted_out = sorted(
            [t for t in outgoing if t.block_time],
            key=lambda t: t.block_time,  # type: ignore
        )

        # Look for burst of outgoing txs within 1 hour
        for i in range(len(sorted_out) - 3):
            window = sorted_out[i: i + 4]
            if window[-1].block_time and window[0].block_time:
                time_span = (window[-1].block_time - window[0].block_time).total_seconds()
                if time_span < 3600:
                    total = sum(float(t.amount_usd) for t in window)
                    if total > 1000:
                        return {
                            "burst_count": 4,
                            "time_span_minutes": round(time_span / 60, 1),
                            "total_usd": round(total, 2),
                        }

        return None

    def _detect_rapid_withdrawal(
        self,
        incoming: list[ProviderTransaction],
        outgoing: list[ProviderTransaction],
    ) -> dict | None:
        """Detect funds being withdrawn quickly after receipt."""
        for tx_in in incoming:
            if not tx_in.block_time or tx_in.amount_usd < 100:
                continue
            for tx_out in outgoing:
                if not tx_out.block_time:
                    continue
                delta = (tx_out.block_time - tx_in.block_time).total_seconds()
                if 0 < delta < 600:  # Within 10 minutes
                    return {
                        "in_amount_usd": float(tx_in.amount_usd),
                        "out_amount_usd": float(tx_out.amount_usd),
                        "delay_seconds": int(delta),
                    }
        return None

    def _calculate_concentration(
        self, incoming: list[ProviderTransaction]
    ) -> float:
        """Calculate Herfindahl-Hirschman Index for sender concentration."""
        if not incoming:
            return 0.0

        sender_volumes: Counter[str] = Counter()
        total = Decimal("0")
        for tx in incoming:
            sender_volumes[tx.from_address.lower()] += float(tx.amount_usd)
            total += tx.amount_usd

        if total == 0:
            return 0.0

        total_f = float(total)
        hhi = sum((vol / total_f) ** 2 for vol in sender_volumes.values())
        return round(hhi, 4)

    def _detect_exchange_behavior(
        self,
        incoming: list[ProviderTransaction],
        outgoing: list[ProviderTransaction],
    ) -> bool:
        """Detect if address behaves like an exchange."""
        if len(incoming) < 10 or len(outgoing) < 10:
            return False

        unique_senders = len(set(t.from_address.lower() for t in incoming))
        unique_receivers = len(set(t.to_address.lower() for t in outgoing))

        return unique_senders > 15 and unique_receivers > 15

    def _estimate_same_owner(
        self, transactions: list[ProviderTransaction]
    ) -> float:
        """Estimate probability that counterparties belong to the same owner."""
        if len(transactions) < 3:
            return 0.0

        # Heuristic: round-trip pattern and timing correlation
        addresses: set[str] = set()
        for tx in transactions:
            addresses.add(tx.from_address.lower())
            addresses.add(tx.to_address.lower())

        # If very few counterparties with high volume, likely same owner
        if len(addresses) <= 5 and len(transactions) > 20:
            return 0.7
        elif len(addresses) <= 3:
            return 0.85

        return 0.1

    def _estimate_cluster_size(
        self, transactions: list[ProviderTransaction]
    ) -> int:
        """Estimate address cluster size from transaction patterns."""
        addresses: set[str] = set()
        for tx in transactions:
            addresses.add(tx.from_address.lower())
            addresses.add(tx.to_address.lower())
        return max(1, len(addresses))
