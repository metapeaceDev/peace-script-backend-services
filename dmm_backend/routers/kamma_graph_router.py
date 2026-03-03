"""
Kamma-Vipāka Graph API Router

REST API endpoints for Kamma-Vipāka Explorer visualization.
Provides graph data, node details, causality chains, and search functionality.

Author: PeaceScript Team
Date: 6 November 2024
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from models.kamma_graph import KammaNode, KammaEdge, KammaGraph
from helpers.kamma_graph_builder import KammaGraphBuilder
from kamma_engine import KammaStorage


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GetGraphRequest(BaseModel):
    """Request parameters for getting a graph"""
    life_range_min: int = Field(-12, ge=-12, le=0, description="Minimum life index")
    life_range_max: int = Field(0, ge=-12, le=0, description="Maximum life index")
    filter_type: Optional[str] = Field(None, description="Filter by type: kusala/akusala/None")
    include_vipaka: bool = Field(True, description="Include vipaka (result) nodes")


class GetGraphResponse(BaseModel):
    """Response containing full graph data"""
    success: bool
    graph: KammaGraph
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (storage stats, etc.)"
    )


class NodeDetailResponse(BaseModel):
    """Response for single node detail"""
    success: bool
    node: KammaNode
    related_edges: List[KammaEdge] = Field(
        default_factory=list,
        description="All edges connected to this node"
    )
    predecessors: List[str] = Field(
        default_factory=list,
        description="Parent node IDs"
    )
    successors: List[str] = Field(
        default_factory=list,
        description="Child node IDs"
    )


class TracebackRequest(BaseModel):
    """Request for causality chain tracing"""
    start_node_id: str = Field(..., description="Starting node ID")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum chain depth")
    direction: str = Field(
        "forward",
        description="Trace direction: forward (effects) or backward (causes)"
    )


class CausalityChain(BaseModel):
    """Single causality chain"""
    chain_id: str = Field(..., description="Unique chain ID")
    nodes: List[str] = Field(..., description="Node IDs in order")
    length: int = Field(..., description="Chain length")
    total_weight: float = Field(..., description="Sum of node weights")
    chain_type: str = Field(..., description="kusala/akusala/mixed")


class TracebackResponse(BaseModel):
    """Response containing causality chains"""
    success: bool
    start_node_id: str
    chains: List[CausalityChain]
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Statistics about found chains"
    )


class SearchNodesRequest(BaseModel):
    """Request for searching nodes"""
    query: str = Field("", description="Search in label")
    node_type: Optional[str] = Field(None, description="Filter by type")
    life_index: Optional[int] = Field(None, ge=-12, le=0, description="Filter by life")
    realm: Optional[str] = Field(None, description="Filter by realm")
    min_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = Field(None, description="Must contain all tags")


class SearchNodesResponse(BaseModel):
    """Response containing search results"""
    success: bool
    results: List[KammaNode]
    total_count: int
    query_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Query parameters used"
    )


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="/api/kamma-graph",
    tags=["Kamma-Vipāka Graph"],
    responses={404: {"model": ErrorResponse}}
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_kamma_storage(model_id: str) -> KammaStorage:
    """
    Retrieve KammaStorage for a character from database.
    
    Args:
        model_id: Character ID
        
    Returns:
        KammaStorage object (empty if not found)
    """
    # Get profile from database
    from documents import DigitalMindModel
    profile = await DigitalMindModel.find_one(
        DigitalMindModel.model_id == model_id
    )
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Character {model_id} not found"
        )
    
    # Check if has kamma_profile (kamma_storage is stored in kamma_profile field)
    kamma_data = profile.kamma_profile if hasattr(profile, 'kamma_profile') else None
    if not kamma_data or not isinstance(kamma_data, dict):
        # Return empty storage
        return KammaStorage(character_id=model_id)
    
    # Parse as KammaStorage
    try:
        kamma_dict = dict(kamma_data)
        kamma_dict["character_id"] = model_id
        storage = KammaStorage(**kamma_dict)
        return storage
    except Exception:
        # If parsing fails, return empty storage
        return KammaStorage(character_id=model_id)


def get_life_history(profile) -> List[Dict[str, Any]]:
    """
    Get life history from profile (placeholder for future implementation).
    
    Args:
        profile: DigitalMindModel document
        
    Returns:
        List of past life events (empty for now)
    """
    # Past life events will be implemented in Phase 2 when life history tracking is added
    # Current implementation focuses on single-lifetime kamma tracking
    # Return empty list as all kamma is tracked in current life for now
    return []


# ============================================================================
# ENDPOINT 0: Health Check
# ============================================================================

@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Health Check",
    description="Check if Kamma Graph API is operational"
)
async def kamma_graph_health_check():
    """
    Health check endpoint for Kamma-Vipāka Graph API
    
    **Returns**: Status and version information
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "kamma-graph-api",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# ENDPOINT 1: Get Full Graph
# ============================================================================

