"""Transaction graph endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.graph import (
    GraphBuildRequest,
    GraphData,
    GraphExpandRequest,
    GraphPathRequest,
)
from app.services.graph_service import GraphService

router = APIRouter()


@router.post("/build", response_model=GraphData)
async def build_graph(request: GraphBuildRequest) -> GraphData:
    """Build a transaction graph around an address."""
    try:
        service = GraphService()
        return await service.build_graph(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/expand", response_model=GraphData)
async def expand_graph_node(request: GraphExpandRequest) -> GraphData:
    """Expand a node to reveal its neighbors."""
    try:
        service = GraphService()
        return await service.expand_node(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/path", response_model=GraphData)
async def find_graph_path(request: GraphPathRequest) -> GraphData:
    """Find path between two addresses in the graph."""
    try:
        service = GraphService()
        return await service.find_path(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
