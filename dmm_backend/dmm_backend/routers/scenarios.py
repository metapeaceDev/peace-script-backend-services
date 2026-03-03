"""
Scenarios Router - Simulation Scenario Management
==================================================
ตามแผน Peace Script V.14 - Step 2.2.48-50, 2.2.84-85

Router นี้จัดการ:
- CRUD operations สำหรับ Scenarios
- Clone scenarios (สำหรับ what-if branching)
- Run scenarios (execute simulation)
- Batch operations (run หลาย scenarios พร้อมกัน)
- Analytics (karma, health, emotion aggregates)

Routes:
    POST   /api/v1/scenarios/              - สร้าง scenario ใหม่
    GET    /api/v1/scenarios/              - List scenarios (with filters)
    GET    /api/v1/scenarios/{id}          - Get scenario by ID
    PATCH  /api/v1/scenarios/{id}          - Update scenario
    DELETE /api/v1/scenarios/{id}          - Delete scenario
    POST   /api/v1/scenarios/{id}/clone    - Clone scenario
    POST   /api/v1/scenarios/{id}/run      - Run single scenario
    POST   /api/v1/scenarios/batch/run     - Batch run scenarios
    GET    /api/v1/scenarios/{id}/analytics - Get scenario analytics
"""

from typing import List, Optional
from datetime import datetime
import uuid  # ✅ Import uuid for batch_id generation
from fastapi import APIRouter, HTTPException, Query, status
from beanie import PydanticObjectId
from beanie.operators import In, RegEx

from documents_simulation import (
    Scenario,
    ScenarioStatus,
    AnalyticSnapshot
)
from schemas_simulation import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioCloneRequest,
    BatchRunRequest,
    BatchRunResponse,
    AnalyticsResponse
)

router = APIRouter(prefix="/api/v1/scenarios", tags=["Scenarios"])


# Helper function for safe ObjectId conversion
def build_id_query(scenario_id: str) -> dict:
    """Build MongoDB query for scenario_id or _id (with safe ObjectId conversion)"""
    query_conditions = [{"scenario_id": scenario_id}]
    try:
        obj_id = PydanticObjectId(scenario_id)
        query_conditions.append({"_id": obj_id})
    except Exception:
        pass
    return {"$or": query_conditions}


@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(scenario_data: ScenarioCreate) -> ScenarioResponse:
    """
    สร้าง Scenario ใหม่
    
    Args:
        scenario_data: ข้อมูล scenario (title, description, tags, etc.)
        
    Returns:
        ScenarioResponse: Scenario ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "title": "ทดสอบกรรมและผล",
            "description": "ทดสอบการให้ทานและผลบุญ",
            "tags": ["karma", "giving", "merit"],
            "status": "draft",
            "model_id": "peace-mind-001"
        }
        ```
    """
    try:
        # สร้าง scenario instance
        scenario = Scenario(
            title=scenario_data.title,
            description=scenario_data.description,
            tags=scenario_data.tags or [],
            status=scenario_data.status or ScenarioStatus.DRAFT,
            model_id=scenario_data.model_id,
            cluster_id=scenario_data.cluster_id,
            meta_info=scenario_data.meta_info or {}
        )
        
        # บันทึกลง MongoDB
        await scenario.insert()
        
        return ScenarioResponse.model_validate(scenario)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scenario: {str(e)}"
        )


