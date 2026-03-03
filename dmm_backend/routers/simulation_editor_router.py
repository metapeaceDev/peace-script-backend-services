"""
Simulation Editor API Router
Visual graph editor for Buddhist scenario simulations

Path: /api/simulation-editor/*
Provides CRUD operations for scenario graphs with nodes and edges
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

# Import graph models
from documents_graph import (
    ScenarioGraph,
    GraphNode,
    GraphEdge,
    Position,
    NodeStyle,
    EdgeStyle,
    ViewportState,
    NodeType,
    EdgeType,
    generate_node_id,
    generate_edge_id,
    generate_graph_id
)

# Import authentication
from dependencies.auth import get_current_user
from documents import User

router = APIRouter(
    prefix="/api/simulation-editor",
    tags=["simulation-editor"]
)


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateGraphRequest(BaseModel):
    """Request to create a new graph"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, description="temptation, conflict, practice")
    tags: List[str] = Field(default_factory=list)
    difficulty_level: Optional[float] = Field(None, ge=0.0, le=10.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "ตลาดแห่งความอยาก",
                "description": "สถานการณ์ทดสอบความอยากในตลาด",
                "category": "temptation",
                "tags": ["lobha", "beginner"],
                "difficulty_level": 6.5
            }
        }


class UpdateGraphRequest(BaseModel):
    """Request to update graph metadata"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty_level: Optional[float] = Field(None, ge=0.0, le=10.0)
    start_node_id: Optional[str] = None
    viewport: Optional[ViewportState] = None


class AddNodeRequest(BaseModel):
    """Request to add a node to graph"""
    node_type: NodeType
    position: Position
    label: str = Field(..., max_length=100)
    style: Optional[NodeStyle] = None
    data: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_type": "actor",
                "position": {"x": 250.0, "y": 100.0},
                "label": "พระโมคคัลลานะ",
                "style": {
                    "background_color": "#1A2B3C",
                    "border_color": "#5BD0E2",
                    "glow_intensity": 0.8
                },
                "data": {
                    "actor_id": "6795c6b0e61fc68f72ae9c30",
                    "status": "active"
                }
            }
        }


class UpdateNodeRequest(BaseModel):
    """Request to update a node"""
    position: Optional[Position] = None
    label: Optional[str] = Field(None, max_length=100)
    style: Optional[NodeStyle] = None
    data: Optional[dict] = None


class AddEdgeRequest(BaseModel):
    """Request to add an edge to graph"""
    edge_type: EdgeType
    source_node_id: str
    target_node_id: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None
    label: Optional[str] = Field(None, max_length=50)
    style: Optional[EdgeStyle] = None
    data: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "edge_type": "energy_line",
                "source_node_id": "actor_1738000000_abc123",
                "target_node_id": "scenario_1738000000_def456",
                "label": "พบเจอ",
                "style": {
                    "stroke_color": "#5BD0E2",
                    "animated": True,
                    "animation_speed": 1.5
                }
            }
        }


class GraphResponse(BaseModel):
    """Response with full graph data"""
    id: str = Field(..., alias="_id")
    graph_id: str
    title: str
    description: Optional[str]
    nodes: List[dict]
    edges: List[dict]
    start_node_id: Optional[str]
    viewport: dict
    author_id: Optional[str]
    category: Optional[str]
    tags: List[str]
    difficulty_level: Optional[float]
    node_count: int
    edge_count: int
    complexity_score: Optional[float]
    is_published: bool
    is_validated: bool
    validation_errors: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class GraphListItem(BaseModel):
    """Lightweight graph list item"""
    id: str = Field(..., alias="_id")
    graph_id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    tags: List[str]
    node_count: int
    edge_count: int
    complexity_score: Optional[float]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class ValidationResponse(BaseModel):
    """Graph validation result"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    complexity_score: Optional[float] = None


