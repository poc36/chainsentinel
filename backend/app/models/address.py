"""Address model for storing analyzed blockchain addresses."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Address(Base):
    """Blockchain address model with analysis results.

    Attributes:
        id: Unique identifier (UUID).
        address: Blockchain address string.
        chain: Blockchain network name (ethereum, bitcoin, etc.).
        address_type: Type classification (eoa, contract, multisig, exchange).
        is_valid: Whether the address format is valid.
        balance_native: Balance in native currency.
        balance_usd: Balance in USD equivalent.
        tx_in_count: Number of incoming transactions.
        tx_out_count: Number of outgoing transactions.
        first_seen: Timestamp of first on-chain activity.
        last_seen: Timestamp of last on-chain activity.
        avg_tx_value: Average transaction value in USD.
        max_tx_value: Maximum transaction value in USD.
        min_tx_value: Minimum transaction value in USD.
        unique_counterparties: Count of unique interacting addresses.
        most_active_hours: JSON list of most active hours.
        most_active_days: JSON list of most active weekdays.
        avg_holding_time_hours: Average time funds are held before transfer.
        balance_change_30d: Balance change over last 30 days in USD.
        activity_trend: Activity trend indicator (increasing/decreasing/stable).
        label: Known entity label (e.g., "Binance Hot Wallet").
        entity_type: Entity classification (exchange, mixer, defi, etc.).
        metadata: Additional metadata JSON.
        analyzed_at: When the analysis was performed.
    """

    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    chain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    address_type: Mapped[str] = mapped_column(String(50), nullable=True)
    is_valid: Mapped[bool] = mapped_column(default=True)

    # Balance
    balance_native: Mapped[Decimal] = mapped_column(
        Numeric(36, 18), default=Decimal("0")
    )
    balance_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal("0")
    )

    # Transaction counts
    tx_in_count: Mapped[int] = mapped_column(Integer, default=0)
    tx_out_count: Mapped[int] = mapped_column(Integer, default=0)

    # Activity timestamps
    first_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Transaction statistics
    avg_tx_value: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal("0")
    )
    max_tx_value: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal("0")
    )
    min_tx_value: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal("0")
    )
    unique_counterparties: Mapped[int] = mapped_column(Integer, default=0)

    # Behavioral metrics
    most_active_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    most_active_days: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    avg_holding_time_hours: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0")
    )
    balance_change_30d: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal("0")
    )
    activity_trend: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Labels
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True
    )
    analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    risk_assessments = relationship(
        "RiskAssessment", back_populates="address", lazy="selectin"
    )
    sent_transactions = relationship(
        "Transaction",
        back_populates="from_address_rel",
        foreign_keys="Transaction.from_address_id",
        lazy="selectin",
    )
    received_transactions = relationship(
        "Transaction",
        back_populates="to_address_rel",
        foreign_keys="Transaction.to_address_id",
        lazy="selectin",
    )
    alerts = relationship("Alert", back_populates="address", lazy="selectin")

    __table_args__ = (
        Index("ix_addresses_chain_address", "chain", "address", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Address {self.chain}:{self.address[:12]}...>"