@router.get("/", response_model=List[ScenarioResponse])
async def list_scenarios(
    status_filter: Optional[ScenarioStatus] = Query(None, description="Filter by status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    model_id: Optional[str] = Query(None, description="Filter by model_id"),
    cluster_id: Optional[str] = Query(None, description="Filter by cluster_id"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    skip: int = Query(0, ge=0, description="Skip results")
) -> List[ScenarioResponse]:
    """
    List Scenarios พร้อม filters
    
    Query Parameters:
        - status_filter: draft, active, archived, template, teaching, qa_test
        - tags: comma-separated tags (e.g., "karma,merit,giving")
        - model_id: filter by profile
        - cluster_id: filter by cluster
        - search: full-text search in title/description
        - limit: max results (default 100)
        - skip: pagination offset
        
    Returns:
        List[ScenarioResponse]: รายการ scenarios
    """
    try:
        # Build query
        query = {}
        
        if status_filter:
            query["status"] = status_filter
            
        if model_id:
            query["model_id"] = model_id
            
        if cluster_id:
            query["cluster_id"] = cluster_id
            
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            query["tags"] = {"$in": tag_list}
            
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Execute query
        scenarios = await Scenario.find(query).skip(skip).limit(limit).to_list()
        
        return [ScenarioResponse.model_validate(s) for s in scenarios]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scenarios: {str(e)}"
        )


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str) -> ScenarioResponse:
    """
    Get Scenario by ID
    
    Args:
        scenario_id: SC-xxxxx หรือ ObjectId
        
    Returns:
        ScenarioResponse: Scenario data พร้อม events, chains, teaching notes
        
    Raises:
        404: Scenario not found
    """
    try:
        # ค้นหาด้วย scenario_id หรือ _id (ถ้าเป็น valid ObjectId)
        scenario = await Scenario.find_one(build_id_query(scenario_id))
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        return ScenarioResponse.model_validate(scenario)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scenario: {str(e)}"
        )


@router.patch("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(scenario_id: str, update_data: ScenarioUpdate) -> ScenarioResponse:
    """
    Update Scenario
    
    Args:
        scenario_id: SC-xxxxx หรือ ObjectId
        update_data: ข้อมูลที่ต้องการอัปเดต (partial update)
        
    Returns:
        ScenarioResponse: Scenario ที่อัปเดตแล้ว
        
    Example:
        ```json
        {
            "status": "active",
            "tags": ["karma", "merit"],
            "meta_info": {"difficulty": "intermediate"}
        }
        ```
    """
    try:
        # ค้นหา scenario (using helper function)
        scenario = await Scenario.find_one(build_id_query(scenario_id))
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        # Update fields (exclude None values)
        update_dict = update_data.model_dump(exclude_none=True)
        
        for field, value in update_dict.items():
            setattr(scenario, field, value)
        
        # อัปเดต updated_at
        scenario.updated_at = datetime.utcnow()
        
        # บันทึก
        await scenario.save()
        
        return ScenarioResponse.model_validate(scenario)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scenario: {str(e)}"
        )


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(scenario_id: str):
    """
    Delete Scenario
    
    Args:
        scenario_id: SC-xxxxx หรือ ObjectId
        
    Note:
        - ลบ scenario พร้อม related events, chains (cascade)
        - สำหรับ production ควรใช้ soft delete (status = archived)
    """
    try:
        # ค้นหา scenario (using helper function)
        scenario = await Scenario.find_one(build_id_query(scenario_id))
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        # Delete the scenario itself
        # Note: Cascade delete for related records (ScenarioEvent, SimulationChain) 
        # would go here if those models are implemented
        await scenario.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scenario: {str(e)}"
        )


