"""
Unit Tests for Kamma Graph Models

Test suite for KammaNode, KammaEdge, and KammaGraph models.

Author: PeaceScript Team
Date: 6 November 2024
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from models.kamma_graph import KammaNode, KammaEdge, KammaGraph


class TestKammaNode:
    """Test cases for KammaNode model"""
    
    def test_create_valid_node(self):
        """Test creating a valid KammaNode"""
        node = KammaNode(
            type="kamma",
            label="ช่วยเหลือคนแปลกหน้า",
            life_index=-2,
            date=datetime.now(),
            realm="มนุษย์",
            weight=0.7,
            tags=["kusala", "generosity"]
        )
        
        assert node.type == "kamma"
        assert node.label == "ช่วยเหลือคนแปลกหน้า"
        assert node.life_index == -2
        assert node.realm == "มนุษย์"
        assert node.weight == 0.7
        assert "kusala" in node.tags
        assert node.id.startswith("node_")
    
    def test_auto_generate_id(self):
        """Test that ID is auto-generated"""
        node1 = KammaNode(
            type="kamma",
            label="Event 1",
            life_index=0,
            date=datetime.now(),
            realm="มนุษย์",
            weight=0.5
        )
        
        node2 = KammaNode(
            type="kamma",
            label="Event 2",
            life_index=0,
            date=datetime.now(),
            realm="มนุษย์",
            weight=0.5
        )
        
        assert node1.id != node2.id
        assert node1.id.startswith("node_")
        assert node2.id.startswith("node_")
    
    def test_invalid_type(self):
        """Test that invalid type raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="invalid_type",  # Should be "kamma", "vipaka", or "neutral"
                label="Test",
                life_index=0,
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.5
            )
    
    def test_invalid_life_index_too_low(self):
        """Test that life_index < -12 raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="kamma",
                label="Test",
                life_index=-13,  # Too low (< -12)
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.5
            )
    
    def test_invalid_life_index_too_high(self):
        """Test that life_index > 0 raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="kamma",
                label="Test",
                life_index=1,  # Too high (> 0)
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.5
            )
    
    def test_invalid_weight_negative(self):
        """Test that negative weight raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="kamma",
                label="Test",
                life_index=0,
                date=datetime.now(),
                realm="มนุษย์",
                weight=-0.1  # Negative
            )
    
    def test_invalid_weight_too_high(self):
        """Test that weight > 1.0 raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="kamma",
                label="Test",
                life_index=0,
                date=datetime.now(),
                realm="มนุษย์",
                weight=1.5  # Too high (> 1.0)
            )
    
    def test_empty_label(self):
        """Test that empty label raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="kamma",
                label="",  # Empty
                life_index=0,
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.5
            )
    
    def test_label_too_long(self):
        """Test that label > 200 chars raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaNode(
                type="kamma",
                label="x" * 201,  # Too long
                life_index=0,
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.5
            )
    
    def test_default_tags_empty(self):
        """Test that tags default to empty list"""
        node = KammaNode(
            type="kamma",
            label="Test",
            life_index=0,
            date=datetime.now(),
            realm="มนุษย์",
            weight=0.5
        )
        
        assert node.tags == []
    
    def test_default_metadata_empty(self):
        """Test that metadata defaults to empty dict"""
        node = KammaNode(
            type="kamma",
            label="Test",
            life_index=0,
            date=datetime.now(),
            realm="มนุษย์",
            weight=0.5
        )
        
        assert node.metadata == {}
    
    def test_metadata_stores_custom_data(self):
        """Test that metadata can store custom data"""
        node = KammaNode(
            type="kamma",
            label="Test",
            life_index=0,
            date=datetime.now(),
            realm="มนุษย์",
            weight=0.5,
            metadata={
                "emotion": "guilt",
                "context": "war",
                "severity": "high"
            }
        )
        
        assert node.metadata["emotion"] == "guilt"
        assert node.metadata["context"] == "war"
        assert node.metadata["severity"] == "high"


