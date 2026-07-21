"""Risk assessment model for storing AML risk scoring results."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RiskAssessment(Base):
    """AML risk assessment result for a blockchain address.

    Attributes:
        id: Unique identifier.
        address_id: FK to the assessed address.
        overall_score: Aggregate risk score (0-100).
        risk_level: Categorized level (critical, high, medium, low, minimal).
        factor_scores: JSON breakdown of individual factor scores.
        explanation: JSON array of human-readable explanations.
        sanctions_match: Whether address matches any sanctions list.
        sanctions_details: Details of sanctions match if any.
        behavior_flags: JSON list of detected behavioral patterns.
        ml_anomaly_score: Machine learning anomaly score (0-1).
        ml_cluster_id: ML-assigned cluster identifier.
        assessed_at: When the assessment was performed.
    """

    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False, index=True
    )

    # Risk scoring
    overall_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(
        String(50), default="minimal", index=True
    )
    factor_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Sanctions
    sanctions_match: Mapped[bool] = mapped_column(default=False)
    sanctions_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Behavioral
    behavior_flags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Machine Learning
    ml_anomaly_score: Mapped[float | None] = mapped_column(nullable=True)
    ml_cluster_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    address = relationship("Address", back_populates="risk_assessments")

    def __repr__(self) -> str:
        return f"<RiskAssessment score={self.overall_score} level={self.risk_level}>"
