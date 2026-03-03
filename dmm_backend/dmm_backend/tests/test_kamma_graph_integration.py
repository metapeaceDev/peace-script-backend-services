"""
Integration Tests for Kamma-Vipāka Graph API

Tests all 5 endpoints end-to-end with mock data:
1. GET /api/kamma-graph/{model_id} - Get full graph
2. GET /api/kamma-graph/{model_id}/node/{node_id} - Node detail
3. POST /api/kamma-graph/{model_id}/traceback - Causality chains
4. POST /api/kamma-graph/{model_id}/search - Search nodes
5. GET /api/kamma-graph/health - Health check

Author: Digital Mind Model Team
Date: November 6, 2024
Version: 1.0
"""

import pytest
from fastapi.testclient import TestClient

# Import main app and dependencies
from main import app
from documents import DigitalMindModel
from helpers.kamma_mock_data import generate_mock_kamma_storage, get_sample_character_data


# Test client
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def test_character_with_kamma():
    """
    Create a test character with populated kamma storage.
    This character will be used across all endpoint tests.
    """
    # Generate mock data
    char_data = get_sample_character_data()
    
    # Create DigitalMindModel document with required fields
    character = DigitalMindModel(
        model_id=char_data["model_id"],
        name=char_data["name"],
        status_label="Testing",
        overall_level=1,
        image_url="https://example.com/test.jpg",
        core_state={},
        conscious_profile={},
        kamma_profile=char_data["kamma_storage"]  # Use kamma_profile instead
    )
    
    # Save to database
    await character.insert()
    
    yield character
    
    # Cleanup after test
    await character.delete()


@pytest.fixture
def sample_kamma_storage():
    """Generate a sample KammaStorage for direct testing."""
    return generate_mock_kamma_storage(
        character_id="test_storage_001",
        num_records=15,
        num_chains=2
    )


# ============================================================================
# TEST 1: Health Check Endpoint
# ============================================================================

