"""Risk assessment endpoints."""

from fastapi import APIRouter, HTTPException

from app.domain.blockchain import Chain, detect_chain
from app.providers.factory import get_provider
from app.services.risk_engine import RiskEngine
from app.schemas.address import RiskScoreResponse

router = APIRouter()


@router.post("/score", response_model=RiskScoreResponse)
async def compute_risk_score(address: str, chain: str | None = None) -> RiskScoreResponse:
    """Compute risk score for an address."""
    detected_chain = Chain(chain) if chain else detect_chain(address)
    if not detected_chain:
        raise HTTPException(status_code=400, detail="Cannot detect chain")

    provider = get_provider()
    transactions = await provider.get_transactions(address, detected_chain, limit=50)

    engine = RiskEngine()
    return await engine.compute_risk(address, detected_chain, transactions)


@router.get("/{address}/factors", response_model=RiskScoreResponse)
async def get_risk_factors(address: str, chain: str | None = None) -> RiskScoreResponse:
    """Get detailed risk factor breakdown."""
    detected_chain = Chain(chain) if chain else detect_chain(address)
    if not detected_chain:
        raise HTTPException(status_code=400, detail="Cannot detect chain")

    provider = get_provider()
    transactions = await provider.get_transactions(address, detected_chain, limit=50)

    engine = RiskEngine()
    return await engine.compute_risk(address, detected_chain, transactions)