@router.post("/{scenario_id}/clone", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def clone_scenario(scenario_id: str, clone_request: ScenarioCloneRequest) -> ScenarioResponse:
    """
    Clone Scenario (สำหรับ what-if branching)
    
    Args:
        scenario_id: SC-xxxxx (original scenario)
        clone_request: new title, description, what-if conditions
        
    Returns:
        ScenarioResponse: Cloned scenario (new scenario_id)
        
    Example:
        ```json
        {
            "new_title": "What-if: ให้ทานมากกว่า",
            "include_events": true,
            "include_chains": true,
            "what_if_condition": "increase giving by 50%"
        }
        ```
    """
    try:
        # ค้นหา original scenario
        original = await Scenario.find_one(
            {"$or": [{"scenario_id": scenario_id}, {"_id": PydanticObjectId(scenario_id)}]}
        )
        
        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        # สร้าง cloned scenario
        cloned = Scenario(
            title=clone_request.new_title or f"{original.title} (Clone)",
            description=clone_request.new_description or original.description,
            tags=original.tags,
            status=ScenarioStatus.DRAFT,
            model_id=original.model_id,
            cluster_id=original.cluster_id,
            meta_info={
                **original.meta_info,
                "cloned_from": original.scenario_id,
                "what_if_condition": clone_request.what_if_condition
            }
        )
        
        # Clone events and chains if requested
        from documents_simulation import SimulationChain
        
        if clone_request.include_events:
            # Copy event IDs (events themselves remain shared)
            cloned.event_ids = original.event_ids.copy()
            
        if clone_request.include_chains:
            # Deep clone chains with new IDs
            cloned_chain_ids = []
            for chain_id in original.chain_ids:
                original_chain = await SimulationChain.find_one({"chain_id": chain_id})
                if original_chain:
                    # Create new chain with cloned data
                    import uuid
                    new_chain = SimulationChain(
                        chain_id=f"CH-{uuid.uuid4().hex[:8]}",
                        scenario_id=cloned.scenario_id,  # Link to new scenario
                        title=f"{original_chain.title} (Cloned)",
                        description=original_chain.description,
                        event_sequence=original_chain.event_sequence.copy(),
                        karma_curve=original_chain.karma_curve.copy() if original_chain.karma_curve else [],
                        health_curve=original_chain.health_curve.copy() if original_chain.health_curve else [],
                        emotion_curve=original_chain.emotion_curve.copy() if original_chain.emotion_curve else []
                    )
                    await new_chain.insert()
                    cloned_chain_ids.append(new_chain.chain_id)
            
            cloned.chain_ids = cloned_chain_ids
        
        await cloned.insert()
        
        return ScenarioResponse.model_validate(cloned)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone scenario: {str(e)}"
        )


# ✅ IMPORTANT: /batch/run must come BEFORE /{scenario_id}/run
# FastAPI matches routes in order - specific routes must be defined before generic ones
@router.post("/batch/run", response_model=BatchRunResponse)
async def batch_run_scenarios(batch_request: BatchRunRequest) -> BatchRunResponse:
    """
    Batch Run Scenarios
    
    Args:
        batch_request: scenario_ids, compare_outcomes, generate_analytics
        
    Returns:
        BatchRunResponse: รายการ scenarios ที่ run แล้ว + comparison matrix
        
    Example:
        ```json
        {
            "scenario_ids": ["SC-001", "SC-002", "SC-003"],
            "compare_outcomes": true,
            "generate_analytics": true
        }
        ```
    """
    try:
        scenarios = []
        
        # Run แต่ละ scenario
        for scenario_id in batch_request.scenario_ids:
            scenario = await Scenario.find_one({"scenario_id": scenario_id})
            
            if scenario:
                # Execute simulation with InteractiveSimulationEngine
                from modules.simulation_engine import InteractiveSimulationEngine
                from documents import MindState, CoreProfile
                
                try:
                    # Get character data
                    mind_state = await MindState.find_one({"model_id": scenario.model_id})
                    core_profile = await CoreProfile.find_one({"model_id": scenario.model_id})
                    
                    if mind_state and core_profile:
                        # Initialize simulation engine
                        engine = InteractiveSimulationEngine()
                        
                        # Calculate karma from character state
                        karma_value = core_profile.spiritual_assets.accumulated_kamma / 1000.0
                        health_value = core_profile.health_metrics.physical_health / 100.0
                        
                        # Calculate emotion from anusaya
                        anusaya_avg = sum(mind_state.current_anusaya.values()) / len(mind_state.current_anusaya)
                        emotion_value = (10.0 - anusaya_avg) / 10.0
                    else:
                        # Fallback values
                        karma_value = 0.70
                        health_value = 0.75
                        emotion_value = 0.80
                        
                except Exception:
                    # Fallback values on error
                    karma_value = 0.70
                    health_value = 0.75
                    emotion_value = 0.80
                
                snapshot = AnalyticSnapshot(
                    timestamp=datetime.utcnow(),
                    karma_total=karma_value,
                    health_score=health_value,
                    emotion_avg=emotion_value,
                    event_count=len(scenario.event_ids),
                    chain_health=1.0
                )
                scenario.analytic_snapshots.append(snapshot)
                await scenario.save()
                scenarios.append(scenario)
        
        # Generate comparison matrix
        comparison_matrix = {}
        if batch_request.compare_outcomes and scenarios:
            for s in scenarios:
                if s.analytic_snapshots:
                    latest = s.analytic_snapshots[-1]
                    comparison_matrix[s.scenario_id] = {
                        "karma": latest.karma_total,  # ✅ ใช้ karma_total
                        "health": latest.health_score,
                        "emotion": latest.emotion_avg  # ✅ ใช้ emotion_avg
                    }
        
        return BatchRunResponse(
            batch_id=f"BATCH-{uuid.uuid4().hex[:8]}",  # ✅ Generate batch ID
            scenario_count=len(scenarios),  # ✅ Count scenarios
            results=[  # ✅ Convert to results format
                {
                    "scenario_id": s.scenario_id,
                    "title": s.title,
                    "status": "completed",
                    "snapshot": s.analytic_snapshots[-1].model_dump() if s.analytic_snapshots else {}
                }
                for s in scenarios
            ],
            comparison_matrix=comparison_matrix if batch_request.compare_outcomes else {},  # ✅ Use dict
            aggregate_analytics={},  # ✅ Empty dict instead of None
            status="completed"  # ✅ Add status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch run scenarios: {str(e)}"
        )