class TestKammaEdge:
    """Test cases for KammaEdge model"""
    
    def test_create_valid_edge(self):
        """Test creating a valid KammaEdge"""
        edge = KammaEdge(
            from_node="node_abc123",
            to_node="node_xyz789",
            kind="cause",
            strength=0.9
        )
        
        assert edge.from_node == "node_abc123"
        assert edge.to_node == "node_xyz789"
        assert edge.kind == "cause"
        assert edge.strength == 0.9
        assert edge.id.startswith("edge_")
    
    def test_auto_generate_id(self):
        """Test that ID is auto-generated"""
        edge1 = KammaEdge(
            from_node="node_1",
            to_node="node_2",
            kind="cause",
            strength=0.5
        )
        
        edge2 = KammaEdge(
            from_node="node_3",
            to_node="node_4",
            kind="result",
            strength=0.5
        )
        
        assert edge1.id != edge2.id
        assert edge1.id.startswith("edge_")
        assert edge2.id.startswith("edge_")
    
    def test_all_edge_kinds(self):
        """Test all valid edge kinds"""
        kinds = ["cause", "result", "support", "obstruct"]
        
        for kind in kinds:
            edge = KammaEdge(
                from_node="node_1",
                to_node="node_2",
                kind=kind,
                strength=0.5
            )
            assert edge.kind == kind
    
    def test_invalid_kind(self):
        """Test that invalid kind raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaEdge(
                from_node="node_1",
                to_node="node_2",
                kind="invalid_kind",
                strength=0.5
            )
    
    def test_invalid_strength_negative(self):
        """Test that negative strength raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaEdge(
                from_node="node_1",
                to_node="node_2",
                kind="cause",
                strength=-0.1
            )
    
    def test_invalid_strength_too_high(self):
        """Test that strength > 1.0 raises ValidationError"""
        with pytest.raises(ValidationError):
            KammaEdge(
                from_node="node_1",
                to_node="node_2",
                kind="cause",
                strength=1.5
            )
    
    def test_default_metadata_empty(self):
        """Test that metadata defaults to empty dict"""
        edge = KammaEdge(
            from_node="node_1",
            to_node="node_2",
            kind="cause",
            strength=0.5
        )
        
        assert edge.metadata == {}