@router.get(
    "/{model_id}",
    response_model=GetGraphResponse,
    summary="Get Kamma-Vipāka Graph",
    description="Get complete graph visualization for a character"
)
async def get_kamma_graph(
    model_id: str,
    life_range_min: int = Query(-12, ge=-12, le=0, description="Min life index"),
    life_range_max: int = Query(0, ge=-12, le=0, description="Max life index"),
    filter_type: Optional[str] = Query(None, description="kusala/akusala/None"),
    include_vipaka: bool = Query(True, description="Include vipaka nodes")
):
    """
    Get complete Kamma-Vipāka graph for visualization
    
    **Process**:
    1. Load KammaStorage from database
    2. Build graph with specified filters
    3. Return nodes, edges, and summary
    
    **Example**:
    ```
    GET /api/kamma-graph/char_123?life_range_min=-3&life_range_max=0&filter_type=kusala
    ```
    
    **Response**: Complete graph with nodes, edges, summary statistics
    """
    try:
        # Get storage
        storage = await get_kamma_storage(model_id)
        
        # Get life history (if available)
        from documents import DigitalMindModel
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        life_history = get_life_history(profile.dict()) if profile else []
        
        # Build graph
        builder = KammaGraphBuilder(storage, life_history=life_history)
        graph = builder.build_graph(
            model_id=model_id,
            life_range=(life_range_min, life_range_max),
            filter_type=filter_type,
            include_vipaka=include_vipaka
        )
        
        # Metadata
        metadata = {
            # Top-level fields expected by tests
            "total_records": len(graph.nodes),
            "kusala_count": graph.summary.get("kusala_count", 0),
            "akusala_count": graph.summary.get("akusala_count", 0),
            
            # Additional details
            "storage_stats": {
                "active_kusala": len(storage.active_kusala),
                "active_akusala": len(storage.active_akusala),
                "ripened_kusala": len(storage.ripened_kusala),
                "ripened_akusala": len(storage.ripened_akusala),
                "total_kusala": storage.total_kusala_created,
                "total_akusala": storage.total_akusala_created
            },
            "graph_stats": {
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "kusala_count": graph.summary.get("kusala_count", 0),
                "akusala_count": graph.summary.get("akusala_count", 0)
            },
            "filters_applied": {
                "life_range": [life_range_min, life_range_max],
                "filter_type": filter_type,
                "include_vipaka": include_vipaka
            }
        }
        
        return GetGraphResponse(
            success=True,
            graph=graph,
            metadata=metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build graph: {str(e)}"
        )


@router.get(
    "/{model_id}/node/{node_id}",
    response_model=NodeDetailResponse,
    summary="Get Node Detail",
    description="Get detailed information about a specific node"
)
async def get_node_detail(
    model_id: str,
    node_id: str
):
    """
    Get detailed information about a specific node
    
    **Returns**:
    - Node data
    - Connected edges
    - Parent nodes (predecessors)
    - Child nodes (successors)
    
    **Example**:
    ```
    GET /api/kamma-graph/char_123/node/node_abc123
    ```
    """
    try:
        # Get storage and build full graph
        storage = await get_kamma_storage(model_id)
        from documents import DigitalMindModel
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        life_history = get_life_history(profile) if profile else []
        
        builder = KammaGraphBuilder(storage, life_history=life_history)
        graph = builder.build_graph(model_id=model_id)
        
        # Find node
        node = graph.get_node_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=404,
                detail=f"Node {node_id} not found"
            )
        
        # Get related data
        related_edges = graph.get_edges_for_node(node_id)
        predecessors = graph.get_predecessors(node_id)
        successors = graph.get_successors(node_id)
        
        return NodeDetailResponse(
            success=True,
            node=node,
            related_edges=related_edges,
            predecessors=predecessors,
            successors=successors
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get node detail: {str(e)}"
        )