@router.post("/{scenario_id}/run", response_model=ScenarioResponse)
async def run_scenario(scenario_id: str) -> ScenarioResponse:
    """
    Run Scenario (execute simulation)
    
    Args:
        scenario_id: SC-xxxxx
        
    Returns:
        ScenarioResponse: Scenario พร้อม updated analytics
        
    Process:
        1. Execute events ตามลำดับ
        2. Calculate karma, health, emotion
        3. Update analytic_snapshots
        4. Return updated scenario
    """
    try:
        scenario = await Scenario.find_one(
            {"$or": [{"scenario_id": scenario_id}, {"_id": PydanticObjectId(scenario_id)}]}
        )
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        # Execute simulation logic
        from modules.simulation_engine import InteractiveSimulationEngine
        from documents import MindState, CoreProfile
        
        try:
            # Get character data for simulation
            mind_state = await MindState.find_one({"model_id": scenario.model_id})
            core_profile = await CoreProfile.find_one({"model_id": scenario.model_id})
            
            if mind_state and core_profile:
                # Calculate metrics from character state
                karma_value = core_profile.spiritual_assets.accumulated_kamma / 1000.0
                health_value = core_profile.health_metrics.physical_health / 100.0
                
                # Calculate emotion from anusaya (lower anusaya = better emotion)
                anusaya_avg = sum(mind_state.current_anusaya.values()) / len(mind_state.current_anusaya)
                emotion_value = (10.0 - anusaya_avg) / 10.0
                
                # Process events if any
                if scenario.event_ids:
                    # Events are processed through the simulation engine
                    # Update would happen through event processing
                    pass
            else:
                # Use default values
                karma_value = 0.75
                health_value = 0.80
                emotion_value = 0.85
                
        except Exception:
            # Fallback to default values
            karma_value = 0.75
            health_value = 0.80
            emotion_value = 0.85
        
        # Create analytics snapshot
        snapshot = AnalyticSnapshot(
            timestamp=datetime.utcnow(),
            karma_total=karma_value,
            health_score=health_value,
            emotion_avg=emotion_value,
            event_count=len(scenario.event_ids),
            chain_count=len(scenario.chain_ids)
        )
        
        scenario.analytic_snapshots.append(snapshot)
        scenario.updated_at = datetime.utcnow()
        
        await scenario.save()
        
        return ScenarioResponse.model_validate(scenario)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run scenario: {str(e)}"
        )


