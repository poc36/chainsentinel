"""Alert model for risk-based notifications."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Alert(Base):
    """Risk alert notification model.

    Attributes:
        id: Unique identifier.
        address_id: FK to the address that triggered the alert.
        alert_type: Type of alert (sanctions_match, high_risk, anomaly, pattern).
        severity: Severity level (critical, high, medium, low).
        title: Short alert title.
        message: Detailed alert message.
        is_read: Whether the alert has been viewed.
        is_resolved: Whether the alert has been resolved.
        resolved_by: User ID who resolved the alert.
        resolved_at: When the alert was resolved.
        metadata: Additional alert metadata.
        created_at: When the alert was created.
    """

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    address_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True
    )
    alert_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="medium", index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    alert_metadata: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    address = relationship("Address", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert {self.alert_type} severity={self.severity}>"