class TestKammaGraph:
    """Test cases for KammaGraph model"""
    
    @pytest.fixture
    def sample_nodes(self):
        """Create sample nodes for testing"""
        return [
            KammaNode(
                id="node_1",
                type="kamma",
                label="Event 1",
                life_index=-2,
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.7,
                tags=["kusala", "generosity"]
            ),
            KammaNode(
                id="node_2",
                type="vipaka",
                label="Event 2",
                life_index=-1,
                date=datetime.now(),
                realm="มนุษย์",
                weight=0.6,
                tags=["vipaka"]
            ),
            KammaNode(
                id="node_3",
                type="kamma",
                label="Event 3",
                life_index=0,
                date=datetime.now(),
                realm="เทวดา",
                weight=0.8,
                tags=["akusala", "anger"]
            )
        ]
    
    @pytest.fixture
    def sample_edges(self):
        """Create sample edges for testing"""
        return [
            KammaEdge(
                id="edge_1",
                from_node="node_1",
                to_node="node_2",
                kind="cause",
                strength=0.9
            ),
            KammaEdge(
                id="edge_2",
                from_node="node_2",
                to_node="node_3",
                kind="support",
                strength=0.5
            )
        ]
    
    def test_create_empty_graph(self):
        """Test creating an empty graph"""
        graph = KammaGraph(model_id="test_model")
        
        assert graph.model_id == "test_model"
        assert graph.nodes == []
        assert graph.edges == []
        assert graph.summary == {}
        assert isinstance(graph.created_at, datetime)
        assert isinstance(graph.updated_at, datetime)
    
    def test_create_graph_with_data(self, sample_nodes, sample_edges):
        """Test creating a graph with nodes and edges"""
        graph = KammaGraph(
            model_id="test_model",
            nodes=sample_nodes,
            edges=sample_edges
        )
        
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert graph.model_id == "test_model"
    
    def test_get_node_by_id(self, sample_nodes):
        """Test getting node by ID"""
        graph = KammaGraph(
            model_id="test_model",
            nodes=sample_nodes
        )
        
        node = graph.get_node_by_id("node_1")
        assert node is not None
        assert node.id == "node_1"
        assert node.label == "Event 1"
        
        # Test non-existent node
        node = graph.get_node_by_id("node_999")
        assert node is None
    
    def test_get_edges_for_node(self, sample_nodes, sample_edges):
        """Test getting all edges connected to a node"""
        graph = KammaGraph(
            model_id="test_model",
            nodes=sample_nodes,
            edges=sample_edges
        )
        
        # Node 2 has 2 edges (1 incoming, 1 outgoing)
        edges = graph.get_edges_for_node("node_2")
        assert len(edges) == 2
        
        # Node 1 has 1 edge (outgoing)
        edges = graph.get_edges_for_node("node_1")
        assert len(edges) == 1
        
        # Node 3 has 1 edge (incoming)
        edges = graph.get_edges_for_node("node_3")
        assert len(edges) == 1
    
    def test_get_predecessors(self, sample_nodes, sample_edges):
        """Test getting predecessor nodes"""
        graph = KammaGraph(
            model_id="test_model",
            nodes=sample_nodes,
            edges=sample_edges
        )
        
        # Node 2's predecessor is node 1
        preds = graph.get_predecessors("node_2")
        assert preds == ["node_1"]
        
        # Node 1 has no predecessors
        preds = graph.get_predecessors("node_1")
        assert preds == []
        
        # Node 3's predecessor is node 2
        preds = graph.get_predecessors("node_3")
        assert preds == ["node_2"]
    
    def test_get_successors(self, sample_nodes, sample_edges):
        """Test getting successor nodes"""
        graph = KammaGraph(
            model_id="test_model",
            nodes=sample_nodes,
            edges=sample_edges
        )
        
        # Node 1's successor is node 2
        succs = graph.get_successors("node_1")
        assert succs == ["node_2"]
        
        # Node 2's successor is node 3
        succs = graph.get_successors("node_2")
        assert succs == ["node_3"]
        
        # Node 3 has no successors
        succs = graph.get_successors("node_3")
        assert succs == []
    
    def test_update_summary(self, sample_nodes, sample_edges):
        """Test updating graph summary"""
        graph = KammaGraph(
            model_id="test_model",
            nodes=sample_nodes,
            edges=sample_edges
        )
        
        graph.update_summary()
        
        assert graph.summary["total_nodes"] == 3
        assert graph.summary["total_edges"] == 2
        assert graph.summary["kusala_count"] == 1  # node_1
        assert graph.summary["akusala_count"] == 1  # node_3
        assert graph.summary["karma_balance"] == 0  # 1 kusala - 1 akusala
        assert graph.summary["life_range"] == [-2, 0]
        assert set(graph.summary["realms"]) == {"มนุษย์", "เทวดา"}
        
        # Check heaviest kamma
        assert graph.summary["heaviest_kamma"]["node_id"] == "node_3"
        assert graph.summary["heaviest_kamma"]["weight"] == 0.8
        
        # Check most connected node
        assert graph.summary["most_connected_node"]["node_id"] == "node_2"
        assert graph.summary["most_connected_node"]["connections"] == 2
    
    def test_update_summary_empty_graph(self):
        """Test updating summary on empty graph"""
        graph = KammaGraph(model_id="test_model")
        graph.update_summary()
        
        assert graph.summary["total_nodes"] == 0
        assert graph.summary["total_edges"] == 0
        assert graph.summary["kusala_count"] == 0
        assert graph.summary["akusala_count"] == 0
        assert graph.summary["karma_balance"] == 0
        assert "heaviest_kamma" not in graph.summary
        assert "most_connected_node" not in graph.summary


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