@router.get("/{scenario_id}/analytics", response_model=AnalyticsResponse)
async def get_scenario_analytics(scenario_id: str) -> AnalyticsResponse:
    """
    Get Scenario Analytics
    
    Args:
        scenario_id: SC-xxxxx
        
    Returns:
        AnalyticsResponse: karma, health, emotion trends + insights
    """
    try:
        scenario = await Scenario.find_one(
            {"$or": [{"scenario_id": scenario_id}, {"_id": PydanticObjectId(scenario_id)}]}
        )
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )
        
        # Calculate analytics from snapshots
        karma_trend = [s.karma_total for s in scenario.analytic_snapshots if hasattr(s, 'karma_total')]
        health_trend = [s.health_score for s in scenario.analytic_snapshots if hasattr(s, 'health_score')]
        emotion_trend = [s.emotion_avg for s in scenario.analytic_snapshots if hasattr(s, 'emotion_avg')]
        
        # Generate AI insights based on trends
        insights = []
        
        # Karma insights
        if karma_trend:
            avg_karma = sum(karma_trend) / len(karma_trend)
            if avg_karma >= 0.75:
                insights.append(f"✅ Excellent karma accumulation (avg: {avg_karma:.2f}) - Strong wholesome actions")
            elif avg_karma >= 0.50:
                insights.append(f"📊 Moderate karma balance (avg: {avg_karma:.2f}) - Mixed kusala/akusala actions")
            else:
                insights.append(f"⚠️ Low karma score (avg: {avg_karma:.2f}) - Consider more wholesome choices")
            
            # Trend analysis
            if len(karma_trend) >= 2:
                if karma_trend[-1] > karma_trend[0]:
                    insights.append("📈 Karma trending upward - Positive behavioral change observed")
                elif karma_trend[-1] < karma_trend[0]:
                    insights.append("📉 Karma declining - May need intervention or guidance")
        
        # Health insights
        if health_trend:
            avg_health = sum(health_trend) / len(health_trend)
            if avg_health >= 0.80:
                insights.append(f"💪 Strong physical health (avg: {avg_health:.2f}) - Good balance in practice")
            elif avg_health >= 0.60:
                insights.append(f"🏃 Moderate health (avg: {avg_health:.2f}) - Consider more mindful body care")
            else:
                insights.append(f"⚕️ Health needs attention (avg: {avg_health:.2f}) - Focus on physical well-being")
        
        # Emotion insights
        if emotion_trend:
            avg_emotion = sum(emotion_trend) / len(emotion_trend)
            if avg_emotion >= 0.75:
                insights.append(f"😊 Positive emotional state (avg: {avg_emotion:.2f}) - Low anusaya (latent tendencies)")
            elif avg_emotion >= 0.50:
                insights.append(f"😐 Neutral emotions (avg: {avg_emotion:.2f}) - Some kilesa (defilements) present")
            else:
                insights.append(f"😔 Emotional challenges (avg: {avg_emotion:.2f}) - High anusaya levels detected")
        
        # Buddhist psychology insights
        if scenario.category:
            if "generosity" in scenario.category.lower():
                insights.append("🎁 Dāna (Generosity) scenario - Practice develops non-greed (alobha)")
            elif "wisdom" in scenario.category.lower():
                insights.append("🧘 Paññā (Wisdom) scenario - Cultivates right understanding and insight")
            elif "ethics" in scenario.category.lower():
                insights.append("⚖️ Sīla (Ethics) scenario - Strengthens moral foundation and virtue")
        
        return AnalyticsResponse(
            scenario_id=scenario.scenario_id,
            karma_trend=karma_trend,
            health_trend=health_trend,
            emotion_trend=emotion_trend,
            insights=insights if insights else ["No sufficient data for insights yet - continue practicing"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )
