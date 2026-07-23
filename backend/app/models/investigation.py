"""Investigation model for managing AML case investigations."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Investigation(Base):
    """AML Investigation case model.

    Attributes:
        id: Unique identifier (UUID).
        user_id: FK to the analyst who created this investigation.
        title: Investigation title.
        description: Detailed description.
        status: Current status (open, in_progress, review, closed, archived).
        priority: Priority level (critical, high, medium, low).
        tags: List of classification tags.
        is_favorite: Whether marked as favorite.
        version: Version number for tracking changes.
        findings: Summary of findings.
        conclusion: Final conclusion.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", index=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user = relationship("User", back_populates="investigations")
    addresses = relationship(
        "InvestigationAddress", back_populates="investigation", lazy="selectin"
    )
    comments = relationship(
        "Comment",
        back_populates="investigation",
        lazy="selectin",
        order_by="Comment.created_at.desc()",
    )
    reports = relationship("Report", back_populates="investigation", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Investigation {self.title[:30]} status={self.status}>"


class InvestigationAddress(Base):
    """Many-to-many link between investigations and addresses.

    Attributes:
        id: Unique identifier.
        investigation_id: FK to investigation.
        address_id: FK to address.
        role: Role of this address in the investigation (subject, counterparty, intermediary).
        notes: Analyst notes about this address.
        added_at: When this address was added to the investigation.
    """

    __tablename__ = "investigation_addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False
    )
    address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="subject")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    investigation = relationship("Investigation", back_populates="addresses")
    address = relationship("Address")


class Comment(Base):
    """Investigation comment model.

    Attributes:
        id: Unique identifier.
        investigation_id: FK to investigation.
        user_id: FK to commenting user.
        content: Comment text content.
        created_at: When the comment was posted.
    """

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    investigation = relationship("Investigation", back_populates="comments")
    user = relationship("User", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment by={self.user_id} on={self.investigation_id}>"
