"""
Unit Tests for Graph Data Models (documents_graph.py)
Tests ScenarioGraph, GraphNode, GraphEdge and helper functions
"""

import pytest
from datetime import datetime
from documents_graph import (
    # Enums
    NodeType,
    EdgeType,
    ChoiceType,
    # Models
    Position,
    NodeStyle,
    EdgeStyle,
    GraphNode,
    GraphEdge,
    ViewportState,
    ScenarioGraph,
    # Helpers
    generate_node_id,
    generate_edge_id,
    generate_graph_id
)
from pydantic import ValidationError


# ============================================================================
# Test Helper Functions
# ============================================================================

def test_generate_node_id():
    """Test node ID generation"""
    node_id = generate_node_id(NodeType.ACTOR)
    
    assert node_id.startswith("actor_")
    assert len(node_id) > 15  # actor_ + timestamp + _ + random
    
    # Test different types
    scenario_id = generate_node_id(NodeType.SCENARIO)
    assert scenario_id.startswith("scenario_")
    
    # IDs should be unique
    assert node_id != generate_node_id(NodeType.ACTOR)


def test_generate_edge_id():
    """Test edge ID generation"""
    edge_id = generate_edge_id(EdgeType.ENERGY_LINE)
    
    assert edge_id.startswith("energy_line_")
    assert len(edge_id) > 20
    
    # Test different types
    karma_id = generate_edge_id(EdgeType.KARMA_LINE)
    assert karma_id.startswith("karma_line_")


def test_generate_graph_id():
    """Test graph ID generation"""
    graph_id = generate_graph_id()
    
    assert graph_id.startswith("graph_")
    assert len(graph_id) > 15


# ============================================================================
# Test Embedded Models
# ============================================================================

def test_position_model():
    """Test Position model"""
    pos = Position(x=100.5, y=200.0)
    
    assert pos.x == 100.5
    assert pos.y == 200.0
    
    # Test negative coordinates
    neg_pos = Position(x=-50, y=-100)
    assert neg_pos.x == -50


def test_node_style_model():
    """Test NodeStyle model"""
    style = NodeStyle(
        background_color="#1A2B3C",
        border_color="#5BD0E2",
        text_color="#FFFFFF",
        glow_intensity=0.6,
        opacity=1.0
    )
    
    assert style.background_color == "#1A2B3C"
    assert style.glow_intensity == 0.6
    
    # Test defaults (all fields optional)
    default_style = NodeStyle()
    assert default_style.glow_intensity == 0.0
    assert default_style.opacity == 1.0


def test_node_style_validation():
    """Test NodeStyle field validation"""
    # Glow intensity out of range
    with pytest.raises(ValidationError):
        NodeStyle(glow_intensity=1.5)
    
    # Opacity out of range
    with pytest.raises(ValidationError):
        NodeStyle(opacity=-0.1)


def test_edge_style_model():
    """Test EdgeStyle model"""
    style = EdgeStyle(
        stroke_color="#5BD0E2",
        stroke_width=2.5,
        stroke_dasharray="5 5",
        animated=True,
        animation_speed=1.5
    )
    
    assert style.animated is True
    assert style.animation_speed == 1.5
    
    # Test defaults
    default_style = EdgeStyle()
    assert default_style.stroke_color == "#5BD0E2"
    assert default_style.animated is False


def test_viewport_state():
    """Test ViewportState model"""
    viewport = ViewportState(x=100, y=200, zoom=1.5)
    
    assert viewport.x == 100
    assert viewport.zoom == 1.5
    
    # Test defaults
    default_viewport = ViewportState()
    assert default_viewport.x == 0.0
    assert default_viewport.zoom == 1.0
    
    # Test zoom validation
    with pytest.raises(ValidationError):
        ViewportState(zoom=10.0)  # Max is 5.0


# ============================================================================
# Test GraphNode
# ============================================================================

