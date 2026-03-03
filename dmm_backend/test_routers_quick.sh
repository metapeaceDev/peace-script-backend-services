#!/bin/bash
# Quick Router Testing Script
# Tests all 4 narrative routers (Scene, Shot, Visual, Character)
# Records which endpoints work/fail without deep debugging

BASE_URL="http://localhost:8000/api/narrative"
RESULTS_FILE="/tmp/router_test_results.txt"

echo "🧪 Peace Script Router Testing" > $RESULTS_FILE
echo "================================" >> $RESULTS_FILE
echo "Started: $(date)" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

# Test helper function
test_endpoint() {
    local router=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    if [ "$method" == "POST" ] || [ "$method" == "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL/$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL/$endpoint" 2>/dev/null)
    fi
    
    status=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status" == "$expected_status" ]; then
        echo "  ✅ $method $endpoint - HTTP $status"
        echo "  ✅ $method $endpoint - HTTP $status" >> $RESULTS_FILE
        return 0
    else
        echo "  ❌ $method $endpoint - HTTP $status (expected $expected_status)"
        echo "  ❌ $method $endpoint - HTTP $status (expected $expected_status)" >> $RESULTS_FILE
        return 1
    fi
}

# =============================================================================
# Scene Router Tests
# =============================================================================
echo ""
echo "📁 SCENE ROUTER"
echo "" >> $RESULTS_FILE
echo "📁 SCENE ROUTER" >> $RESULTS_FILE

# Create project first (needed for scene)
PROJECT_DATA='{"project_id":"test_proj_001","script_name":"Test Script","genre":"drama","studio":"Test","writer":"AI","language":"th","status":"draft"}'
curl -s -X POST "$BASE_URL/projects" -H "Content-Type: application/json" -d "$PROJECT_DATA" > /dev/null 2>&1

# Scene CREATE
SCENE_DATA='{"project_id":"test_proj_001","scene_number":1,"scene_title":"Opening Scene","location":"Exterior - Day","time_of_day":"morning"}'
response=$(curl -s -X POST "$BASE_URL/scenes/" -H "Content-Type: application/json" -d "$SCENE_DATA" 2>/dev/null)
SCENE_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$SCENE_ID" ]; then
    echo "  ✅ POST /scenes/ - Created $SCENE_ID"
    echo "  ✅ POST /scenes/ - Created $SCENE_ID" >> $RESULTS_FILE
    
    test_endpoint "scene" "GET" "scenes/?project_id=test_proj_001" "" "200"
    test_endpoint "scene" "GET" "scenes/$SCENE_ID" "" "200"
    test_endpoint "scene" "PUT" "scenes/$SCENE_ID" '{"scene_title":"Updated Scene"}' "200"
    test_endpoint "scene" "GET" "scenes/health" "" "200"
    test_endpoint "scene" "DELETE" "scenes/$SCENE_ID" "" "204"
else
    echo "  ❌ POST /scenes/ - Failed to create"
    echo "  ❌ POST /scenes/ - Failed to create" >> $RESULTS_FILE
fi

# =============================================================================
# Shot Router Tests
# =============================================================================
echo ""
echo "🎬 SHOT ROUTER"
echo "" >> $RESULTS_FILE
echo "🎬 SHOT ROUTER" >> $RESULTS_FILE

# Create scene for shot
SCENE_DATA='{"project_id":"test_proj_001","scene_number":2,"scene_title":"Shot Test Scene","location":"Interior","time_of_day":"day"}'
response=$(curl -s -X POST "$BASE_URL/scenes/" -H "Content-Type: application/json" -d "$SCENE_DATA" 2>/dev/null)
TEST_SCENE_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$TEST_SCENE_ID" ]; then
    # Shot CREATE
    SHOT_DATA="{\"scene_id\":\"$TEST_SCENE_ID\",\"shot_number\":1,\"shot_title\":\"Wide Shot\",\"duration_seconds\":5}"
    response=$(curl -s -X POST "$BASE_URL/shots/" -H "Content-Type: application/json" -d "$SHOT_DATA" 2>/dev/null)
    SHOT_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    
    if [ ! -z "$SHOT_ID" ]; then
        echo "  ✅ POST /shots/ - Created $SHOT_ID"
        echo "  ✅ POST /shots/ - Created $SHOT_ID" >> $RESULTS_FILE
        
        test_endpoint "shot" "GET" "shots/?scene_id=$TEST_SCENE_ID" "" "200"
        test_endpoint "shot" "GET" "shots/$SHOT_ID" "" "200"
        test_endpoint "shot" "PUT" "shots/$SHOT_ID" '{"duration_seconds":8}' "200"
        test_endpoint "shot" "GET" "shots/health" "" "200"
        test_endpoint "shot" "DELETE" "shots/$SHOT_ID" "" "204"
    else
        echo "  ❌ POST /shots/ - Failed to create"
        echo "  ❌ POST /shots/ - Failed to create" >> $RESULTS_FILE
    fi