@router.post(
    "/{model_id}/traceback",
    response_model=TracebackResponse,
    summary="Trace Causality Chains",
    description="Find causality chains from a starting node"
)
async def trace_causality_chains(
    model_id: str,
    request: TracebackRequest = Body(...)
):
    """
    Trace causality chains (forward or backward) from a starting node
    
    **Forward**: Find effects/results of this kamma
    **Backward**: Find causes/origins of this kamma
    
    **Example Request**:
    ```json
    {
        "start_node_id": "node_abc123",
        "max_depth": 5,
        "direction": "forward"
    }
    ```
    
    **Response**: List of causality chains with statistics
    """
    try:
        # Get storage and build graph
        storage = await get_kamma_storage(model_id)
        from documents import DigitalMindModel
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        life_history = get_life_history(profile) if profile else []
        
        builder = KammaGraphBuilder(storage, life_history=life_history)
        graph = builder.build_graph(model_id=model_id)
        
        # Check node exists
        node = graph.get_node_by_id(request.start_node_id)
        if not node:
            raise HTTPException(
                status_code=404,
                detail=f"Node {request.start_node_id} not found"
            )
        
        # Find chains
        if request.direction == "forward":
            # Forward: successors (effects)
            raw_chains = builder.find_causality_chains(
                request.start_node_id,
                max_depth=request.max_depth
            )
        else:
            # Backward: predecessors (causes)
            # Reverse graph and find chains
            # TODO: Implement backward tracing
            raw_chains = []
        
        # Convert to CausalityChain objects
        chains: List[CausalityChain] = []
        for i, chain_nodes in enumerate(raw_chains):
            # Calculate chain properties
            total_weight = 0.0
            for nid in chain_nodes:
                node = graph.get_node_by_id(nid)
                if node:
                    total_weight += node.weight
            
            # Determine chain type
            chain_types = set()
            for nid in chain_nodes:
                n = graph.get_node_by_id(nid)
                if n:
                    if "kusala" in n.tags:
                        chain_types.add("kusala")
                    elif "akusala" in n.tags:
                        chain_types.add("akusala")
            
            if len(chain_types) > 1:
                chain_type = "mixed"
            elif "kusala" in chain_types:
                chain_type = "kusala"
            elif "akusala" in chain_types:
                chain_type = "akusala"
            else:
                chain_type = "neutral"
            
            chains.append(CausalityChain(
                chain_id=f"chain_{i+1}",
                nodes=chain_nodes,
                length=len(chain_nodes),
                total_weight=total_weight,
                chain_type=chain_type
            ))
        
        # Summary statistics
        summary = {
            "total_chains": len(chains),
            "avg_length": sum(c.length for c in chains) / len(chains) if chains else 0,
            "max_length": max((c.length for c in chains), default=0),
            "kusala_chains": len([c for c in chains if c.chain_type == "kusala"]),
            "akusala_chains": len([c for c in chains if c.chain_type == "akusala"]),
            "mixed_chains": len([c for c in chains if c.chain_type == "mixed"])
        }
        
        return TracebackResponse(
            success=True,
            start_node_id=request.start_node_id,
            chains=chains,
            summary=summary
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trace chains: {str(e)}"
        )


@router.post(
    "/{model_id}/search",
    response_model=SearchNodesResponse,
    summary="Search Nodes",
    description="Search nodes by various criteria"
)
async def search_nodes(
    model_id: str,
    request: SearchNodesRequest = Body(...)
):
    """
    Search nodes with advanced filtering
    
    **Filter Options**:
    - query: Text search in label
    - node_type: kamma/vipaka/neutral
    - life_index: Specific life (-12 to 0)
    - realm: มนุษย์, เทวดา, etc.
    - min_weight/max_weight: Weight range
    - tags: Must contain all specified tags
    
    **Example Request**:
    ```json
    {
        "query": "generosity",
        "node_type": "kamma",
        "min_weight": 0.7,
        "tags": ["kusala"]
    }
    ```
    
    **Response**: List of matching nodes
    """
    try:
        # Get storage and build graph
        storage = await get_kamma_storage(model_id)
        from documents import DigitalMindModel
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        life_history = get_life_history(profile) if profile else []
        
        builder = KammaGraphBuilder(storage, life_history=life_history)
        graph = builder.build_graph(model_id=model_id)
        
        # Search
        results = builder.search_nodes(
            query=request.query,
            node_type=request.node_type,
            life_index=request.life_index,
            realm=request.realm,
            min_weight=request.min_weight,
            max_weight=request.max_weight,
            tags=request.tags
        )
        
        # Query info for debugging
        query_info = {
            "query": request.query,
            "node_type": request.node_type,
            "life_index": request.life_index,
            "realm": request.realm,
            "weight_range": [request.min_weight, request.max_weight],
            "tags": request.tags,
            "total_nodes_in_graph": len(graph.nodes)
        }
        
        return SearchNodesResponse(
            success=True,
            results=results,
            total_count=len(results),
            query_info=query_info
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search nodes: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/health",
    summary="Health Check",
    description="Check if Kamma Graph API is operational"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "kamma-graph-api",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    }