def test_graph_node_creation():
    """Test creating a GraphNode"""
    node = GraphNode(
        node_id="actor_1738000000_abc123",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=200),
        label="พระโมคคัลลานะ",
        data={"actor_id": "12345", "status": "active"}
    )
    
    assert node.node_id == "actor_1738000000_abc123"
    assert node.node_type == NodeType.ACTOR
    assert node.label == "พระโมคคัลลานะ"
    assert node.data["actor_id"] == "12345"
    assert isinstance(node.created_at, datetime)


def test_graph_node_with_style():
    """Test GraphNode with custom style"""
    style = NodeStyle(
        background_color="#1A2B3C",
        glow_intensity=0.8
    )
    
    node = GraphNode(
        node_id="scenario_1738000000_xyz789",
        node_type=NodeType.SCENARIO,
        position=Position(x=400, y=100),
        label="ตลาดแห่งความอยาก",
        style=style
    )
    
    assert node.style.glow_intensity == 0.8
    assert node.style.background_color == "#1A2B3C"


def test_graph_node_validation():
    """Test GraphNode validation"""
    # Invalid node_id (too short)
    with pytest.raises(ValidationError):
        GraphNode(
            node_id="abc",
            node_type=NodeType.ACTOR,
            position=Position(x=0, y=0),
            label="Test"
        )
    
    # Label too long
    with pytest.raises(ValidationError):
        GraphNode(
            node_id="actor_1738000000_abc123",
            node_type=NodeType.ACTOR,
            position=Position(x=0, y=0),
            label="a" * 101  # Max is 100
        )


# ============================================================================
# Test GraphEdge
# ============================================================================

def test_graph_edge_creation():
    """Test creating a GraphEdge"""
    edge = GraphEdge(
        edge_id="energy_1738000000_xyz789",
        edge_type=EdgeType.ENERGY_LINE,
        source_node_id="actor_1738000000_abc123",
        target_node_id="scenario_1738000000_def456",
        label="พบเจอ"
    )
    
    assert edge.edge_id == "energy_1738000000_xyz789"
    assert edge.edge_type == EdgeType.ENERGY_LINE
    assert edge.source_node_id == "actor_1738000000_abc123"
    assert edge.label == "พบเจอ"


def test_graph_edge_with_handles():
    """Test GraphEdge with connection handles"""
    edge = GraphEdge(
        edge_id="choice_1738000000_aaa111",
        edge_type=EdgeType.CHOICE_LINE,
        source_node_id="scenario_1",
        target_node_id="state_1",
        source_handle="bottom",
        target_handle="top"
    )
    
    assert edge.source_handle == "bottom"
    assert edge.target_handle == "top"


def test_graph_edge_with_style():
    """Test GraphEdge with animated style"""
    style = EdgeStyle(
        stroke_color="#F6B766",
        stroke_width=3.0,
        animated=True,
        animation_speed=2.0
    )
    
    edge = GraphEdge(
        edge_id="karma_1738000000_bbb222",
        edge_type=EdgeType.KARMA_LINE,
        source_node_id="choice_1",
        target_node_id="consequence_1",
        style=style
    )
    
    assert edge.style.animated is True
    assert edge.style.stroke_color == "#F6B766"


# ============================================================================
# Test ScenarioGraph
# ============================================================================

def test_scenario_graph_creation():
    """Test creating an empty ScenarioGraph"""
    graph = ScenarioGraph(
        graph_id="graph_20250127_ABC123",
        title="Test Graph",
        description="A test graph"
    )
    
    assert graph.graph_id == "graph_20250127_ABC123"
    assert graph.title == "Test Graph"
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert graph.node_count == 0
    assert graph.edge_count == 0


def test_scenario_graph_add_node():
    """Test adding nodes to graph"""
    graph = ScenarioGraph(
        graph_id="graph_test_001",
        title="Node Test"
    )
    
    node1 = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    
    graph.add_node(node1)
    
    assert graph.node_count == 1
    assert len(graph.nodes) == 1
    assert graph.get_node("actor_1") == node1
    
    # Add another node
    node2 = GraphNode(
        node_id="scenario_1",
        node_type=NodeType.SCENARIO,
        position=Position(x=400, y=100),
        label="Scenario 1"
    )
    
    graph.add_node(node2)
    assert graph.node_count == 2