def test_health_check():
    """Test GET /api/kamma-graph/health endpoint."""
    response = client.get("/api/kamma-graph/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "kamma-graph-api"
    assert data["version"] == "1.0"
    assert "timestamp" in data
    
    print("✅ Health check endpoint working")


# ============================================================================
# TEST 2: Get Full Graph Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_get_full_graph(test_character_with_kamma):
    """Test GET /api/kamma-graph/{model_id} endpoint."""
    model_id = test_character_with_kamma.model_id
    
    # Test without filters
    response = client.get(f"/api/kamma-graph/{model_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "graph" in data
    assert "metadata" in data
    
    # Verify graph structure
    graph = data["graph"]
    assert "nodes" in graph
    assert "edges" in graph
    assert "summary" in graph
    
    # Verify nodes and edges exist
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) >= 0
    
    # Verify metadata
    metadata = data["metadata"]
    assert "total_records" in metadata
    assert "kusala_count" in metadata
    assert "akusala_count" in metadata
    
    print(f"✅ Got graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")


@pytest.mark.asyncio
async def test_get_graph_with_filters(test_character_with_kamma):
    """Test GET /api/kamma-graph/{model_id} with filters."""
    model_id = test_character_with_kamma.model_id
    
    # Test with kusala filter
    response = client.get(
        f"/api/kamma-graph/{model_id}",
        params={
            "filter_type": "kusala",
            "include_vipaka": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    graph = data["graph"]
    
    # Verify all nodes are kusala
    for node in graph["nodes"]:
        assert node["node_type"] == "kusala"
    
    print(f"✅ Filtered graph returned {len(graph['nodes'])} kusala nodes")


@pytest.mark.asyncio
async def test_get_graph_not_found():
    """Test GET /api/kamma-graph/{model_id} with non-existent character."""
    response = client.get("/api/kamma-graph/nonexistent_id_12345")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert "not found" in data["detail"].lower()
    
    print("✅ 404 error correctly returned for non-existent character")


# ============================================================================
# TEST 3: Get Node Detail Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_get_node_detail(test_character_with_kamma):
    """Test GET /api/kamma-graph/{model_id}/node/{node_id} endpoint."""
    model_id = test_character_with_kamma.model_id
    
    # First get the full graph to get a node ID
    graph_response = client.get(f"/api/kamma-graph/{model_id}")
    graph_data = graph_response.json()
    nodes = graph_data["graph"]["nodes"]
    
    assert len(nodes) > 0, "Graph must have at least one node"
    
    # Get first node's ID
    node_id = nodes[0]["id"]
    
    # Test node detail endpoint
    response = client.get(f"/api/kamma-graph/{model_id}/node/{node_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "node" in data
    assert "related_edges" in data
    assert "predecessors" in data
    assert "successors" in data
    
    # Verify node data
    node = data["node"]
    assert node["id"] == node_id
    assert "label" in node
    assert "node_type" in node
    
    print(f"✅ Got node detail for {node_id}")


@pytest.mark.asyncio
async def test_get_node_detail_not_found(test_character_with_kamma):
    """Test GET /api/kamma-graph/{model_id}/node/{node_id} with invalid node."""
    model_id = test_character_with_kamma.model_id
    
    response = client.get(f"/api/kamma-graph/{model_id}/node/invalid_node_id")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert "not found" in data["detail"].lower()
    
    print("✅ 404 error correctly returned for non-existent node")


# ============================================================================
# TEST 4: Traceback (Causality Chains) Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_traceback_forward(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/traceback with forward direction."""
    model_id = test_character_with_kamma.model_id
    
    # Get a starting node
    graph_response = client.get(f"/api/kamma-graph/{model_id}")
    nodes = graph_response.json()["graph"]["nodes"]
    start_node_id = nodes[0]["id"]
    
    # Test traceback endpoint
    response = client.post(
        f"/api/kamma-graph/{model_id}/traceback",
        json={
            "start_node_id": start_node_id,
            "max_depth": 5,
            "direction": "forward"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["start_node_id"] == start_node_id
    assert "chains" in data
    assert "summary" in data
    
    # Verify chains structure
    chains = data["chains"]
    assert isinstance(chains, list)
    
    if len(chains) > 0:
        chain = chains[0]
        assert "chain_id" in chain
        assert "nodes" in chain
        assert "length" in chain
        assert "total_weight" in chain
        assert "chain_type" in chain
        
        print(f"✅ Found {len(chains)} forward causality chains from {start_node_id}")
    else:
        print(f"✅ No forward chains found (expected for leaf nodes)")


@pytest.mark.asyncio
async def test_traceback_backward(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/traceback with backward direction."""
    model_id = test_character_with_kamma.model_id
    
    # Get a starting node
    graph_response = client.get(f"/api/kamma-graph/{model_id}")
    nodes = graph_response.json()["graph"]["nodes"]
    start_node_id = nodes[-1]["id"]  # Use last node (more likely to have predecessors)
    
    # Test traceback endpoint
    response = client.post(
        f"/api/kamma-graph/{model_id}/traceback",
        json={
            "start_node_id": start_node_id,
            "max_depth": 5,
            "direction": "backward"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "chains" in data
    
    print(f"✅ Backward traceback completed")


@pytest.mark.asyncio
async def test_traceback_invalid_node(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/traceback with invalid node."""
    model_id = test_character_with_kamma.model_id
    
    response = client.post(
        f"/api/kamma-graph/{model_id}/traceback",
        json={
            "start_node_id": "invalid_node_99999",
            "max_depth": 5,
            "direction": "forward"
        }
    )
    
    assert response.status_code == 404
    
    print("✅ 404 error correctly returned for invalid traceback node")


# ============================================================================
# TEST 5: Search Nodes Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_search_by_query(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/search with text query."""
    model_id = test_character_with_kamma.model_id
    
    # Search for kusala-related terms
    response = client.post(
        f"/api/kamma-graph/{model_id}/search",
        json={
            "query": "บุญ"  # Merit/Dāna
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "results" in data
    assert "total_count" in data
    assert "query_info" in data
    
    # Verify results
    results = data["results"]
    assert isinstance(results, list)
    
    if len(results) > 0:
        # Verify each result has required fields
        for node in results:
            assert "id" in node
            assert "label" in node
            assert "node_type" in node
        
        print(f"✅ Search found {len(results)} nodes matching 'บุญ'")
    else:
        print("✅ Search completed (no matches for 'บุญ')")


@pytest.mark.asyncio
async def test_search_by_type(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/search filtered by type."""
    model_id = test_character_with_kamma.model_id
    
    # Search for akusala nodes only
    response = client.post(
        f"/api/kamma-graph/{model_id}/search",
        json={
            "query": "",
            "node_type": "akusala"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    results = data["results"]
    
    # Verify all results are akusala
    for node in results:
        assert node["node_type"] == "akusala"
    
    print(f"✅ Search found {len(results)} akusala nodes")


@pytest.mark.asyncio
async def test_search_by_weight_range(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/search filtered by weight."""
    model_id = test_character_with_kamma.model_id
    
    # Search for strong kamma (weight > 0.7)
    response = client.post(
        f"/api/kamma-graph/{model_id}/search",
        json={
            "query": "",
            "min_weight": 0.7,
            "max_weight": 1.0
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    results = data["results"]
    
    # Verify all results have weight >= 0.7
    for node in results:
        assert node["weight"] >= 0.7
    
    print(f"✅ Search found {len(results)} nodes with weight >= 0.7")


@pytest.mark.asyncio
async def test_search_empty_results(test_character_with_kamma):
    """Test POST /api/kamma-graph/{model_id}/search with no matches."""
    model_id = test_character_with_kamma.model_id
    
    # Search for something that won't match
    response = client.post(
        f"/api/kamma-graph/{model_id}/search",
        json={
            "query": "xxxnonexistentxxx"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["total_count"] == 0
    assert len(data["results"]) == 0
    
    print("✅ Search correctly returned empty results")


# ============================================================================
# TEST 6: Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_model_id_format():
    """Test endpoints with invalid model ID format."""
    invalid_id = ""
    
    response = client.get(f"/api/kamma-graph/{invalid_id}")
    
    # Should return 404 or 422
    assert response.status_code in [404, 422]
    
    print("✅ Invalid model ID correctly rejected")


@pytest.mark.asyncio
async def test_malformed_request_body(test_character_with_kamma):
    """Test endpoints with malformed request bodies."""
    model_id = test_character_with_kamma.model_id
    
    # Test traceback with missing required field
    response = client.post(
        f"/api/kamma-graph/{model_id}/traceback",
        json={
            "max_depth": 5
            # Missing start_node_id
        }
    )
    
    assert response.status_code == 422  # Unprocessable Entity
    
    print("✅ Malformed request correctly rejected with 422")


# ============================================================================
# TEST 7: Performance Tests (Optional)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_large_graph_performance():
    """Test performance with larger kamma storage (optional)."""
    # Generate large storage
    large_storage = generate_mock_kamma_storage(
        character_id="perf_test_char",
        num_records=100,
        num_chains=10
    )
    
    # Create character with required fields
    character = DigitalMindModel(
        model_id="perf_test_char",
        name="Performance Test Character",
        status_label="Testing",
        overall_level=1,
        image_url="https://example.com/perf.jpg",
        core_state={},
        conscious_profile={},
        kamma_profile=large_storage.dict()
    )
    await character.insert()
    
    try:
        import time
        start = time.time()
        
        # Test get graph
        response = client.get("/api/kamma-graph/perf_test_char")
        
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5.0  # Should complete within 5 seconds
        
        print(f"✅ Large graph (100 records) loaded in {elapsed:.2f}s")
        
    finally:
        # Cleanup
        await character.delete()


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