class AnalyticsResponse(BaseModel):
    """Graph analytics data"""
    node_count: int
    edge_count: int
    node_types: dict = Field(..., description="Count by node type")
    edge_types: dict = Field(..., description="Count by edge type")
    avg_path_length: Optional[float] = None
    complexity_score: float
    isolated_nodes: int = Field(..., description="Nodes with no connections")
    max_depth: Optional[int] = Field(None, description="Maximum path depth from start")


# ============================================================================
# Graph CRUD Endpoints
# ============================================================================

@router.post("/graphs", response_model=GraphResponse, status_code=status.HTTP_201_CREATED)
async def create_graph(
    request: CreateGraphRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new scenario graph
    🔒 Protected: Requires authentication
    
    Creates an empty graph with metadata.
    Use node/edge endpoints to populate it.
    """
    graph = ScenarioGraph(
        graph_id=generate_graph_id(),
        title=request.title,
        description=request.description,
        author_id=str(current_user.id),
        category=request.category,
        tags=request.tags,
        difficulty_level=request.difficulty_level
    )
    
    await graph.insert()
    
    return GraphResponse(
        _id=str(graph.id),
        graph_id=graph.graph_id,
        title=graph.title,
        description=graph.description,
        nodes=[node.dict() for node in graph.nodes],
        edges=[edge.dict() for edge in graph.edges],
        start_node_id=graph.start_node_id,
        viewport=graph.viewport.dict(),
        author_id=graph.author_id,
        category=graph.category,
        tags=graph.tags,
        difficulty_level=graph.difficulty_level,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        complexity_score=graph.complexity_score,
        is_published=graph.is_published,
        is_validated=graph.is_validated,
        validation_errors=graph.validation_errors,
        created_at=graph.created_at,
        updated_at=graph.updated_at
    )


@router.get("/graphs", response_model=List[GraphListItem])
async def list_graphs(
    category: Optional[str] = None,
    is_published: Optional[bool] = None,
    author_id: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    List all graphs (with filters)
    🔒 Protected: Requires authentication
    
    Query Parameters:
    - category: Filter by category
    - is_published: Filter by published status
    - author_id: Filter by author (defaults to current user if omitted)
    - limit: Max results (default 50)
    - skip: Pagination offset
    """
    # Build filter query
    query_filter = {}
    
    if author_id:
        query_filter["author_id"] = author_id
    else:
        # Default to current user's graphs
        query_filter["author_id"] = str(current_user.id)
    
    if category:
        query_filter["category"] = category
    
    if is_published is not None:
        query_filter["is_published"] = is_published
    
    # Query database
    graphs = await ScenarioGraph.find(query_filter)\
        .sort("-created_at")\
        .skip(skip)\
        .limit(limit)\
        .to_list()
    
    return [
        GraphListItem(
            _id=str(g.id),
            graph_id=g.graph_id,
            title=g.title,
            description=g.description,
            category=g.category,
            tags=g.tags,
            node_count=g.node_count,
            edge_count=g.edge_count,
            complexity_score=g.complexity_score,
            is_published=g.is_published,
            created_at=g.created_at,
            updated_at=g.updated_at
        )
        for g in graphs
    ]


@router.get("/graphs/{graph_id}", response_model=GraphResponse)
async def get_graph(
    graph_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific graph by ID
    🔒 Protected: Requires authentication
    
    Returns full graph with all nodes and edges.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission (author or admin)
    is_author = graph.author_id == str(current_user.id)
    is_admin = "admin" in current_user.roles
    
    if not is_author and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this graph"
        )
    
    return GraphResponse(
        _id=str(graph.id),
        graph_id=graph.graph_id,
        title=graph.title,
        description=graph.description,
        nodes=[node.dict() for node in graph.nodes],
        edges=[edge.dict() for edge in graph.edges],
        start_node_id=graph.start_node_id,
        viewport=graph.viewport.dict(),
        author_id=graph.author_id,
        category=graph.category,
        tags=graph.tags,
        difficulty_level=graph.difficulty_level,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        complexity_score=graph.complexity_score,
        is_published=graph.is_published,
        is_validated=graph.is_validated,
        validation_errors=graph.validation_errors,
        created_at=graph.created_at,
        updated_at=graph.updated_at
    )


@router.patch("/graphs/{graph_id}", response_model=GraphResponse)
async def update_graph(
    graph_id: str,
    request: UpdateGraphRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update graph metadata
    🔒 Protected: Requires authentication
    
    Updates title, description, category, tags, etc.
    Does not modify nodes/edges (use dedicated endpoints).
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this graph"
        )
    
    # Update fields (only if provided)
    update_data = request.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(graph, field, value)
    
    graph.updated_at = datetime.utcnow()
    await graph.save()
    
    return GraphResponse(
        _id=str(graph.id),
        graph_id=graph.graph_id,
        title=graph.title,
        description=graph.description,
        nodes=[node.dict() for node in graph.nodes],
        edges=[edge.dict() for edge in graph.edges],
        start_node_id=graph.start_node_id,
        viewport=graph.viewport.dict(),
        author_id=graph.author_id,
        category=graph.category,
        tags=graph.tags,
        difficulty_level=graph.difficulty_level,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        complexity_score=graph.complexity_score,
        is_published=graph.is_published,
        is_validated=graph.is_validated,
        validation_errors=graph.validation_errors,
        created_at=graph.created_at,
        updated_at=graph.updated_at
    )


@router.delete("/graphs/{graph_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_graph(
    graph_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a graph permanently
    🔒 Protected: Requires authentication
    
    Deletes graph and all its nodes/edges.
    This action cannot be undone.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this graph"
        )
    
    await graph.delete()
    
    return None  # 204 No Content


# ============================================================================
# Node Operations
# ============================================================================

@router.post("/graphs/{graph_id}/nodes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_node(
    graph_id: str,
    request: AddNodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add a node to the graph
    🔒 Protected: Requires authentication
    
    Creates a new node with auto-generated ID.
    Returns the created node with its ID.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this graph"
        )
    
    # Create node
    node = GraphNode(
        node_id=generate_node_id(request.node_type),
        node_type=request.node_type,
        position=request.position,
        label=request.label,
        style=request.style,
        data=request.data
    )
    
    # Add to graph
    graph.add_node(node)
    await graph.save()
    
    return node.dict()


@router.patch("/graphs/{graph_id}/nodes/{node_id}", response_model=dict)
async def update_node(
    graph_id: str,
    node_id: str,
    request: UpdateNodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update a node's properties
    🔒 Protected: Requires authentication
    
    Updates position, label, style, or data.
    Only provided fields are updated.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this graph"
        )
    
    # Update node
    updates = request.dict(exclude_unset=True)
    success = graph.update_node(node_id, updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found in graph"
        )
    
    await graph.save()
    
    updated_node = graph.get_node(node_id)
    return updated_node.dict()


@router.delete("/graphs/{graph_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    graph_id: str,
    node_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a node from the graph
    🔒 Protected: Requires authentication
    
    Deletes the node and all connected edges.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this graph"
        )
    
    # Delete node (also removes connected edges)
    success = graph.delete_node(node_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' not found in graph"
        )
    
    await graph.save()
    
    return None  # 204 No Content


# ============================================================================
# Edge Operations
# ============================================================================

@router.post("/graphs/{graph_id}/edges", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_edge(
    graph_id: str,
    request: AddEdgeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add an edge to the graph
    🔒 Protected: Requires authentication
    
    Creates a connection between two nodes.
    Both source and target nodes must exist.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this graph"
        )
    
    # Create edge
    edge = GraphEdge(
        edge_id=generate_edge_id(request.edge_type),
        edge_type=request.edge_type,
        source_node_id=request.source_node_id,
        target_node_id=request.target_node_id,
        source_handle=request.source_handle,
        target_handle=request.target_handle,
        label=request.label,
        style=request.style,
        data=request.data
    )
    
    # Add to graph (validates that nodes exist)
    try:
        graph.add_edge(edge)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    await graph.save()
    
    return edge.dict()


@router.delete("/graphs/{graph_id}/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    graph_id: str,
    edge_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an edge from the graph
    🔒 Protected: Requires authentication
    
    Removes the connection between two nodes.
    Nodes remain intact.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Check permission
    if graph.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this graph"
        )
    
    # Delete edge
    success = graph.delete_edge(edge_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edge '{edge_id}' not found in graph"
        )
    
    await graph.save()
    
    return None  # 204 No Content


# ============================================================================
# Advanced Operations
# ============================================================================

@router.post("/graphs/{graph_id}/validate", response_model=ValidationResponse)
async def validate_graph(
    graph_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Validate graph structure
    🔒 Protected: Requires authentication
    
    Checks for:
    - At least one node
    - Valid start node (if set)
    - All edges have valid source/target
    - No excessive isolated nodes
    
    Returns validation errors and complexity score.
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Validate
    errors = graph.validate_graph()
    complexity = graph.calculate_complexity()
    
    # Save validation results
    await graph.save()
    
    return ValidationResponse(
        is_valid=len(errors) == 0,
        errors=errors,
        complexity_score=complexity
    )


@router.get("/graphs/{graph_id}/analytics", response_model=AnalyticsResponse)
async def get_graph_analytics(
    graph_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get graph analytics and metrics
    🔒 Protected: Requires authentication
    
    Returns:
    - Node/edge counts
    - Type distribution
    - Complexity metrics
    - Path statistics
    """
    graph = await ScenarioGraph.find_one({"graph_id": graph_id})
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph '{graph_id}' not found"
        )
    
    # Calculate node type distribution
    node_types = {}
    for node in graph.nodes:
        node_type = node.node_type.value
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    # Calculate edge type distribution
    edge_types = {}
    for edge in graph.edges:
        edge_type = edge.edge_type.value
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    # Find isolated nodes
    connected_node_ids = set()
    for edge in graph.edges:
        connected_node_ids.add(edge.source_node_id)
        connected_node_ids.add(edge.target_node_id)
    
    isolated_count = len([
        n for n in graph.nodes
        if n.node_id not in connected_node_ids
    ])
    
    # Calculate complexity
    complexity = graph.calculate_complexity()
    
    # Calculate average path length (BFS from start node)
    avg_path_length = None
    if graph.start_node_id:
        # Build adjacency list
        adj_list = {}
        for node in graph.nodes:
            adj_list[node.node_id] = []
        for edge in graph.edges:
            adj_list[edge.source_node_id].append(edge.target_node_id)
        
        # BFS to calculate all path lengths from start
        from collections import deque
        visited = {graph.start_node_id: 0}
        queue = deque([(graph.start_node_id, 0)])
        path_lengths = []
        
        while queue:
            node_id, depth = queue.popleft()
            for neighbor in adj_list.get(node_id, []):
                if neighbor not in visited:
                    visited[neighbor] = depth + 1
                    path_lengths.append(depth + 1)
                    queue.append((neighbor, depth + 1))
        
        avg_path_length = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
    
    # Calculate max depth (longest path from start node)
    max_depth = None
    if graph.start_node_id and visited:
        max_depth = max(visited.values()) if visited else 0
    
    return AnalyticsResponse(
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        node_types=node_types,
        edge_types=edge_types,
        avg_path_length=round(avg_path_length, 2) if avg_path_length is not None else None,
        complexity_score=complexity,
        isolated_nodes=isolated_count,
        max_depth=max_depth
    )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint (public)"""
    # Count total graphs
    total_graphs = await ScenarioGraph.count()
    published_graphs = await ScenarioGraph.find({"is_published": True}).count()
    
    return {
        "status": "healthy",
        "total_graphs": total_graphs,
        "published_graphs": published_graphs,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Startup Event
# ============================================================================

@router.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🎨 Simulation Editor Router initialized - simulation_editor_router.py")
    
    # Count existing graphs (wrapped in try-except for initialization timing)
    try:
        total = await ScenarioGraph.count()
        print(f"✅ {total} scenario graphs in database")
    except Exception as e:
        print(f"⚠️  Could not count graphs yet (DB may still be initializing): {e}")

