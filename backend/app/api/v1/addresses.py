"""Address analysis endpoints."""

from fastapi import APIRouter, HTTPException

from app.domain.blockchain import Chain, detect_chain
from app.providers.factory import get_provider
from app.schemas.address import (
    AddressAnalyzeRequest,
    AddressFullAnalysis,
    AddressProfileResponse,
    TransactionResponse,
)
from app.services.address_service import AddressService
from app.services.behavior_analyzer import BehaviorAnalyzer
from app.services.ml_engine import MLEngine
from app.services.risk_engine import RiskEngine

router = APIRouter()


@router.post("/analyze", response_model=AddressFullAnalysis)
async def analyze_address(request: AddressAnalyzeRequest) -> AddressFullAnalysis:
    """Perform comprehensive address analysis.

    Runs the full pipeline:
    1. Address validation & chain detection
    2. Balance & transaction data
    3. Risk scoring
    4. Behavioral analysis
    5. ML anomaly detection
    """
    try:
        address_service = AddressService()
        risk_engine = RiskEngine()
        behavior_analyzer = BehaviorAnalyzer()
        ml_engine = MLEngine()
        provider = get_provider()

        # Get profile
        profile = await address_service.analyze(
            address=request.address,
            chain_hint=request.chain,
        )

        # Get transactions
        chain = Chain(request.chain) if request.chain else detect_chain(request.address)
        if not chain:
            raise ValueError("Cannot detect chain")

        raw_txs = await provider.get_transactions(request.address, chain, limit=50)
        transactions = address_service.transactions_to_response(raw_txs)

        # Risk assessment
        risk = await risk_engine.compute_risk(request.address, chain, raw_txs)

        # Behavior analysis
        behavior = await behavior_analyzer.analyze(request.address, raw_txs)

        # ML analysis
        ml = await ml_engine.analyze(request.address, raw_txs)

        return AddressFullAnalysis(
            profile=profile,
            risk=risk,
            behavior=behavior,
            ml=ml,
            transactions=transactions,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {e!s}",
        ) from e


@router.get("/{address}/profile", response_model=AddressProfileResponse)
async def get_address_profile(address: str, chain: str | None = None) -> AddressProfileResponse:
    """Get cached address profile."""
    try:
        service = AddressService()
        return await service.analyze(address=address, chain_hint=chain)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{address}/transactions", response_model=list[TransactionResponse])
async def get_address_transactions(
    address: str,
    chain: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TransactionResponse]:
    """Get paginated transaction list for an address."""
    detected_chain = Chain(chain) if chain else detect_chain(address)
    if not detected_chain:
        raise HTTPException(status_code=400, detail="Cannot detect chain")

    provider = get_provider()
    service = AddressService()
    raw_txs = await provider.get_transactions(address, detected_chain, limit=limit, offset=offset)
    return service.transactions_to_response(raw_txs)
