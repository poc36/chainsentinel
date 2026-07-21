"""Report and dashboard schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---- Report schemas ----

class ReportGenerateRequest(BaseModel):
    """Request to generate a report."""

    investigation_id: UUID
    report_type: str = Field(default="full", pattern="^(full|executive_summary|sar)$")


class ReportResponse(BaseModel):
    """Report data response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    investigation_id: UUID
    report_type: str
    status: str
    file_path: str | None = None
    generated_at: datetime | None = None
    created_at: datetime


# ---- Dashboard schemas ----

class DashboardStats(BaseModel):
    """Overview statistics for the dashboard."""

    total_addresses_analyzed: int = 0
    total_investigations: int = 0
    active_investigations: int = 0
    high_risk_addresses: int = 0
    total_alerts: int = 0
    unread_alerts: int = 0
    total_reports: int = 0
    avg_risk_score: float = 0.0


class RiskDistribution(BaseModel):
    """Risk level distribution data."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    minimal: int = 0


class ActivityDataPoint(BaseModel):
    """Single data point for activity charts."""

    timestamp: str
    value: float
    label: str | None = None


class NetworkUsage(BaseModel):
    """Network usage statistics."""

    chain: str
    count: int
    percentage: float


class TopWallet(BaseModel):
    """Top wallet by volume or risk."""

    address: str
    chain: str
    label: str | None = None
    volume_usd: float = 0.0
    risk_score: int = 0


class DashboardData(BaseModel):
    """Complete dashboard data response."""

    stats: DashboardStats
    risk_distribution: RiskDistribution
    daily_activity: list[ActivityDataPoint] = []
    hourly_activity: list[ActivityDataPoint] = []
    network_usage: list[NetworkUsage] = []
    top_wallets: list[TopWallet] = []
    recent_alerts: list[dict[str, Any]] = []
    volume_history: list[ActivityDataPoint] = []


# ---- AI schemas ----

class AIChatRequest(BaseModel):
    """Request for AI investigator chat."""

    message: str = Field(..., min_length=1, max_length=2000)
    context: dict[str, Any] | None = None
    address: str | None = None
    investigation_id: UUID | None = None


class AIChatResponse(BaseModel):
    """AI investigator response."""

    response: str
    suggestions: list[str] = []
    sources: list[str] = []
    confidence: float = 0.0


class AISummaryRequest(BaseModel):
    """Request for AI executive summary."""

    address: str
    chain: str | None = None
    include_recommendations: bool = True


class AISARRequest(BaseModel):
    """Request for AI SAR report generation."""

    investigation_id: UUID
    reporting_entity: str = "ChainSentinel AML Platform"
    analyst_name: str | None = None
