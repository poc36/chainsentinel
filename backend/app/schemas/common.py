"""Common schemas used across the application."""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""

    created_at: datetime
    updated_at: datetime | None = None


class BaseResponse(BaseModel):
    """Standard API response wrapper."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    message: str = "OK"


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    message: str
    detail: str | None = None
    code: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
