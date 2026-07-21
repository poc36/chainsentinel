"""AI Investigator service — LLM integration for AML analysis."""

from typing import Any

import httpx

from app.config import get_settings
from app.schemas.report import AIChatResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


# System prompt for the AML investigator
AML_SYSTEM_PROMPT = """You are ChainSentinel AI Investigator — an expert AML (Anti-Money Laundering) 
analyst specializing in blockchain forensics and cryptocurrency compliance.

Your capabilities:
- Analyze blockchain transaction patterns
- Interpret risk scores and factor explanations
- Identify suspicious activities (layering, smurfing, mixing, etc.)
- Assess sanctions exposure (OFAC, EU, UK)
- Recommend investigative actions
- Generate executive summaries and SAR narratives
- Explain complex blockchain concepts in clear language

When analyzing data:
- Be precise and cite specific evidence
- Use professional AML terminology
- Quantify risks with confidence levels
- Always recommend next steps
- Flag critical findings prominently

Format your responses with clear sections and bullet points."""


EXECUTIVE_SUMMARY_PROMPT = """Generate a professional Executive Summary for this blockchain address analysis.

Address: {address}
Chain: {chain}
Risk Score: {risk_score}/100 ({risk_level})
Balance: ${balance_usd:,.2f}
Total Transactions: {tx_count}
Unique Counterparties: {counterparties}

Risk Factors:
{risk_factors}

Behavioral Flags:
{behavior_flags}

ML Analysis:
- Anomaly Score: {anomaly_score}
- Cluster: {cluster_label}

Structure the summary with:
1. Overview (2-3 sentences)
2. Key Findings (bullet points)
3. Risk Assessment (detailed)
4. Recommended Actions
5. Conclusion"""


SAR_PROMPT = """Generate a Suspicious Activity Report (SAR) narrative for this investigation.

Investigation: {title}
Analyst: {analyst_name}
Date: {date}

Subject Address: {address}
Chain: {chain}
Risk Score: {risk_score}/100

Follow the standard SAR narrative structure:
1. Subject Information
2. Suspicious Activity Description
3. Amount and Nature of Suspicious Activity
4. Timing and Duration
5. Source and Use of Funds
6. Actions Taken
7. Law Enforcement Contact Information (placeholder)

Use professional, factual language suitable for regulatory filing.
Include specific transaction details and risk factor evidence."""


