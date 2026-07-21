"""Risk factor catalog with 30+ AML risk indicators."""

from dataclasses import dataclass, field
from enum import StrEnum


class RiskCategory(StrEnum):
    """Categories of risk factors."""

    SANCTIONS = "sanctions"
    MIXER = "mixer"
    ILLICIT = "illicit"
    PATTERN = "pattern"
    BEHAVIORAL = "behavioral"
    STRUCTURAL = "structural"
    EXCHANGE = "exchange"


class RiskSeverity(StrEnum):
    """Severity levels for risk factors."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class RiskFactor:
    """Definition of a single AML risk factor.

    Attributes:
        code: Unique identifier for this factor.
        name: Human-readable name.
        description: Detailed description of the risk.
        category: Risk category grouping.
        severity: Severity level.
        weight: Numeric weight (1-10) for score calculation.
        indicators: List of behavioral indicators that trigger this factor.
    """

    code: str
    name: str
    description: str
    category: RiskCategory
    severity: RiskSeverity
    weight: float
    indicators: list[str] = field(default_factory=list)


# ============================================================
# Complete Risk Factor Catalog
# ============================================================

RISK_FACTORS: dict[str, RiskFactor] = {
    # ---- Sanctions ----
    "OFAC": RiskFactor(
        code="OFAC",
        name="OFAC Sanctions",
        description="Address matches OFAC Specially Designated Nationals list",
        category=RiskCategory.SANCTIONS,
        severity=RiskSeverity.CRITICAL,
        weight=10.0,
        indicators=["Direct match on SDN list", "Interaction with sanctioned entity"],
    ),
    "EU_SANCTIONS": RiskFactor(
        code="EU_SANCTIONS",
        name="EU Sanctions",
        description="Address matches EU consolidated sanctions list",
        category=RiskCategory.SANCTIONS,
        severity=RiskSeverity.CRITICAL,
        weight=10.0,
        indicators=["Listed on EU sanctions", "Connected to EU-sanctioned entity"],
    ),
    "UK_SANCTIONS": RiskFactor(
        code="UK_SANCTIONS",
        name="UK Sanctions",
        description="Address matches UK HM Treasury sanctions list",
        category=RiskCategory.SANCTIONS,
        severity=RiskSeverity.CRITICAL,
        weight=10.0,
        indicators=["Listed on OFSI", "Connected to UK-sanctioned entity"],
    ),

    # ---- Mixers & Privacy ----
    "TORNADO_CASH": RiskFactor(
        code="TORNADO_CASH",
        name="Tornado Cash",
        description="Direct interaction with Tornado Cash smart contracts",
        category=RiskCategory.MIXER,
        severity=RiskSeverity.CRITICAL,
        weight=9.5,
        indicators=["Deposit to TC", "Withdrawal from TC", "TC router interaction"],
    ),
    "SINBAD": RiskFactor(
        code="SINBAD",
        name="Sinbad Mixer",
        description="Interaction with Sinbad mixing service",
        category=RiskCategory.MIXER,
        severity=RiskSeverity.CRITICAL,
        weight=9.5,
        indicators=["Funds routed through Sinbad"],
    ),
    "MIXER": RiskFactor(
        code="MIXER",
        name="Generic Mixer",
        description="Interaction with known cryptocurrency mixing services",
        category=RiskCategory.MIXER,
        severity=RiskSeverity.HIGH,
        weight=8.0,
        indicators=["CoinJoin participation", "Mixer deposit/withdrawal pattern"],
    ),
    "BRIDGE": RiskFactor(
        code="BRIDGE",
        name="Cross-chain Bridge",
        description="Frequent use of cross-chain bridges (potential obfuscation)",
        category=RiskCategory.MIXER,
        severity=RiskSeverity.MEDIUM,
        weight=4.0,
        indicators=["Multiple bridge interactions", "Rapid cross-chain transfers"],
    ),
    "DEX": RiskFactor(
        code="DEX",
        name="DEX Activity",
        description="High volume of decentralized exchange interactions",
        category=RiskCategory.EXCHANGE,
        severity=RiskSeverity.LOW,
        weight=2.0,
        indicators=["Frequent swaps", "Large volume through DEX"],
    ),

    # ---- Illicit Activity ----
    "DARKNET": RiskFactor(
        code="DARKNET",
        name="Darknet Market",
        description="Interaction with known darknet marketplace addresses",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.CRITICAL,
        weight=9.0,
        indicators=["Direct darknet interaction", "Funds from darknet"],
    ),
    "SCAM": RiskFactor(
        code="SCAM",
        name="Scam",
        description="Address associated with known scam operations",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.HIGH,
        weight=8.5,
        indicators=["Reported as scam", "Pig butchering pattern", "Rug pull involvement"],
    ),
    "PHISHING": RiskFactor(
        code="PHISHING",
        name="Phishing",
        description="Address linked to phishing attacks or approval exploits",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.HIGH,
        weight=8.5,
        indicators=["Approval phishing", "Token drain pattern"],
    ),
    "EXPLOIT": RiskFactor(
        code="EXPLOIT",
        name="Smart Contract Exploit",
        description="Address involved in DeFi protocol exploits",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.CRITICAL,
        weight=9.0,
        indicators=["Flash loan attack", "Reentrancy exploit", "Oracle manipulation"],
    ),
    "HACK": RiskFactor(
        code="HACK",
        name="Hack",
        description="Address associated with exchange or protocol hacks",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.CRITICAL,
        weight=9.5,
        indicators=["Stolen funds movement", "Hot wallet compromise"],
    ),
    "RANSOMWARE": RiskFactor(
        code="RANSOMWARE",
        name="Ransomware",
        description="Address used for ransomware payments or collection",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.CRITICAL,
        weight=10.0,
        indicators=["Known ransomware address", "Ransom collection pattern"],
    ),
    "GAMBLING": RiskFactor(
        code="GAMBLING",
        name="Gambling",
        description="Interaction with unlicensed gambling platforms",
        category=RiskCategory.ILLICIT,
        severity=RiskSeverity.MEDIUM,
        weight=5.0,
        indicators=["Casino deposits", "Betting platform interaction"],
    ),
    "HIGH_RISK_EXCHANGE": RiskFactor(
        code="HIGH_RISK_EXCHANGE",
        name="High Risk Exchange",
        description="Interaction with exchanges known for weak KYC/AML",
        category=RiskCategory.EXCHANGE,
        severity=RiskSeverity.HIGH,
        weight=7.0,
        indicators=["No-KYC exchange usage", "Weak compliance exchange"],
    ),

    # ---- Structural Patterns ----
    "P2P": RiskFactor(
        code="P2P",
        name="P2P Trading",
        description="Pattern consistent with peer-to-peer OTC trading",
        category=RiskCategory.STRUCTURAL,
        severity=RiskSeverity.MEDIUM,
        weight=4.0,
        indicators=["Round amounts", "Regular intervals", "Many counterparties"],
    ),
    "DUSTING": RiskFactor(
        code="DUSTING",
        name="Dusting Attack",
        description="Receiving many tiny (dust) transactions — possible tracking",
        category=RiskCategory.STRUCTURAL,
        severity=RiskSeverity.LOW,
        weight=3.0,
        indicators=["Many micro-transactions received", "Sub-threshold amounts"],
    ),
    "WHALE": RiskFactor(
        code="WHALE",
        name="Whale Activity",
        description="Extremely large holdings or transaction volumes",
        category=RiskCategory.STRUCTURAL,
        severity=RiskSeverity.LOW,
        weight=2.0,
        indicators=["Top 0.1% balance", "Single tx > $1M"],
    ),
    "SELF_TRANSFER": RiskFactor(
        code="SELF_TRANSFER",
        name="Self Transfer",
        description="Funds sent to addresses owned by the same entity",
        category=RiskCategory.STRUCTURAL,
        severity=RiskSeverity.LOW,
        weight=2.0,
        indicators=["Same-entity transfers", "Wallet consolidation"],
    ),

    # ---- Behavioral Patterns ----
    "LAYERING": RiskFactor(
        code="LAYERING",
        name="Layering",
        description="Complex chain of transfers to obscure fund origins",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.HIGH,
        weight=8.0,
        indicators=["Multiple hops", "Intermediary wallets", "Rapid forwarding"],
    ),
    "PEEL_CHAIN": RiskFactor(
        code="PEEL_CHAIN",
        name="Peel Chain",
        description="Sequential small withdrawals from a larger sum (peeling)",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.HIGH,
        weight=7.5,
        indicators=["Decreasing amounts", "Sequential addresses", "Systematic peeling"],
    ),
    "FAN_IN": RiskFactor(
        code="FAN_IN",
        name="Fan-In Pattern",
        description="Many addresses sending to a single consolidation point",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.MEDIUM,
        weight=5.0,
        indicators=["Multiple senders", "Consolidation wallet", "Collection pattern"],
    ),
    "FAN_OUT": RiskFactor(
        code="FAN_OUT",
        name="Fan-Out Pattern",
        description="Single address distributing to many recipients",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.MEDIUM,
        weight=5.0,
        indicators=["Mass distribution", "Airdrop-like pattern", "Payroll pattern"],
    ),
    "SMURFING": RiskFactor(
        code="SMURFING",
        name="Smurfing",
        description="Breaking large amounts into many small transactions",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.HIGH,
        weight=7.5,
        indicators=["Many sub-threshold transactions", "Structured deposits"],
    ),
    "CIRCULAR": RiskFactor(
        code="CIRCULAR",
        name="Circular Transactions",
        description="Funds cycling back to origin through intermediaries",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.HIGH,
        weight=8.0,
        indicators=["Round-trip funds", "Circular flow detected"],
    ),
    "CROSS_CHAIN": RiskFactor(
        code="CROSS_CHAIN",
        name="Cross-chain Movement",
        description="Funds moving between multiple blockchain networks",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.MEDIUM,
        weight=4.5,
        indicators=["Bridge usage", "Multi-chain presence"],
    ),
    "DORMANT": RiskFactor(
        code="DORMANT",
        name="Dormant Wallet",
        description="Previously inactive wallet suddenly active",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.MEDIUM,
        weight=4.0,
        indicators=["Long inactivity period", "Sudden large movement"],
    ),
    "RAPID_MOVEMENT": RiskFactor(
        code="RAPID_MOVEMENT",
        name="Rapid Movement",
        description="Funds moved very quickly after reception (< 1 hour)",
        category=RiskCategory.BEHAVIORAL,
        severity=RiskSeverity.HIGH,
        weight=6.5,
        indicators=["Pass-through wallet", "Minimal holding time"],
    ),
}


def get_risk_factor(code: str) -> RiskFactor | None:
    """Get a risk factor by its code.

    Args:
        code: Risk factor code.

    Returns:
        RiskFactor or None if not found.
    """
    return RISK_FACTORS.get(code)


def get_factors_by_category(category: RiskCategory) -> list[RiskFactor]:
    """Get all risk factors in a category.

    Args:
        category: Risk category to filter by.

    Returns:
        List of risk factors in the specified category.
    """
    return [f for f in RISK_FACTORS.values() if f.category == category]


def get_max_possible_score() -> float:
    """Calculate the maximum possible risk score.

    Returns:
        Sum of all factor weights (theoretical maximum).
    """
    return sum(f.weight for f in RISK_FACTORS.values())


def calculate_risk_level(score: int) -> str:
    """Map a numeric risk score to a risk level string.

    Args:
        score: Risk score (0-100).

    Returns:
        Risk level string.
    """
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    elif score >= 20:
        return "low"
    return "minimal"


def get_risk_color(risk_level: str) -> str:
    """Get the display color for a risk level.

    Args:
        risk_level: Risk level string.

    Returns:
        Hex color code for the risk level.
    """
    colors = {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#22c55e",
        "minimal": "#4ade80",
    }
    return colors.get(risk_level, "#6b7280")