def test_scenario_graph_add_duplicate_node():
    """Test that duplicate node IDs are rejected"""
    graph = ScenarioGraph(
        graph_id="graph_test_002",
        title="Duplicate Test"
    )
    
    node1 = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    
    graph.add_node(node1)
    
    # Try to add node with same ID
    node2 = GraphNode(
        node_id="actor_1",  # Same ID
        node_type=NodeType.ACTOR,
        position=Position(x=200, y=200),
        label="Actor 2"
    )
    
    with pytest.raises(ValueError, match="already exists"):
        graph.add_node(node2)


def test_scenario_graph_update_node():
    """Test updating node properties"""
    graph = ScenarioGraph(
        graph_id="graph_test_003",
        title="Update Test"
    )
    
    node = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Original Label"
    )
    
    graph.add_node(node)
    
    # Update label
    success = graph.update_node("actor_1", {"label": "Updated Label"})
    
    assert success is True
    updated_node = graph.get_node("actor_1")
    assert updated_node.label == "Updated Label"
    
    # Try to update non-existent node
    success = graph.update_node("nonexistent", {"label": "Test"})
    assert success is False


def test_scenario_graph_delete_node():
    """Test deleting nodes and connected edges"""
    graph = ScenarioGraph(
        graph_id="graph_test_004",
        title="Delete Test"
    )
    
    # Add two nodes
    node1 = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    node2 = GraphNode(
        node_id="scenario_1",
        node_type=NodeType.SCENARIO,
        position=Position(x=400, y=100),
        label="Scenario 1"
    )
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    # Add edge between them
    edge = GraphEdge(
        edge_id="edge_1",
        edge_type=EdgeType.ENERGY_LINE,
        source_node_id="actor_1",
        target_node_id="scenario_1"
    )
    
    graph.add_edge(edge)
    
    assert graph.node_count == 2
    assert graph.edge_count == 1
    
    # Delete node1 - should also delete connected edge
    success = graph.delete_node("actor_1")
    
    assert success is True
    assert graph.node_count == 1
    assert graph.edge_count == 0  # Edge removed
    assert graph.get_node("actor_1") is None


def test_scenario_graph_add_edge():
    """Test adding edges to graph"""
    graph = ScenarioGraph(
        graph_id="graph_test_005",
        title="Edge Test"
    )
    
    # Add two nodes first
    node1 = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    node2 = GraphNode(
        node_id="scenario_1",
        node_type=NodeType.SCENARIO,
        position=Position(x=400, y=100),
        label="Scenario 1"
    )
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    # Add edge
    edge = GraphEdge(
        edge_id="edge_1",
        edge_type=EdgeType.ENERGY_LINE,
        source_node_id="actor_1",
        target_node_id="scenario_1"
    )
    
    graph.add_edge(edge)
    
    assert graph.edge_count == 1
    assert graph.get_edge("edge_1") == edge


def test_scenario_graph_add_edge_invalid_nodes():
    """Test that edges require valid source/target nodes"""
    graph = ScenarioGraph(
        graph_id="graph_test_006",
        title="Invalid Edge Test"
    )
    
    # Try to add edge without nodes
    edge = GraphEdge(
        edge_id="edge_1",
        edge_type=EdgeType.ENERGY_LINE,
        source_node_id="nonexistent_1",
        target_node_id="nonexistent_2"
    )
    
    with pytest.raises(ValueError, match="Source node.*not found"):
        graph.add_edge(edge)


