"""Dashboard analytics endpoints."""

from fastapi import APIRouter

from app.services.dashboard_service import DashboardService
from app.schemas.report import DashboardData

router = APIRouter()


@router.get("/data", response_model=DashboardData)
async def get_dashboard_data() -> DashboardData:
    """Get complete dashboard analytics data."""
    service = DashboardService()
    return await service.get_dashboard_data()
