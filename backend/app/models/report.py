"""Report model for generated PDF investigation reports."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Report(Base):
    """Generated investigation report model.

    Attributes:
        id: Unique identifier.
        investigation_id: FK to the parent investigation.
        report_type: Type of report (full, executive_summary, sar).
        status: Generation status (pending, generating, completed, failed).
        file_path: Path to the generated PDF file.
        content: JSON representation of report content.
        generated_by: User ID who requested the report.
        generated_at: When the report was generated.
    """

    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    investigation = relationship("Investigation", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report type={self.report_type} status={self.status}>"
