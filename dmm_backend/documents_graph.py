"""
Graph Data Models for Simulation Editor
Stores visual graph representation of Buddhist scenario simulations

Collections:
- scenario_graphs: Graph documents with nodes and edges

Related to:
- documents_simulation.py: Exported as Scenario documents
- simulation_editor_router.py: API CRUD operations
"""

from beanie import Document
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums for Type Safety
# ============================================================================

class NodeType(str, Enum):
    """Types of nodes in the graph"""
    ACTOR = "actor"
    SCENARIO = "scenario"
    STATE = "state"
    SCENE = "scene"
    ENERGY_ORB = "energy_orb"


class EdgeType(str, Enum):
    """Types of edges in the graph"""
    ENERGY_LINE = "energy_line"       # Cyan animated line
    KARMA_LINE = "karma_line"         # Gold animated line
    CHOICE_LINE = "choice_line"       # White dashed line
    CONSEQUENCE_LINE = "consequence_line"  # Purple line


class ChoiceType(str, Enum):
    """Buddhist choice classification"""
    KUSALA = "kusala"       # Wholesome
    AKUSALA = "akusala"     # Unwholesome
    NEUTRAL = "neutral"     # Neutral


# ============================================================================
# Embedded Models (not stored as separate documents)
# ============================================================================

