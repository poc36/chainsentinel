"""API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.addresses import router as addresses_router
from app.api.v1.graph import router as graph_router
from app.api.v1.risk import router as risk_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.ai import router as ai_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(addresses_router, prefix="/addresses", tags=["Address Analysis"])
api_router.include_router(graph_router, prefix="/graph", tags=["Transaction Graph"])
api_router.include_router(risk_router, prefix="/risk", tags=["Risk Assessment"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Investigator"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
