"""
Integration tests for Simulation Phase 2 routers
=================================================
Test coverage:
- Scenarios CRUD + batch operations
- Events CRUD + annotations
- Chains CRUD + health analytics + branching
- Clusters CRUD + analytics
- Teaching CRUD + AI Q&A
- QA CRUD + regression testing
"""

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_scenarios_crud():
    """Test Scenarios CRUD operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # CREATE scenario
        scenario_data = {
            "title": "Test Scenario",
            "description": "Testing simulation",
            "tags": ["test", "karma"],
            "status": "draft"
        }
        
        response = await client.post("/api/v1/scenarios/", json=scenario_data, headers=headers)
        assert response.status_code == 201
        scenario = response.json()
        assert scenario["title"] == "Test Scenario"
        scenario_id = scenario["scenario_id"]
        
        # LIST scenarios
        response = await client.get("/api/v1/scenarios/", headers=headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) >= 1
        
        # GET scenario
        response = await client.get(f"/api/v1/scenarios/{scenario_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["scenario_id"] == scenario_id
        
        # UPDATE scenario
        update_data = {"status": "active"}
        response = await client.patch(f"/api/v1/scenarios/{scenario_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "active"
        
        # DELETE scenario
        response = await client.delete(f"/api/v1/scenarios/{scenario_id}", headers=headers)
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_simulation_events():
    """Test Simulation Events operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # Create scenario first
        scenario_data = {
            "title": "Event Test Scenario",
            "description": "For testing events"
        }
        response = await client.post("/api/v1/scenarios/", json=scenario_data, headers=headers)
        scenario_id = response.json()["scenario_id"]
        
        # CREATE event
        event_data = {
            "scenario_id": scenario_id,
            "type": "action",
            "title": "Test Event",
            "intensity": 0.8
        }
        
        response = await client.post("/api/v1/simulation-events/", json=event_data, headers=headers)
        assert response.status_code == 201
        event = response.json()
        assert event["title"] == "Test Event"
        event_id = event["event_id"]
        
        # ANNOTATE event
        annotation_data = {
            "annotation": "This is important",
            "teaching_note": "Teaching point here"
        }
        response = await client.post(f"/api/v1/simulation-events/{event_id}/annotate", json=annotation_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["annotation"] == "This is important"


@pytest.mark.asyncio
async def test_simulation_chains():
    """Test Simulation Chains operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # CREATE chain
        chain_data = {
            "scenario_id": "SC-test",
            "event_ids": ["EV-001", "EV-002"],
            "status": "active"
        }
        
        response = await client.post("/api/v1/simulation-chains/", json=chain_data, headers=headers)
        assert response.status_code == 201
        chain = response.json()
        chain_id = chain["chain_id"]
        
        # GET chain health
        response = await client.get(f"/api/v1/simulation-chains/{chain_id}/health", headers=headers)
        assert response.status_code == 200
        health = response.json()
        assert "chain_health" in health
        assert "karma_total" in health


@pytest.mark.asyncio
async def test_simulation_clusters():
    """Test Simulation Clusters operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # CREATE cluster
        cluster_data = {
            "title": "Test Cluster",
            "description": "Group of test scenarios",
            "scenario_ids": ["SC-001", "SC-002"]
        }
        
        response = await client.post("/api/v1/simulation-clusters/", json=cluster_data, headers=headers)
        if response.status_code != 201:
            print(f"\n❌ Cluster creation failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 201
        cluster = response.json()
        assert cluster["title"] == "Test Cluster"
        cluster_id = cluster["cluster_id"]
        
        # GET cluster analytics
        response = await client.get(f"/api/v1/simulation-clusters/{cluster_id}/analytics", headers=headers)
        assert response.status_code == 200
        analytics = response.json()
        assert "aggregate_karma" in analytics


@pytest.mark.asyncio
async def test_teaching_router():
    """Test Teaching router operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # CREATE teaching step
        step_data = {
            "title": "Test Teaching Step",
            "description": "Learning about karma",
            "step_number": 1
        }
        
        response = await client.post("/api/v1/teaching/steps", json=step_data, headers=headers)
        if response.status_code != 201:
            print(f"\n❌ Teaching step creation failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 201
        step = response.json()
        assert step["title"] == "Test Teaching Step"
        step_id = step["step_id"]
        
        # GENERATE AI Q&A
        response = await client.get(f"/api/v1/teaching/steps/{step_id}/ai-qa", headers=headers)
        if response.status_code != 200:
            print(f"\n❌ AI Q&A generation failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 200
        qa = response.json()
        assert "questions" in qa  # ✅ Changed from ai_question
        assert "dhamma_insights" in qa  # ✅ Changed from quiz_options


@pytest.mark.asyncio
async def test_qa_router():
    """Test QA router operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # CREATE test case
        test_data = {
            "title": "Test QA Case",
            "scenario_id": "SC-test",
            "expected_outcome": {
                "karma_score": 0.75
            },
            "conditions": {}
        }
        
        response = await client.post("/api/v1/qa/test-cases", json=test_data, headers=headers)
        if response.status_code != 201:
            print(f"\n❌ QA test case creation failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 201
        test_case = response.json()
        assert test_case["title"] == "Test QA Case"
        test_case_id = test_case["test_case_id"]
        
        # RUN test
        response = await client.post(f"/api/v1/qa/test-cases/{test_case_id}/run", headers=headers)
        if response.status_code != 200:
            print(f"\n❌ QA test run failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 200
        result = response.json()
        assert "passed" in result
        
        # GET regression analysis
        response = await client.get(f"/api/v1/qa/test-cases/{test_case_id}/regression", headers=headers)
        if response.status_code != 200:
            print(f"\n❌ Regression analysis failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 200
        regression = response.json()
        assert "pass_rate" in regression


@pytest.mark.asyncio
async def test_batch_operations():
    """Test batch operations"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-KEY": "YOUR_SECRET_API_KEY"}
        
        # Create multiple scenarios
        scenario_ids = []
        for i in range(3):
            scenario_data = {
                "title": f"Batch Test Scenario {i+1}",
                "description": f"Scenario for batch testing {i+1}"
            }
            response = await client.post("/api/v1/scenarios/", json=scenario_data, headers=headers)
            scenario_ids.append(response.json()["scenario_id"])
        
        # BATCH RUN
        batch_data = {
            "scenario_ids": scenario_ids,
            "compare_outcomes": True,
            "generate_analytics": True
        }
        
        response = await client.post("/api/v1/scenarios/batch/run", json=batch_data, headers=headers)
        if response.status_code != 200:
            print(f"\n❌ Batch run failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        assert response.status_code == 200
        batch_result = response.json()
        assert len(batch_result["results"]) == 3  # ✅ Changed from "scenarios" to "results"
        assert "comparison_matrix" in batch_result