def test_scenario_graph_delete_edge():
    """Test deleting edges"""
    graph = ScenarioGraph(
        graph_id="graph_test_007",
        title="Delete Edge Test"
    )
    
    # Setup nodes and edge
    node1 = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    node2 = GraphNode(
        node_id="scenario_1",
        node_type=NodeType.SCENARIO,
        position=Position(x=400, y=100),
        label="Scenario 1"
    )
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    edge = GraphEdge(
        edge_id="edge_1",
        edge_type=EdgeType.ENERGY_LINE,
        source_node_id="actor_1",
        target_node_id="scenario_1"
    )
    
    graph.add_edge(edge)
    assert graph.edge_count == 1
    
    # Delete edge
    success = graph.delete_edge("edge_1")
    
    assert success is True
    assert graph.edge_count == 0
    assert graph.get_edge("edge_1") is None


def test_scenario_graph_validate():
    """Test graph validation"""
    graph = ScenarioGraph(
        graph_id="graph_test_008",
        title="Validation Test"
    )
    
    # Empty graph should fail validation
    errors = graph.validate_graph()
    assert len(errors) > 0
    assert "must have at least one node" in errors[0]
    assert graph.is_validated is False
    
    # Add a node
    node1 = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    graph.add_node(node1)
    
    # Single node should pass
    errors = graph.validate_graph()
    assert len(errors) == 0
    assert graph.is_validated is True


def test_scenario_graph_validate_start_node():
    """Test validation of start_node_id"""
    graph = ScenarioGraph(
        graph_id="graph_test_009",
        title="Start Node Test"
    )
    
    node = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    graph.add_node(node)
    
    # Set invalid start node
    graph.start_node_id = "nonexistent"
    
    errors = graph.validate_graph()
    assert len(errors) > 0
    assert any("Start node" in err for err in errors)
    
    # Set valid start node
    graph.start_node_id = "actor_1"
    errors = graph.validate_graph()
    assert len(errors) == 0


def test_scenario_graph_calculate_complexity():
    """Test complexity score calculation"""
    graph = ScenarioGraph(
        graph_id="graph_test_010",
        title="Complexity Test"
    )
    
    # Empty graph - 0 complexity
    score = graph.calculate_complexity()
    assert score == 0.0
    
    # Add nodes and edges
    for i in range(5):
        node = GraphNode(
            node_id=f"node_{i}",
            node_type=NodeType.SCENARIO,
            position=Position(x=i*100, y=100),
            label=f"Node {i}"
        )
        graph.add_node(node)
    
    # Add some edges
    for i in range(4):
        edge = GraphEdge(
            edge_id=f"edge_{i}",
            edge_type=EdgeType.ENERGY_LINE,
            source_node_id=f"node_{i}",
            target_node_id=f"node_{i+1}"
        )
        graph.add_edge(edge)
    
    score = graph.calculate_complexity()
    assert score > 0.0
    assert score <= 100.0
    assert graph.complexity_score == score


def test_scenario_graph_with_metadata():
    """Test graph with full metadata"""
    graph = ScenarioGraph(
        graph_id="graph_test_011",
        title="Marketplace Scenario",
        description="Test marketplace with temptations",
        author_id="user_123",
        category="temptation",
        tags=["lobha", "beginner"],
        difficulty_level=6.5
    )
    
    assert graph.category == "temptation"
    assert "lobha" in graph.tags
    assert graph.difficulty_level == 6.5
    assert graph.is_published is False


def test_scenario_graph_publish():
    """Test graph publishing workflow"""
    graph = ScenarioGraph(
        graph_id="graph_test_012",
        title="Publish Test"
    )
    
    # Add minimal valid content
    node = GraphNode(
        node_id="actor_1",
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=100),
        label="Actor 1"
    )
    graph.add_node(node)
    
    # Validate
    errors = graph.validate_graph()
    assert len(errors) == 0
    assert graph.is_validated is True
    
    # Publish
    graph.is_published = True
    graph.published_at = datetime.utcnow()
    
    assert graph.is_published is True
    assert graph.published_at is not None


# ============================================================================
# Integration Test: Build Complete Graph
# ============================================================================