class AIInvestigator:
    """LLM-powered AML investigation assistant.

    Supports both OpenAI API and Ollama (local) as LLM providers.
    Provides contextual Q&A about risk assessments, executive summaries,
    and SAR report generation.
    """

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def chat(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> AIChatResponse:
        """Process a chat message with the AI investigator.

        Args:
            message: User's question or instruction.
            context: Optional analysis context (risk data, tx data, etc.).

        Returns:
            AIChatResponse with the AI's response and suggestions.
        """
        # Build context string
        context_str = ""
        if context:
            context_str = "\n\nAnalysis Context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"

        full_prompt = f"{message}{context_str}"

        try:
            response_text = await self._call_llm(
                system=AML_SYSTEM_PROMPT,
                user=full_prompt,
            )
        except Exception as e:
            logger.error("ai_chat_error", error=str(e))
            response_text = self._generate_fallback_response(message, context)

        suggestions = self._generate_suggestions(message, context)

        return AIChatResponse(
            response=response_text,
            suggestions=suggestions,
            sources=["ChainSentinel AML Engine", "Risk Factor Analysis"],
            confidence=0.85,
        )

    async def generate_executive_summary(
        self,
        analysis_data: dict[str, Any],
    ) -> str:
        """Generate an executive summary from analysis data.

        Args:
            analysis_data: Complete analysis results.

        Returns:
            Formatted executive summary text.
        """
        prompt = EXECUTIVE_SUMMARY_PROMPT.format(**analysis_data)

        try:
            return await self._call_llm(
                system=AML_SYSTEM_PROMPT,
                user=prompt,
            )
        except Exception:
            return self._generate_fallback_summary(analysis_data)

    async def generate_sar(
        self,
        investigation_data: dict[str, Any],
    ) -> str:
        """Generate a SAR (Suspicious Activity Report) narrative.

        Args:
            investigation_data: Investigation details and evidence.

        Returns:
            SAR narrative text.
        """
        prompt = SAR_PROMPT.format(**investigation_data)

        try:
            return await self._call_llm(
                system=AML_SYSTEM_PROMPT,
                user=prompt,
            )
        except Exception:
            return self._generate_fallback_sar(investigation_data)

    async def _call_llm(self, system: str, user: str) -> str:
        """Call the configured LLM provider.

        Tries the primary provider first, falls back to the other.
        """
        if self.provider == "openai" and settings.openai_api_key:
            return await self._call_openai(system, user)
        elif self.provider == "ollama":
            return await self._call_ollama(system, user)
        else:
            # If no API key configured, use fallback
            raise ValueError("No LLM provider configured")

    async def _call_openai(self, system: str, user: str) -> str:
        """Call OpenAI API."""
        response = await self.http_client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_ollama(self, system: str, user: str) -> str:
        """Call Ollama local API."""
        response = await self.http_client.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    def _generate_fallback_response(
        self, message: str, context: dict[str, Any] | None
    ) -> str:
        """Generate a structured response without LLM when API is unavailable."""
        msg_lower = message.lower()
        risk_score = context.get("risk_score", 0) if context else 0
        risk_level = context.get("risk_level", "unknown") if context else "unknown"

        if "risk" in msg_lower or "why" in msg_lower:
            return (
                f"## Risk Assessment Analysis\n\n"
                f"The address has been assigned a risk score of **{risk_score}/100** "
                f"(classified as **{risk_level}**).\n\n"
                f"### Contributing Factors\n"
                f"The risk score is computed from a weighted combination of:\n"
                f"- **Sanctions screening** against OFAC, EU, and UK lists\n"
                f"- **Mixer/privacy tool interaction** detection\n"
                f"- **Structural pattern analysis** (fan-in/out, layering, smurfing)\n"
                f"- **Behavioral anomaly detection** using ML models\n\n"
                f"### Recommendation\n"
                f"Review the detailed factor breakdown in the Risk tab for specific triggers."
            )

        if "sar" in msg_lower or "report" in msg_lower:
            return (
                f"## SAR Generation\n\n"
                f"To generate a Suspicious Activity Report, use the Report Generation feature.\n"
                f"The SAR will include:\n"
                f"- Subject identification\n"
                f"- Suspicious activity description with evidence\n"
                f"- Transaction timeline and amounts\n"
                f"- Risk factor analysis\n"
                f"- Recommended actions"
            )

        return (
            f"## Analysis Summary\n\n"
            f"Based on the available data, I can assist with:\n"
            f"- **Risk explanation**: Understanding why a score was assigned\n"
            f"- **Transaction analysis**: Identifying suspicious patterns\n"
            f"- **Sanctions exposure**: Checking connections to sanctioned entities\n"
            f"- **Report generation**: Creating SAR narratives and executive summaries\n"
            f"- **Investigation guidance**: Recommending next steps\n\n"
            f"Please ask a specific question about the analysis results."
        )

    def _generate_fallback_summary(self, data: dict[str, Any]) -> str:
        """Generate executive summary without LLM."""
        return (
            f"# Executive Summary\n\n"
            f"## Overview\n"
            f"Analysis of address `{data.get('address', 'N/A')}` on "
            f"{data.get('chain', 'N/A')} blockchain reveals a risk score of "
            f"**{data.get('risk_score', 0)}/100** ({data.get('risk_level', 'N/A')}).\n\n"
            f"## Key Findings\n"
            f"- Balance: ${data.get('balance_usd', 0):,.2f}\n"
            f"- Total Transactions: {data.get('tx_count', 0)}\n"
            f"- Unique Counterparties: {data.get('counterparties', 0)}\n"
            f"- Anomaly Score: {data.get('anomaly_score', 0)}\n\n"
            f"## Risk Factors\n{data.get('risk_factors', 'None detected')}\n\n"
            f"## Recommendation\n"
            f"Further investigation is {'recommended' if data.get('risk_score', 0) > 50 else 'optional'} "
            f"based on the current risk profile."
        )

    def _generate_fallback_sar(self, data: dict[str, Any]) -> str:
        """Generate SAR narrative without LLM."""
        return (
            f"# Suspicious Activity Report\n\n"
            f"**Date**: {data.get('date', 'N/A')}\n"
            f"**Analyst**: {data.get('analyst_name', 'N/A')}\n\n"
            f"## Subject\n"
            f"Address: `{data.get('address', 'N/A')}`\n"
            f"Chain: {data.get('chain', 'N/A')}\n\n"
            f"## Suspicious Activity\n"
            f"Risk Score: {data.get('risk_score', 0)}/100\n\n"
            f"*Detailed SAR generation requires LLM configuration. "
            f"Please configure OpenAI API key or Ollama in settings.*"
        )

    def _generate_suggestions(
        self, message: str, context: dict[str, Any] | None
    ) -> list[str]:
        """Generate follow-up question suggestions."""
        return [
            "Why is the risk score this level?",
            "What are the most suspicious transactions?",
            "Is there any connection to sanctioned entities?",
            "What actions should an AML analyst take?",
            "Generate an executive summary",
            "Prepare a SAR report",
        ]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.http_client.aclose()
