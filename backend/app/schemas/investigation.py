"""Investigation management schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InvestigationCreate(BaseModel):
    """Schema for creating an investigation."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    priority: str = Field(default="medium", pattern="^(critical|high|medium|low)$")
    tags: list[str] | None = None
    addresses: list[str] | None = None


class InvestigationUpdate(BaseModel):
    """Schema for updating an investigation."""

    title: str | None = None
    description: str | None = None
    status: str | None = Field(None, pattern="^(open|in_progress|review|closed|archived)$")
    priority: str | None = Field(None, pattern="^(critical|high|medium|low)$")
    tags: list[str] | None = None
    is_favorite: bool | None = None
    findings: str | None = None
    conclusion: str | None = None


class InvestigationResponse(BaseModel):
    """Investigation data response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None = None
    status: str
    priority: str
    tags: list[str] | None = None
    is_favorite: bool = False
    version: int = 1
    findings: str | None = None
    conclusion: str | None = None
    created_at: datetime
    updated_at: datetime
    address_count: int = 0
    comment_count: int = 0


class CommentCreate(BaseModel):
    """Schema for adding a comment."""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Comment data response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    investigation_id: UUID
    user_id: UUID
    user_name: str | None = None
    content: str
    created_at: datetime


class InvestigationFilter(BaseModel):
    """Filter parameters for investigation list."""

    status: str | None = None
    priority: str | None = None
    tag: str | None = None
    is_favorite: bool | None = None
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
