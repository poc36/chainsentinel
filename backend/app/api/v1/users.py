"""User management endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.auth import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(user: CurrentUser) -> UserResponse:
    """Get current user profile."""
    return UserResponse.model_validate(user)