fi

# =============================================================================
# Character Router Tests
# =============================================================================
echo ""
echo "👤 CHARACTER ROUTER"
echo "" >> $RESULTS_FILE
echo "👤 CHARACTER ROUTER" >> $RESULTS_FILE

# Character CREATE
CHAR_DATA='{"project_id":"test_proj_001","character_name":"ศิริพร","role":"protagonist","age_range":"25-30","personality":"gentle, thoughtful"}'
response=$(curl -s -X POST "$BASE_URL/characters/" -H "Content-Type: application/json" -d "$CHAR_DATA" 2>/dev/null)
CHAR_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$CHAR_ID" ]; then
    echo "  ✅ POST /characters/ - Created $CHAR_ID"
    echo "  ✅ POST /characters/ - Created $CHAR_ID" >> $RESULTS_FILE
    
    test_endpoint "character" "GET" "characters/?project_id=test_proj_001" "" "200"
    test_endpoint "character" "GET" "characters/$CHAR_ID" "" "200"
    test_endpoint "character" "PUT" "characters/$CHAR_ID" '{"age_range":"30-35"}' "200"
    test_endpoint "character" "GET" "characters/health" "" "200"
    test_endpoint "character" "DELETE" "characters/$CHAR_ID" "" "204"
else
    echo "  ❌ POST /characters/ - Failed to create"
    echo "  ❌ POST /characters/ - Failed to create" >> $RESULTS_FILE
fi

# =============================================================================
# Visual Router Tests  
# =============================================================================
echo ""
echo "🖼️  VISUAL ROUTER"
echo "" >> $RESULTS_FILE
echo "🖼️  VISUAL ROUTER" >> $RESULTS_FILE

# Create shot for visual
SHOT_DATA2="{\"scene_id\":\"$TEST_SCENE_ID\",\"shot_number\":2,\"shot_title\":\"Visual Test Shot\",\"duration_seconds\":3}"
response=$(curl -s -X POST "$BASE_URL/shots/" -H "Content-Type: application/json" -d "$SHOT_DATA2" 2>/dev/null)
TEST_SHOT_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ ! -z "$TEST_SHOT_ID" ]; then
    # Visual CREATE
    VISUAL_DATA="{\"shot_id\":\"$TEST_SHOT_ID\",\"image_prompt\":\"A beautiful sunset over mountains\",\"image_size\":\"1024x1024\",\"status\":\"pending\"}"
    response=$(curl -s -X POST "$BASE_URL/visuals/" -H "Content-Type: application/json" -d "$VISUAL_DATA" 2>/dev/null)
    VISUAL_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    
    if [ ! -z "$VISUAL_ID" ]; then
        echo "  ✅ POST /visuals/ - Created $VISUAL_ID"
        echo "  ✅ POST /visuals/ - Created $VISUAL_ID" >> $RESULTS_FILE
        
        test_endpoint "visual" "GET" "visuals/?shot_id=$TEST_SHOT_ID" "" "200"
        test_endpoint "visual" "GET" "visuals/$VISUAL_ID" "" "200"
        test_endpoint "visual" "PUT" "visuals/$VISUAL_ID" '{"status":"completed"}' "200"
        test_endpoint "visual" "GET" "visuals/health" "" "200"
        test_endpoint "visual" "DELETE" "visuals/$VISUAL_ID" "" "204"
    else
        echo "  ❌ POST /visuals/ - Failed to create"
        echo "  ❌ POST /visuals/ - Failed to create" >> $RESULTS_FILE
    fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "================================"
echo "📊 SUMMARY"
echo "" >> $RESULTS_FILE
echo "================================" >> $RESULTS_FILE
echo "📊 SUMMARY" >> $RESULTS_FILE

TOTAL_PASS=$(grep -c "✅" $RESULTS_FILE)
TOTAL_FAIL=$(grep -c "❌" $RESULTS_FILE)
TOTAL=$((TOTAL_PASS + TOTAL_FAIL))

echo "Total Tests: $TOTAL"
echo "Passed: $TOTAL_PASS"
echo "Failed: $TOTAL_FAIL"

echo "" >> $RESULTS_FILE
echo "Total Tests: $TOTAL" >> $RESULTS_FILE
echo "Passed: $TOTAL_PASS" >> $RESULTS_FILE
echo "Failed: $TOTAL_FAIL" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE
echo "Completed: $(date)" >> $RESULTS_FILE

echo ""
echo "📄 Full results saved to: $RESULTS_FILE"
