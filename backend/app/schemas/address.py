"""Address analysis schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddressAnalyzeRequest(BaseModel):
    """Request schema for address analysis."""

    address: str = Field(..., min_length=1, max_length=255, description="Blockchain address")
    chain: str | None = Field(
        None,
        description="Blockchain network. Auto-detected if not provided.",
    )
    depth: int = Field(default=1, ge=1, le=5, description="Graph exploration depth")


class AddressProfileResponse(BaseModel):
    """Full address profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    address: str
    chain: str
    address_type: str | None = None
    is_valid: bool = True

    # Balance
    balance_native: Decimal = Decimal("0")
    balance_usd: Decimal = Decimal("0")

    # Transaction counts
    tx_in_count: int = 0
    tx_out_count: int = 0
    total_tx_count: int = 0

    # Activity
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    # Statistics
    avg_tx_value: Decimal = Decimal("0")
    max_tx_value: Decimal = Decimal("0")
    min_tx_value: Decimal = Decimal("0")
    unique_counterparties: int = 0

    # Behavioral
    most_active_hours: list[int] | None = None
    most_active_days: list[str] | None = None
    avg_holding_time_hours: Decimal = Decimal("0")
    balance_change_30d: Decimal = Decimal("0")
    activity_trend: str | None = None

    # Labels
    label: str | None = None
    entity_type: str | None = None

    analyzed_at: datetime | None = None


class TransactionResponse(BaseModel):
    """Transaction data response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tx_hash: str
    chain: str
    from_address: str | None = None
    to_address: str | None = None
    amount: Decimal
    amount_usd: Decimal
    token: str
    fee: Decimal
    fee_usd: Decimal
    block_number: int | None = None
    block_time: datetime | None = None
    status: str = "confirmed"
    tx_type: str = "transfer"


class AddressFullAnalysis(BaseModel):
    """Complete analysis result including profile, risk, behavior, and ML."""

    profile: AddressProfileResponse
    risk: "RiskScoreResponse"
    behavior: "BehaviorAnalysisResponse"
    ml: "MLAnalysisResponse"
    transactions: list[TransactionResponse] = []


# ---- Risk schemas ----


class RiskFactorScore(BaseModel):
    """Individual risk factor score."""

    code: str
    name: str
    category: str
    weight: float
    score: float
    confidence: float
    description: str
    triggered: bool = False


class RiskScoreResponse(BaseModel):
    """Complete risk assessment response."""

    overall_score: int = Field(ge=0, le=100)
    risk_level: str
    factor_scores: list[RiskFactorScore] = []
    explanation: list[str] = []
    sanctions_match: bool = False
    sanctions_details: dict[str, Any] | None = None


# ---- Behavior schemas ----


class BehaviorFlag(BaseModel):
    """Detected behavioral pattern."""

    code: str
    name: str
    severity: str
    description: str
    evidence: dict[str, Any] | None = None


class BehaviorAnalysisResponse(BaseModel):
    """Behavioral analysis result."""

    flags: list[BehaviorFlag] = []
    anomalous_transfers: int = 0
    repeating_patterns: list[str] = []
    unusual_timing: bool = False
    new_counterparties: int = 0
    suspicious_splitting: bool = False
    rapid_withdrawal: bool = False
    fund_concentration: float = 0.0
    cluster_size: int = 1
    probable_exchange: bool = False
    same_owner_probability: float = 0.0


# ---- ML schemas ----


class MLAnalysisResponse(BaseModel):
    """Machine learning analysis result."""

    anomaly_score: float = 0.0
    is_anomaly: bool = False
    cluster_id: str | None = None
    cluster_label: str | None = None
    similar_wallets: list[str] = []
    features: dict[str, float] = {}


# Forward ref resolution
AddressFullAnalysis.model_rebuild()
