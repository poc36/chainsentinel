"""Graph visualization schemas."""

from typing import Any
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Node in the transaction graph."""

    id: str
    address: str
    label: str | None = None
    entity_type: str | None = None
    chain: str | None = None
    risk_score: int = 0
    risk_level: str = "minimal"
    balance_usd: float = 0.0
    color: str = "#4ade80"  # Default green for minimal risk


class GraphEdge(BaseModel):
    """Edge (transaction) in the graph."""

    id: str
    source: str
    target: str
    amount: float
    amount_usd: float
    token: str = "ETH"
    tx_hash: str | None = None
    fee: float = 0.0
    timestamp: str | None = None
    label: str | None = None


class GraphData(BaseModel):
    """Complete graph data for Cytoscape.js rendering."""

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    metadata: dict[str, Any] = {}


class GraphBuildRequest(BaseModel):
    """Request to build a transaction graph."""

    address: str
    chain: str | None = None
    depth: int = Field(default=2, ge=1, le=5)
    limit: int = Field(default=50, ge=1, le=200)
    direction: str = Field(default="both", pattern="^(in|out|both)$")


class GraphExpandRequest(BaseModel):
    """Request to expand a node's neighbors."""

    node_address: str
    chain: str
    depth: int = Field(default=1, ge=1, le=3)
    limit: int = Field(default=20, ge=1, le=100)


class GraphPathRequest(BaseModel):
    """Request to find paths between two addresses."""

    source: str
    target: str
    chain: str | None = None
    max_depth: int = Field(default=5, ge=1, le=10)
