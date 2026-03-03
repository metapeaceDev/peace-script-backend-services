#!/bin/bash
# Simple bash script to test all simulation API endpoints

BASE_URL="http://localhost:8000"

echo "=== Interactive Simulation API Testing ==="
echo ""

# Test 1: Health
echo "Test 1: Health Check"
echo "GET $BASE_URL/api/simulation/health"
curl -s "$BASE_URL/api/simulation/health" | python3 -m json.tool
echo ""

# Test 2: List Scenarios
echo "Test 2: List Scenarios"
echo "GET $BASE_URL/api/simulation/scenarios"
curl -s "$BASE_URL/api/simulation/scenarios" | python3 -m json.tool
echo ""

# Test 3: Scenario Detail
echo "Test 3: Scenario Detail (marketplace_expensive)"
echo "GET $BASE_URL/api/simulation/scenarios/marketplace_expensive"
echo "Response:"
curl -v "$BASE_URL/api/simulation/scenarios/marketplace_expensive" 2>&1 | grep -E "(HTTP|< )" || echo "Request sent, checking response..."
curl -s "$BASE_URL/api/simulation/scenarios/marketplace_expensive" | python3 -m json.tool || echo "Failed to parse JSON response"
echo ""

# Test 4: Run Simulation (if detail works)
echo "Test 4: Run Simulation"
echo "POST $BASE_URL/api/simulation/simulate"
PAYLOAD='{"scenario_id":"marketplace_expensive","choice_index":0,"user_id":"test_user_001","reflection":"Testing"}'
echo "Payload: $PAYLOAD"
curl -s -X POST "$BASE_URL/api/simulation/simulate" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -m json.tool || echo "Failed to parse JSON response"
echo ""

# Test 5: User Progress
echo "Test 5: User Progress"
echo "GET $BASE_URL/api/simulation/progress/test_user_001"
curl -s "$BASE_URL/api/simulation/progress/test_user_001" | python3 -m json.tool || echo "Failed to parse JSON response"
echo ""

echo "=== Testing Complete ==="