def test_build_complete_graph():
    """Integration test: Build a complete scenario graph"""
    graph = ScenarioGraph(
        graph_id=generate_graph_id(),
        title="ตลาดแห่งความอยาก",
        description="สถานการณ์ทดลองความอยากในตลาด",
        category="temptation",
        difficulty_level=6.5
    )
    
    # Add Actor node
    actor_node = GraphNode(
        node_id=generate_node_id(NodeType.ACTOR),
        node_type=NodeType.ACTOR,
        position=Position(x=100, y=200),
        label="พระโมคคัลลานะ",
        data={"actor_id": "12345", "status": "active"}
    )
    graph.add_node(actor_node)
    
    # Add Scenario node
    scenario_node = GraphNode(
        node_id=generate_node_id(NodeType.SCENARIO),
        node_type=NodeType.SCENARIO,
        position=Position(x=400, y=200),
        label="เห็นของน่าทาน",
        data={"sensory_input": "visual", "vedana": "pleasant"}
    )
    graph.add_node(scenario_node)
    
    # Add State nodes (3 choices)
    state_kusala = GraphNode(
        node_id=generate_node_id(NodeType.STATE),
        node_type=NodeType.STATE,
        position=Position(x=700, y=100),
        label="สังเกตและเดินผ่าน",
        data={"choice_type": "kusala", "difficulty": 7}
    )
    graph.add_node(state_kusala)
    
    state_akusala = GraphNode(
        node_id=generate_node_id(NodeType.STATE),
        node_type=NodeType.STATE,
        position=Position(x=700, y=200),
        label="ซื้อกินทันที",
        data={"choice_type": "akusala", "difficulty": 3}
    )
    graph.add_node(state_akusala)
    
    state_neutral = GraphNode(
        node_id=generate_node_id(NodeType.STATE),
        node_type=NodeType.STATE,
        position=Position(x=700, y=300),
        label="เดินผ่านไปเฉยๆ",
        data={"choice_type": "neutral", "difficulty": 5}
    )
    graph.add_node(state_neutral)
    
    # Connect Actor -> Scenario
    edge1 = GraphEdge(
        edge_id=generate_edge_id(EdgeType.ENERGY_LINE),
        edge_type=EdgeType.ENERGY_LINE,
        source_node_id=actor_node.node_id,
        target_node_id=scenario_node.node_id,
        label="พบเจอ",
        style=EdgeStyle(animated=True)
    )
    graph.add_edge(edge1)
    
    # Connect Scenario -> States (3 choice paths)
    edge2 = GraphEdge(
        edge_id=generate_edge_id(EdgeType.CHOICE_LINE),
        edge_type=EdgeType.CHOICE_LINE,
        source_node_id=scenario_node.node_id,
        target_node_id=state_kusala.node_id,
        label="กุศล"
    )
    graph.add_edge(edge2)
    
    edge3 = GraphEdge(
        edge_id=generate_edge_id(EdgeType.CHOICE_LINE),
        edge_type=EdgeType.CHOICE_LINE,
        source_node_id=scenario_node.node_id,
        target_node_id=state_akusala.node_id,
        label="อกุศล"
    )
    graph.add_edge(edge3)
    
    edge4 = GraphEdge(
        edge_id=generate_edge_id(EdgeType.CHOICE_LINE),
        edge_type=EdgeType.CHOICE_LINE,
        source_node_id=scenario_node.node_id,
        target_node_id=state_neutral.node_id,
        label="เฉยๆ"
    )
    graph.add_edge(edge4)
    
    # Set start node
    graph.start_node_id = actor_node.node_id
    
    # Validate
    errors = graph.validate_graph()
    assert len(errors) == 0
    assert graph.is_validated is True
    
    # Check structure
    assert graph.node_count == 5
    assert graph.edge_count == 4
    
    # Calculate complexity
    complexity = graph.calculate_complexity()
    assert complexity > 0
    
    print(f"✅ Complete graph created: {graph.node_count} nodes, {graph.edge_count} edges, complexity={complexity:.2f}")
    
    return graph


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
