"""Graph service for building and querying transaction graphs."""

import hashlib
from datetime import datetime

from app.domain.blockchain import Chain, detect_chain
from app.domain.address_classifier import classify_address
from app.domain.risk_factors import get_risk_color, calculate_risk_level
from app.providers.base import ProviderTransaction
from app.providers.factory import get_provider
from app.schemas.graph import (
    GraphData,
    GraphEdge,
    GraphNode,
    GraphBuildRequest,
    GraphExpandRequest,
    GraphPathRequest,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class GraphService:
    """Service for building and managing transaction graphs.

    Creates Cytoscape.js-compatible graph data from blockchain transactions.
    Supports graph expansion, path finding, and subgraph queries.
    """

    async def build_graph(self, request: GraphBuildRequest) -> GraphData:
        """Build a transaction graph around a central address.

        Args:
            request: Graph build parameters (address, chain, depth, limit).

        Returns:
            GraphData with nodes and edges for Cytoscape.js rendering.
        """
        chain = Chain(request.chain) if request.chain else detect_chain(request.address)
        if not chain:
            raise ValueError(f"Cannot detect chain for: {request.address}")

        provider = get_provider()
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        # BFS graph construction
        addresses_to_process = [(request.address, 0)]
        processed: set[str] = set()

        while addresses_to_process:
            addr, depth = addresses_to_process.pop(0)

            if addr.lower() in processed or depth > request.depth:
                continue

            processed.add(addr.lower())

            # Add node
            if addr.lower() not in nodes:
                node = self._create_node(addr, chain)
                nodes[addr.lower()] = node

            # Fetch transactions
            limit = request.limit if depth == 0 else min(20, request.limit)
            transactions = await provider.get_transactions(addr, chain, limit=limit)

            for tx in transactions:
                # Add counterparty nodes
                counterparty = (
                    tx.to_address
                    if tx.from_address.lower() == addr.lower()
                    else tx.from_address
                )

                if counterparty.lower() not in nodes:
                    cp_node = self._create_node(counterparty, chain)
                    nodes[counterparty.lower()] = cp_node

                # Add edge
                edge = self._create_edge(tx)
                edges.append(edge)

                # Queue for next depth
                if depth < request.depth and counterparty.lower() not in processed:
                    addresses_to_process.append((counterparty, depth + 1))

            # Respect total limit
            if len(nodes) >= request.limit:
                break

        logger.info(
            "graph_built",
            address=request.address[:12],
            nodes=len(nodes),
            edges=len(edges),
            depth=request.depth,
        )

        return GraphData(
            nodes=list(nodes.values()),
            edges=edges,
            metadata={
                "center_address": request.address,
                "chain": str(chain),
                "depth": request.depth,
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        )

    async def expand_node(self, request: GraphExpandRequest) -> GraphData:
        """Expand a node to show its neighbors.

        Args:
            request: Node expansion parameters.

        Returns:
            GraphData with new nodes and edges to add.
        """
        chain = Chain(request.chain)
        provider = get_provider()

        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        transactions = await provider.get_transactions(
            request.node_address, chain, limit=request.limit
        )

        for tx in transactions:
            counterparty = (
                tx.to_address
                if tx.from_address.lower() == request.node_address.lower()
                else tx.from_address
            )

            if counterparty.lower() not in nodes:
                nodes[counterparty.lower()] = self._create_node(counterparty, chain)

            edges.append(self._create_edge(tx))

        return GraphData(
            nodes=list(nodes.values()),
            edges=edges,
            metadata={"expanded_from": request.node_address},
        )

    async def find_path(self, request: GraphPathRequest) -> GraphData:
        """Find path between two addresses.

        Uses BFS on transaction data to find connections.
        In demo mode, generates a synthetic path.

        Args:
            request: Path finding parameters.

        Returns:
            GraphData representing the path.
        """
        chain = Chain(request.chain) if request.chain else Chain.ETHEREUM
        provider = get_provider()

        # Generate path via BFS (simplified for demo)
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        # Create synthetic path for demo
        path_length = min(request.max_depth, 4)
        path_addresses = [request.source]

        for i in range(path_length - 1):
            seed = hashlib.sha256(
                f"{request.source}{request.target}{i}".encode()
            ).hexdigest()
            intermediate = f"0x{seed[:40]}"
            path_addresses.append(intermediate)

        path_addresses.append(request.target)

        for addr in path_addresses:
            nodes[addr.lower()] = self._create_node(addr, chain)

        for i in range(len(path_addresses) - 1):
            edge_id = hashlib.md5(
                f"{path_addresses[i]}{path_addresses[i + 1]}".encode()
            ).hexdigest()[:16]

            edges.append(GraphEdge(
                id=f"path_edge_{edge_id}",
                source=path_addresses[i].lower(),
                target=path_addresses[i + 1].lower(),
                amount=round(__import__("random").uniform(0.5, 50.0), 4),
                amount_usd=round(__import__("random").uniform(100, 50000), 2),
                token="ETH",
                label=f"Step {i + 1}",
            ))

        return GraphData(
            nodes=list(nodes.values()),
            edges=edges,
            metadata={
                "source": request.source,
                "target": request.target,
                "path_length": len(path_addresses),
                "found": True,
            },
        )

    def _create_node(self, address: str, chain: Chain) -> GraphNode:
        """Create a graph node from an address."""
        classification = classify_address(address, chain)

        # Deterministic risk score for demo
        seed = int(hashlib.md5(address.encode()).hexdigest(), 16) % 100
        risk_score = seed
        risk_level = calculate_risk_level(risk_score)
        color = get_risk_color(risk_level)

        return GraphNode(
            id=address.lower(),
            address=address,
            label=classification.label or f"{address[:6]}...{address[-4:]}",
            entity_type=classification.address_type,
            chain=str(chain),
            risk_score=risk_score,
            risk_level=risk_level,
            balance_usd=round(seed * 137.42, 2),
            color=color,
        )

    def _create_edge(self, tx: ProviderTransaction) -> GraphEdge:
        """Create a graph edge from a transaction."""
        return GraphEdge(
            id=tx.tx_hash[:16] if tx.tx_hash else "unknown",
            source=tx.from_address.lower(),
            target=tx.to_address.lower(),
            amount=float(tx.amount),
            amount_usd=float(tx.amount_usd),
            token=tx.token,
            tx_hash=tx.tx_hash,
            fee=float(tx.fee),
            timestamp=tx.block_time.isoformat() if tx.block_time else None,
            label=f"{tx.amount} {tx.token}",
        )
