"""AI Investigator endpoints."""

from fastapi import APIRouter, HTTPException

from app.services.ai_investigator import AIInvestigator
from app.schemas.report import AIChatRequest, AIChatResponse, AISummaryRequest

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest) -> AIChatResponse:
    """Chat with the AI investigator."""
    investigator = AIInvestigator()
    try:
        return await investigator.chat(
            message=request.message,
            context=request.context,
        )
    finally:
        await investigator.close()


@router.post("/summary", response_model=AIChatResponse)
async def generate_summary(request: AISummaryRequest) -> AIChatResponse:
    """Generate an executive summary for an address."""
    investigator = AIInvestigator()
    try:
        summary = await investigator.generate_executive_summary({
            "address": request.address,
            "chain": request.chain or "ethereum",
            "risk_score": 0,
            "risk_level": "unknown",
            "balance_usd": 0,
            "tx_count": 0,
            "counterparties": 0,
            "risk_factors": "N/A",
            "behavior_flags": "N/A",
            "anomaly_score": 0,
            "cluster_label": "N/A",
        })
        return AIChatResponse(
            response=summary,
            suggestions=["What are the main risk factors?", "Generate SAR report"],
            confidence=0.8,
        )
    finally:
        await investigator.close()
