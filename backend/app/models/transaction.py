"""Transaction model for storing blockchain transactions."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Transaction(Base):
    """Blockchain transaction model.

    Attributes:
        id: Unique identifier (UUID).
        tx_hash: Transaction hash on the blockchain.
        chain: Blockchain network name.
        from_address_id: FK to sender Address.
        to_address_id: FK to receiver Address.
        amount: Transaction amount in native currency.
        amount_usd: Transaction amount in USD.
        token: Token symbol (ETH, BTC, USDT, etc.).
        fee: Transaction fee in native currency.
        fee_usd: Transaction fee in USD.
        block_number: Block number containing this transaction.
        block_time: Timestamp of the block.
        status: Transaction status (confirmed, pending, failed).
        tx_type: Transaction type (transfer, swap, contract_call, etc.).
        created_at: Record creation timestamp.
    """

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tx_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    chain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Addresses
    from_address_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True
    )
    to_address_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True
    )

    # Values
    amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal("0"))
    amount_usd: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0"))
    token: Mapped[str] = mapped_column(String(50), default="ETH")
    fee: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal("0"))
    fee_usd: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal("0"))

    # Block info
    block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    block_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(String(50), default="confirmed")
    tx_type: Mapped[str] = mapped_column(String(50), default="transfer")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    from_address_rel = relationship(
        "Address",
        back_populates="sent_transactions",
        foreign_keys=[from_address_id],
    )
    to_address_rel = relationship(
        "Address",
        back_populates="received_transactions",
        foreign_keys=[to_address_id],
    )

    __table_args__ = (
        Index("ix_transactions_block_time", "block_time"),
        Index("ix_transactions_chain_hash", "chain", "tx_hash"),
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.tx_hash[:12]}... {self.amount} {self.token}>"