class Position(BaseModel):
    """2D position in the canvas"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    
    class Config:
        json_schema_extra = {
            "example": {"x": 250.5, "y": 100.0}
        }


class NodeStyle(BaseModel):
    """Visual styling for a node"""
    background_color: Optional[str] = Field(None, description="Background color (hex)")
    border_color: Optional[str] = Field(None, description="Border color (hex)")
    text_color: Optional[str] = Field(None, description="Text color (hex)")
    glow_intensity: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Glow effect intensity")
    opacity: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Node opacity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "background_color": "#1A2B3C",
                "border_color": "#5BD0E2",
                "text_color": "#FFFFFF",
                "glow_intensity": 0.6,
                "opacity": 1.0
            }
        }


class EdgeStyle(BaseModel):
    """Visual styling for an edge"""
    stroke_color: Optional[str] = Field("#5BD0E2", description="Line color (hex)")
    stroke_width: Optional[float] = Field(2.0, ge=0.5, le=10.0, description="Line width (px)")
    stroke_dasharray: Optional[str] = Field(None, description="Dash pattern (e.g., '5 5')")
    animated: Optional[bool] = Field(False, description="Enable energy flow animation")
    animation_speed: Optional[float] = Field(1.0, ge=0.1, le=5.0, description="Animation speed multiplier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stroke_color": "#5BD0E2",
                "stroke_width": 2.5,
                "stroke_dasharray": None,
                "animated": True,
                "animation_speed": 1.5
            }
        }


class GraphNode(BaseModel):
    """
    A node in the simulation graph
    Can represent: Actor, Scenario, State, Scene, or Energy Orb
    """
    # Identification
    node_id: str = Field(..., description="Unique node ID (generated)")
    node_type: NodeType = Field(..., description="Type of node")
    
    # Position
    position: Position = Field(..., description="Position in canvas")
    
    # Visual
    label: str = Field(..., max_length=100, description="Display label")
    style: Optional[NodeStyle] = Field(None, description="Custom styling")
    
    # Data (flexible per node type)
    data: Dict[str, Any] = Field(default_factory=dict, description="Node-specific data")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('node_id')
    def validate_node_id(cls, v):
        """Ensure node_id follows format: {type}_{timestamp}_{random}"""
        if not v or len(v) < 5:
            raise ValueError("node_id must be at least 5 characters")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "actor_1738000000_a1b2c3",
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
                    "avatar_url": "/avatars/moggallana.png",
                    "status": "active",
                    "specialty": "อิทธิบาท"
                },
                "created_at": "2025-01-27T10:30:00Z",
                "updated_at": "2025-01-27T10:30:00Z"
            }
        }


class GraphEdge(BaseModel):
    """
    An edge (connection) between two nodes
    Represents: Energy flow, Karma link, Choice path, or Consequence
    """
    # Identification
    edge_id: str = Field(..., description="Unique edge ID (generated)")
    edge_type: EdgeType = Field(..., description="Type of edge")
    
    # Connection
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    source_handle: Optional[str] = Field(None, description="Source connection point")
    target_handle: Optional[str] = Field(None, description="Target connection point")
    
    # Visual
    label: Optional[str] = Field(None, max_length=50, description="Edge label")
    style: Optional[EdgeStyle] = Field(None, description="Custom styling")
    
    # Data (flexible per edge type)
    data: Dict[str, Any] = Field(default_factory=dict, description="Edge-specific data")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('edge_id')
    def validate_edge_id(cls, v):
        """Ensure edge_id follows format: {type}_{timestamp}_{random}"""
        if not v or len(v) < 5:
            raise ValueError("edge_id must be at least 5 characters")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "edge_id": "energy_1738000000_x9y8z7",
                "edge_type": "energy_line",
                "source_node_id": "actor_1738000000_a1b2c3",
                "target_node_id": "scenario_1738000000_d4e5f6",
                "source_handle": "right",
                "target_handle": "left",
                "label": "มรรควิธี",
                "style": {
                    "stroke_color": "#5BD0E2",
                    "stroke_width": 2.5,
                    "animated": True,
                    "animation_speed": 1.5
                },
                "data": {
                    "energy_type": "wisdom",
                    "intensity": 0.8
                },
                "created_at": "2025-01-27T10:35:00Z",
                "updated_at": "2025-01-27T10:35:00Z"
            }
        }


class ViewportState(BaseModel):
    """Viewport state for canvas (zoom, pan position)"""
    x: float = Field(0.0, description="Pan position X")
    y: float = Field(0.0, description="Pan position Y")
    zoom: float = Field(1.0, ge=0.1, le=5.0, description="Zoom level")
    
    class Config:
        json_schema_extra = {
            "example": {"x": -150.0, "y": -75.0, "zoom": 1.2}
        }


# ============================================================================
# Main Document (stored in MongoDB)
# ============================================================================

class ScenarioGraph(Document):
    """
    Complete graph representing a Buddhist scenario simulation
    Stored in MongoDB collection: scenario_graphs
    
    A graph contains:
    - Nodes: Actors, Scenarios, States, Scenes, Energy Orbs
    - Edges: Energy lines, Karma lines, Choice paths, Consequences
    - Metadata: Title, description, analytics
    
    Can be exported to:
    - Scenario document (documents_simulation.py)
    - Teaching pack
    - QA test cases
    """
    
    # Identification
    graph_id: str = Field(..., description="Unique graph ID")
    title: str = Field(..., max_length=200, description="Graph title")
    description: Optional[str] = Field(None, max_length=1000, description="Graph description")
    
    # Structure
    nodes: List[GraphNode] = Field(default_factory=list, description="All nodes in graph")
    edges: List[GraphEdge] = Field(default_factory=list, description="All edges in graph")
    
    # Start point
    start_node_id: Optional[str] = Field(None, description="Entry point node ID")
    
    # Viewport
    viewport: ViewportState = Field(
        default_factory=ViewportState,
        description="Canvas viewport state"
    )
    
    # Metadata
    author_id: Optional[str] = Field(None, description="Creator user ID")
    category: Optional[str] = Field(None, description="Category (temptation, conflict, practice)")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")
    difficulty_level: Optional[float] = Field(None, ge=0.0, le=10.0, description="Overall difficulty")
    
    # Analytics (calculated)
    node_count: int = Field(0, description="Total node count")
    edge_count: int = Field(0, description="Total edge count")
    avg_path_length: Optional[float] = Field(None, description="Average path length")
    complexity_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Complexity score")
    
    # Status
    is_published: bool = Field(False, description="Published for simulation")
    is_validated: bool = Field(False, description="Passed validation")
    validation_errors: List[str] = Field(default_factory=list, description="Validation error messages")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(None)
    
    # Export tracking
    exported_as_scenario_id: Optional[str] = Field(None, description="Scenario document ID if exported")
    last_exported_at: Optional[datetime] = Field(None)
    
    class Settings:
        name = "scenario_graphs"
        indexes = [
            "graph_id",
            "author_id",
            "category",
            "is_published",
            [("created_at", -1)],  # Sort by newest first
            [("author_id", 1), ("created_at", -1)],  # User's graphs
        ]
    
    @validator('nodes', always=True)
    def update_node_count(cls, v, values):
        """Automatically update node_count"""
        values['node_count'] = len(v)
        return v
    
    @validator('edges', always=True)
    def update_edge_count(cls, v, values):
        """Automatically update edge_count"""
        values['edge_count'] = len(v)
        return v
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get node by ID"""
        return next((node for node in self.nodes if node.node_id == node_id), None)
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Get edge by ID"""
        return next((edge for edge in self.edges if edge.edge_id == edge_id), None)
    
    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph"""
        # Check for duplicate ID
        if any(n.node_id == node.node_id for n in self.nodes):
            raise ValueError(f"Node with ID '{node.node_id}' already exists")
        
        self.nodes.append(node)
        self.node_count = len(self.nodes)
        self.updated_at = datetime.utcnow()
    
    def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update a node's fields"""
        node = self.get_node(node_id)
        if not node:
            return False
        
        # Update fields
        for key, value in updates.items():
            if hasattr(node, key):
                setattr(node, key, value)
        
        node.updated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all connected edges
        Returns True if deleted, False if not found
        """
        node = self.get_node(node_id)
        if not node:
            return False
        
        # Remove node
        self.nodes = [n for n in self.nodes if n.node_id != node_id]
        
        # Remove connected edges
        self.edges = [
            e for e in self.edges
            if e.source_node_id != node_id and e.target_node_id != node_id
        ]
        
        self.node_count = len(self.nodes)
        self.edge_count = len(self.edges)
        self.updated_at = datetime.utcnow()
        return True
    
    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph"""
        # Validate that source and target nodes exist
        if not self.get_node(edge.source_node_id):
            raise ValueError(f"Source node '{edge.source_node_id}' not found")
        if not self.get_node(edge.target_node_id):
            raise ValueError(f"Target node '{edge.target_node_id}' not found")
        
        # Check for duplicate ID
        if any(e.edge_id == edge.edge_id for e in self.edges):
            raise ValueError(f"Edge with ID '{edge.edge_id}' already exists")
        
        self.edges.append(edge)
        self.edge_count = len(self.edges)
        self.updated_at = datetime.utcnow()
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge. Returns True if deleted, False if not found"""
        edge = self.get_edge(edge_id)
        if not edge:
            return False
        
        self.edges = [e for e in self.edges if e.edge_id != edge_id]
        self.edge_count = len(self.edges)
        self.updated_at = datetime.utcnow()
        return True
    
    def validate_graph(self) -> List[str]:
        """
        Validate graph structure and return list of errors
        Returns empty list if valid
        """
        errors = []
        
        # Must have at least one node
        if len(self.nodes) == 0:
            errors.append("Graph must have at least one node")
        
        # If start_node_id is set, it must exist
        if self.start_node_id:
            if not self.get_node(self.start_node_id):
                errors.append(f"Start node '{self.start_node_id}' not found")
        
        # Check all edges have valid source/target
        for edge in self.edges:
            if not self.get_node(edge.source_node_id):
                errors.append(f"Edge '{edge.edge_id}': source node '{edge.source_node_id}' not found")
            if not self.get_node(edge.target_node_id):
                errors.append(f"Edge '{edge.edge_id}': target node '{edge.target_node_id}' not found")
        
        # Check for isolated nodes (no connections)
        connected_node_ids = set()
        for edge in self.edges:
            connected_node_ids.add(edge.source_node_id)
            connected_node_ids.add(edge.target_node_id)
        
        isolated_nodes = [
            node.node_id for node in self.nodes
            if node.node_id not in connected_node_ids
        ]
        
        if len(isolated_nodes) > 1:  # Allow one isolated node (could be start)
            errors.append(f"Found {len(isolated_nodes)} isolated nodes: {isolated_nodes[:5]}")
        
        # Update validation status
        self.validation_errors = errors
        self.is_validated = len(errors) == 0
        
        return errors
    
    def calculate_complexity(self) -> float:
        """
        Calculate graph complexity score (0-100)
        Based on: node count, edge count, branching factor, path depth
        """
        if len(self.nodes) == 0:
            return 0.0
        
        # Node complexity (0-30 points)
        node_score = min(len(self.nodes) / 50.0 * 30, 30)
        
        # Edge complexity (0-30 points)
        edge_score = min(len(self.edges) / 100.0 * 30, 30)
        
        # Branching factor (0-20 points)
        # Count average outgoing edges per node
        outgoing_counts = {}
        for edge in self.edges:
            outgoing_counts[edge.source_node_id] = outgoing_counts.get(edge.source_node_id, 0) + 1
        
        avg_branching = sum(outgoing_counts.values()) / len(self.nodes) if self.nodes else 0
        branching_score = min(avg_branching / 5.0 * 20, 20)
        
        # Depth score (0-20 points) - estimate max path length
        # Simple heuristic: edge_count / node_count ratio
        depth_ratio = len(self.edges) / len(self.nodes) if self.nodes else 0
        depth_score = min(depth_ratio * 10, 20)
        
        total_score = node_score + edge_score + branching_score + depth_score
        
        self.complexity_score = round(total_score, 2)
        return self.complexity_score
    
    class Config:
        json_schema_extra = {
            "example": {
                "graph_id": "graph_20250127_abc123",
                "title": "ตลาดแห่งความอยาก (Marketplace of Desire)",
                "description": "สถานการณ์ทดสอบความอยากและกิเลสในตลาด",
                "nodes": [
                    {
                        "node_id": "actor_1738000000_a1b2c3",
                        "node_type": "actor",
                        "position": {"x": 100, "y": 100},
                        "label": "พระโมคคัลลานะ",
                        "data": {"actor_id": "6795c6b0e61fc68f72ae9c30"}
                    },
                    {
                        "node_id": "scenario_1738000000_d4e5f6",
                        "node_type": "scenario",
                        "position": {"x": 400, "y": 100},
                        "label": "เห็นของน่าทาน",
                        "data": {"sensory_input": "visual", "vedana": "pleasant"}
                    }
                ],
                "edges": [
                    {
                        "edge_id": "energy_1738000000_x9y8z7",
                        "edge_type": "energy_line",
                        "source_node_id": "actor_1738000000_a1b2c3",
                        "target_node_id": "scenario_1738000000_d4e5f6",
                        "label": "พบเจอ",
                        "style": {"animated": True}
                    }
                ],
                "start_node_id": "actor_1738000000_a1b2c3",
                "viewport": {"x": 0, "y": 0, "zoom": 1.0},
                "author_id": "user_123",
                "category": "temptation",
                "tags": ["lobha", "marketplace", "beginner"],
                "difficulty_level": 6.5,
                "node_count": 2,
                "edge_count": 1,
                "is_published": False,
                "is_validated": True,
                "created_at": "2025-01-27T10:00:00Z",
                "updated_at": "2025-01-27T10:30:00Z"
            }
        }


# ============================================================================
# Helper Functions
# ============================================================================

def generate_node_id(node_type: NodeType) -> str:
    """Generate unique node ID"""
    import random
    import string
    timestamp = int(datetime.utcnow().timestamp())
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{node_type.value}_{timestamp}_{random_suffix}"


def generate_edge_id(edge_type: EdgeType) -> str:
    """Generate unique edge ID"""
    import random
    import string
    timestamp = int(datetime.utcnow().timestamp())
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{edge_type.value}_{timestamp}_{random_suffix}"


def generate_graph_id() -> str:
    """Generate unique graph ID"""
    import random
    import string
    timestamp = int(datetime.utcnow().timestamp())
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"graph_{timestamp}_{random_suffix}"
