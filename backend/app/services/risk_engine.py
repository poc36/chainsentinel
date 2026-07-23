"""AML Risk Scoring Engine — core risk assessment logic.

Evaluates addresses against 30+ risk factors to compute a weighted risk score.
"""

from decimal import Decimal

from app.core.logging import get_logger
from app.domain.address_classifier import KNOWN_MIXERS, classify_address
from app.domain.blockchain import Chain
from app.domain.risk_factors import (
    RISK_FACTORS,
    calculate_risk_level,
)
from app.domain.sanctions import get_sanctions_checker
from app.providers.base import ProviderTransaction
from app.schemas.address import RiskFactorScore, RiskScoreResponse

logger = get_logger(__name__)


class RiskEngine:
    """AML Risk Scoring Engine.

    Evaluates blockchain addresses against a comprehensive set of
    risk factors including sanctions, mixer interaction, behavioral
    patterns, and structural indicators.

    Risk Score Range:
        0-19:  Minimal
        20-39: Low
        40-59: Medium
        60-79: High
        80-100: Critical
    """

    def __init__(self) -> None:
        self.sanctions_checker = get_sanctions_checker()
        self.max_weighted_score = sum(f.weight for f in RISK_FACTORS.values())

    async def compute_risk(
        self,
        address: str,
        chain: Chain,
        transactions: list[ProviderTransaction],
        counterparties: list[str] | None = None,
    ) -> RiskScoreResponse:
        """Compute comprehensive risk score for an address.

        Args:
            address: Blockchain address to assess.
            chain: Blockchain network.
            transactions: Address transaction history.
            counterparties: List of counterparty addresses.

        Returns:
            Complete risk assessment with factor breakdown.
        """
        logger.info("risk_assessment_started", address=address[:12], chain=chain)

        factor_scores: list[RiskFactorScore] = []
        explanations: list[str] = []
        total_weighted_score: float = 0.0
        sanctions_match = False
        sanctions_details: dict | None = None

        # --- Sanctions Check ---
        sanctions_result = self.sanctions_checker.check(address)
        if sanctions_result.is_sanctioned:
            sanctions_match = True
            sanctions_details = sanctions_result.details

            for list_name in sanctions_result.lists:
                factor_code = list_name if list_name in RISK_FACTORS else "OFAC"
                factor = RISK_FACTORS.get(factor_code)
                if factor:
                    score = RiskFactorScore(
                        code=factor.code,
                        name=factor.name,
                        category=factor.category,
                        weight=factor.weight,
                        score=factor.weight,
                        confidence=1.0,
                        description=f"Direct match: {sanctions_result.entity_name or 'Unknown'}",
                        triggered=True,
                    )
                    factor_scores.append(score)
                    total_weighted_score += factor.weight
                    explanations.append(
                        f"🚨 {factor.name}: Address directly matches {list_name} sanctions list "
                        f"({sanctions_result.entity_name})"
                    )

        # --- Counterparty Sanctions ---
        cp_addresses = counterparties or self._extract_counterparties(address, transactions)
        cp_sanctions = self.sanctions_checker.check_counterparties(cp_addresses)
        if cp_sanctions:
            factor = RISK_FACTORS["OFAC"]
            confidence = min(0.8, len(cp_sanctions) * 0.2)
            score_val = factor.weight * confidence
            factor_scores.append(
                RiskFactorScore(
                    code="OFAC_INDIRECT",
                    name="Indirect Sanctions Exposure",
                    category=factor.category,
                    weight=factor.weight * 0.7,
                    score=score_val * 0.7,
                    confidence=confidence,
                    description=f"Transacted with {len(cp_sanctions)} sanctioned address(es)",
                    triggered=True,
                )
            )
            total_weighted_score += score_val * 0.7
            explanations.append(
                f"⚠️ Indirect sanctions exposure: {len(cp_sanctions)} counterparties "
                f"are on sanctions lists"
            )

        # --- Mixer Detection ---
        mixer_score = self._check_mixer_interaction(address, chain, transactions)
        if mixer_score:
            factor_scores.append(mixer_score)
            total_weighted_score += mixer_score.score
            explanations.append(f"🔴 {mixer_score.name}: {mixer_score.description}")

        # --- Pattern Detection ---
        pattern_scores = self._detect_patterns(address, chain, transactions)
        for ps in pattern_scores:
            factor_scores.append(ps)
            total_weighted_score += ps.score
            if ps.triggered:
                explanations.append(f"⚠️ {ps.name}: {ps.description}")

        # --- Behavioral Scoring ---
        behavior_scores = self._evaluate_behavior(address, transactions)
        for bs in behavior_scores:
            factor_scores.append(bs)
            total_weighted_score += bs.score
            if bs.triggered:
                explanations.append(f"📊 {bs.name}: {bs.description}")

        # --- Address Type Risk ---
        classification = classify_address(address, chain)
        type_score = self._score_address_type(classification.address_type)
        if type_score:
            factor_scores.append(type_score)
            total_weighted_score += type_score.score
            if type_score.triggered:
                explanations.append(f"[i] {type_score.name}: {type_score.description}")

        # --- Normalize to 0-100 ---
        overall_score = min(100, int((total_weighted_score / self.max_weighted_score) * 100))
        risk_level = calculate_risk_level(overall_score)

        if not explanations:
            explanations.append("✅ No significant risk factors detected.")

        logger.info(
            "risk_assessment_completed",
            address=address[:12],
            score=overall_score,
            level=risk_level,
            factors_triggered=sum(1 for f in factor_scores if f.triggered),
        )

        return RiskScoreResponse(
            overall_score=overall_score,
            risk_level=risk_level,
            factor_scores=factor_scores,
            explanation=explanations,
            sanctions_match=sanctions_match,
            sanctions_details=sanctions_details,
        )

    def _extract_counterparties(
        self, address: str, transactions: list[ProviderTransaction]
    ) -> list[str]:
        """Extract unique counterparty addresses from transactions."""
        addr_lower = address.lower()
        counterparties: set[str] = set()
        for tx in transactions:
            if tx.from_address.lower() != addr_lower:
                counterparties.add(tx.from_address)
            if tx.to_address.lower() != addr_lower:
                counterparties.add(tx.to_address)
        return list(counterparties)

    def _check_mixer_interaction(
        self,
        address: str,
        chain: Chain,
        transactions: list[ProviderTransaction],
    ) -> RiskFactorScore | None:
        """Check for mixer/Tornado Cash interaction."""
        mixer_addresses = set(KNOWN_MIXERS.keys())
        mixer_txs = [
            tx
            for tx in transactions
            if (
                tx.from_address.lower() in mixer_addresses
                or tx.to_address.lower() in mixer_addresses
            )
        ]

        if mixer_txs:
            # Check if it's specifically Tornado Cash
            is_tornado = any(
                "Tornado" in KNOWN_MIXERS.get(tx.from_address.lower(), "")
                or "Tornado" in KNOWN_MIXERS.get(tx.to_address.lower(), "")
                for tx in mixer_txs
            )

            if is_tornado:
                factor = RISK_FACTORS["TORNADO_CASH"]
                return RiskFactorScore(
                    code=factor.code,
                    name=factor.name,
                    category=factor.category,
                    weight=factor.weight,
                    score=factor.weight * 0.95,
                    confidence=0.95,
                    description=f"Direct Tornado Cash interaction ({len(mixer_txs)} txs)",
                    triggered=True,
                )

            factor = RISK_FACTORS["MIXER"]
            return RiskFactorScore(
                code=factor.code,
                name=factor.name,
                category=factor.category,
                weight=factor.weight,
                score=factor.weight * 0.85,
                confidence=0.85,
                description=f"Mixer interaction detected ({len(mixer_txs)} txs)",
                triggered=True,
            )

        return None

    def _detect_patterns(
        self,
        address: str,
        chain: Chain,
        transactions: list[ProviderTransaction],
    ) -> list[RiskFactorScore]:
        """Detect structural and transactional patterns."""
        scores: list[RiskFactorScore] = []
        addr_lower = address.lower()

        if not transactions:
            return scores

        incoming = [t for t in transactions if t.to_address.lower() == addr_lower]
        outgoing = [t for t in transactions if t.from_address.lower() == addr_lower]

        # Fan-In detection (many senders)
        unique_senders = len(set(t.from_address.lower() for t in incoming))
        if unique_senders > 10:
            factor = RISK_FACTORS["FAN_IN"]
            confidence = min(1.0, unique_senders / 30)
            scores.append(
                RiskFactorScore(
                    code=factor.code,
                    name=factor.name,
                    category=factor.category,
                    weight=factor.weight,
                    score=factor.weight * confidence,
                    confidence=confidence,
                    description=f"{unique_senders} unique senders detected (consolidation pattern)",
                    triggered=True,
                )
            )

        # Fan-Out detection (many receivers)
        unique_receivers = len(set(t.to_address.lower() for t in outgoing))
        if unique_receivers > 10:
            factor = RISK_FACTORS["FAN_OUT"]
            confidence = min(1.0, unique_receivers / 30)
            scores.append(
                RiskFactorScore(
                    code=factor.code,
                    name=factor.name,
                    category=factor.category,
                    weight=factor.weight,
                    score=factor.weight * confidence,
                    confidence=confidence,
                    description=f"{unique_receivers} unique recipients (distribution pattern)",
                    triggered=True,
                )
            )

        # Rapid Movement detection
        for tx_in in incoming:
            if tx_in.block_time:
                quick_outs = [
                    tx
                    for tx in outgoing
                    if tx.block_time
                    and 0 < (tx.block_time - tx_in.block_time).total_seconds() < 3600
                ]
                if quick_outs:
                    factor = RISK_FACTORS["RAPID_MOVEMENT"]
                    scores.append(
                        RiskFactorScore(
                            code=factor.code,
                            name=factor.name,
                            category=factor.category,
                            weight=factor.weight,
                            score=factor.weight * 0.8,
                            confidence=0.8,
                            description="Funds forwarded within 1 hour of receipt",
                            triggered=True,
                        )
                    )
                    break

        # Smurfing detection (many similar-sized transactions)
        if len(outgoing) >= 5:
            amounts = [float(t.amount_usd) for t in outgoing if t.amount_usd > 0]
            if amounts:
                avg_amount = sum(amounts) / len(amounts)
                if avg_amount > 0:
                    similar = sum(1 for a in amounts if abs(a - avg_amount) / avg_amount < 0.15)
                    if similar > len(amounts) * 0.6:
                        factor = RISK_FACTORS["SMURFING"]
                        confidence = similar / len(amounts)
                        scores.append(
                            RiskFactorScore(
                                code=factor.code,
                                name=factor.name,
                                category=factor.category,
                                weight=factor.weight,
                                score=factor.weight * confidence,
                                confidence=confidence,
                                description=(
                                    f"{similar}/{len(amounts)} outgoing txs have similar amounts "
                                    f"(~${avg_amount:.0f}) — possible structuring"
                                ),
                                triggered=True,
                            )
                        )

        # Self Transfer
        self_txs = [
            t
            for t in transactions
            if t.from_address.lower() == addr_lower and t.to_address.lower() == addr_lower
        ]
        if self_txs:
            factor = RISK_FACTORS["SELF_TRANSFER"]
            scores.append(
                RiskFactorScore(
                    code=factor.code,
                    name=factor.name,
                    category=factor.category,
                    weight=factor.weight,
                    score=factor.weight * 0.6,
                    confidence=0.6,
                    description=f"{len(self_txs)} self-transfer transactions detected",
                    triggered=True,
                )
            )

        return scores

    def _evaluate_behavior(
        self,
        address: str,
        transactions: list[ProviderTransaction],
    ) -> list[RiskFactorScore]:
        """Evaluate behavioral risk factors."""
        scores: list[RiskFactorScore] = []

        if not transactions:
            return scores

        # Dusting detection
        dust_txs = [t for t in transactions if t.amount_usd < Decimal("0.50") and t.amount_usd > 0]
        if len(dust_txs) > 5:
            factor = RISK_FACTORS["DUSTING"]
            confidence = min(1.0, len(dust_txs) / 20)
            scores.append(
                RiskFactorScore(
                    code=factor.code,
                    name=factor.name,
                    category=factor.category,
                    weight=factor.weight,
                    score=factor.weight * confidence,
                    confidence=confidence,
                    description=f"{len(dust_txs)} dust transactions (< $0.50) received",
                    triggered=True,
                )
            )

        # Whale detection
        whale_txs = [t for t in transactions if t.amount_usd > Decimal("100000")]
        if whale_txs:
            factor = RISK_FACTORS["WHALE"]
            scores.append(
                RiskFactorScore(
                    code=factor.code,
                    name=factor.name,
                    category=factor.category,
                    weight=factor.weight,
                    score=factor.weight * 0.5,
                    confidence=0.5,
                    description=f"{len(whale_txs)} transactions exceed $100,000",
                    triggered=True,
                )
            )

        return scores

    def _score_address_type(self, address_type: str) -> RiskFactorScore | None:
        """Score based on address type classification."""
        if address_type == "mixer":
            factor = RISK_FACTORS["MIXER"]
            return RiskFactorScore(
                code="TYPE_MIXER",
                name="Mixer Address",
                category=factor.category,
                weight=factor.weight,
                score=factor.weight * 0.95,
                confidence=0.95,
                description="Address classified as a known mixing service",
                triggered=True,
            )

        if address_type == "exchange":
            factor = RISK_FACTORS["HIGH_RISK_EXCHANGE"]
            return RiskFactorScore(
                code="TYPE_EXCHANGE",
                name="Exchange Address",
                category=factor.category,
                weight=2.0,
                score=1.0,
                confidence=0.95,
                description="Address classified as a cryptocurrency exchange",
                triggered=False,
            )

        return None
