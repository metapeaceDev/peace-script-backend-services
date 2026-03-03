"""
Simulation Chains Router - Chain Management & Analytics
=======================================================
ตามแผน Peace Script V.14 - Step 2.2.48-50, 2.2.84-85

Router นี้จัดการ:
- CRUD operations สำหรับ Chains
- Chain health analysis (karma, emotion, health curves)
- What-if branching (สร้าง alternative chains)
- Chain comparison (เปรียบเทียบ outcomes)

Routes:
    POST   /api/v1/simulation-chains/           - สร้าง chain ใหม่
    GET    /api/v1/simulation-chains/           - List chains
    GET    /api/v1/simulation-chains/{id}       - Get chain by ID
    PATCH  /api/v1/simulation-chains/{id}       - Update chain
    DELETE /api/v1/simulation-chains/{id}       - Delete chain
    GET    /api/v1/simulation-chains/{id}/health      - Chain health analytics
    POST   /api/v1/simulation-chains/{id}/branch      - Create what-if branch
    POST   /api/v1/simulation-chains/compare          - Compare chains
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status
import logging

logger = logging.getLogger(__name__)

from documents_simulation import (
    SimulationChain,
    ChainStatus,
    EnhancedSimulationEvent
)
from schemas_simulation import (
    ChainCreate,
    ChainUpdate,
    ChainResponse,
    ChainHealthResponse,
    WhatIfBranchRequest,
    WhatIfBranchResponse,
    CompareChainsRequest,
    CompareChainsResponse
)

router = APIRouter(prefix="/api/v1/simulation-chains", tags=["Simulation Chains"])


@router.post("/", response_model=ChainResponse, status_code=status.HTTP_201_CREATED)
async def create_chain(chain_data: ChainCreate) -> ChainResponse:
    """
    สร้าง Simulation Chain ใหม่
    
    Args:
        chain_data: ข้อมูล chain (event_ids, scenario_id, etc.)
        
    Returns:
        ChainResponse: Chain ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "scenario_id": "SC-001",
            "event_ids": ["EV-001", "EV-002", "EV-003"],
            "status": "active",
            "is_what_if_branch": false
        }
        ```
    """
    try:
        chain = SimulationChain(
            scenario_id=chain_data.scenario_id,
            event_ids=chain_data.event_ids or [],
            parent_chain_id=chain_data.parent_chain_id,
            branch_point_event_id=chain_data.branch_point_event_id,
            status=chain_data.status or ChainStatus.ACTIVE,
            is_what_if_branch=chain_data.is_what_if_branch or False,
            what_if_condition=chain_data.what_if_condition,
            meta_info=chain_data.meta_info or {}
        )
        
        await chain.insert()
        
        return ChainResponse.model_validate(chain)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chain: {str(e)}"
        )


@router.get("/", response_model=List[ChainResponse])
async def list_chains(
    scenario_id: Optional[str] = Query(None, description="Filter by scenario"),
    status_filter: Optional[ChainStatus] = Query(None, description="Filter by status"),
    is_what_if: Optional[bool] = Query(None, description="Filter what-if branches"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[ChainResponse]:
    """
    List Simulation Chains พร้อม filters
    
    Query Parameters:
        - scenario_id: SC-xxxxx
        - status_filter: active, broken, merged, branched
        - is_what_if: true/false (what-if branches only)
        - limit, skip: pagination
        
    Returns:
        List[ChainResponse]: รายการ chains
    """
    try:
        query = {}
        
        if scenario_id:
            query["scenario_id"] = scenario_id
            
        if status_filter:
            query["status"] = status_filter
            
        if is_what_if is not None:
            query["is_what_if_branch"] = is_what_if
        
        chains = await SimulationChain.find(query).skip(skip).limit(limit).to_list()
        
        return [ChainResponse.model_validate(c) for c in chains]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list chains: {str(e)}"
        )


@router.get("/{chain_id}", response_model=ChainResponse)
async def get_chain(chain_id: str) -> ChainResponse:
    """
    Get Chain by ID
    
    Args:
        chain_id: CH-xxxxx
        
    Returns:
        ChainResponse: Chain data พร้อม events, curves, analytics
    """
    try:
        chain = await SimulationChain.find_one({"chain_id": chain_id})
        
        if not chain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chain {chain_id} not found"
            )
        
        return ChainResponse.model_validate(chain)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chain: {str(e)}"
        )


@router.patch("/{chain_id}", response_model=ChainResponse)
async def update_chain(chain_id: str, update_data: ChainUpdate) -> ChainResponse:
    """
    Update Chain
    
    Args:
        chain_id: CH-xxxxx
        update_data: ข้อมูลที่ต้องการอัปเดต
        
    Returns:
        ChainResponse: Chain ที่อัปเดตแล้ว
    """
    try:
        chain = await SimulationChain.find_one({"chain_id": chain_id})
        
        if not chain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chain {chain_id} not found"
            )
        
        update_dict = update_data.model_dump(exclude_none=True)
        
        for field, value in update_dict.items():
            setattr(chain, field, value)
        
        chain.updated_at = datetime.utcnow()
        await chain.save()
        
        return ChainResponse.model_validate(chain)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chain: {str(e)}"
        )


@router.delete("/{chain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chain(chain_id: str):
    """
    Delete Chain
    
    Args:
        chain_id: CH-xxxxx
    """
    try:
        chain = await SimulationChain.find_one({"chain_id": chain_id})
        
        if not chain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chain {chain_id} not found"
            )
        
        await chain.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chain: {str(e)}"
        )


@router.get("/{chain_id}/health", response_model=ChainHealthResponse)
async def get_chain_health(chain_id: str) -> ChainHealthResponse:
    """
    Get Chain Health Analytics
    
    Args:
        chain_id: CH-xxxxx
        
    Returns:
        ChainHealthResponse: chain_health score, karma_total, curves, insights
        
    Process:
        - คำนวณ chain health (0.0-1.0)
        - Aggregate karma impacts
        - Track emotion/health curves
        - Generate AI insights
    """
    try:
        chain = await SimulationChain.find_one({"chain_id": chain_id})
        
        if not chain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chain {chain_id} not found"
            )
        
        # Generate health insights
        insights = []
        
        if chain.chain_health < 0.3:
            insights.append("Chain health is critical - review negative karma events")
        elif chain.chain_health < 0.6:
            insights.append("Chain health moderate - balance needed")
        else:
            insights.append("Chain health good - positive karma flow")
        
        if chain.karma_total > 0:
            insights.append(f"Positive karma accumulation: {chain.karma_total:.2f}")
        elif chain.karma_total < 0:
            insights.append(f"Negative karma burden: {chain.karma_total:.2f}")
        
        return ChainHealthResponse(
            chain_id=chain.chain_id,
            chain_health=chain.chain_health,
            karma_total=chain.karma_total,
            emotion_curve=chain.emotion_curve,
            health_curve=chain.health_curve,
            insights=insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chain health: {str(e)}"
        )


@router.post("/{chain_id}/branch", response_model=WhatIfBranchResponse, status_code=status.HTTP_201_CREATED)
async def create_what_if_branch(chain_id: str, branch_request: WhatIfBranchRequest) -> WhatIfBranchResponse:
    """
    Create What-If Branch Chain
    
    Args:
        chain_id: CH-xxxxx (parent chain)
        branch_request: branch_point_event_id, alternative_events, condition
        
    Returns:
        WhatIfBranchResponse: Original chain และ branched chain พร้อม comparison
        
    Example:
        ```json
        {
            "branch_point_event_id": "EV-003",
            "alternative_events": [
                {
                    "type": "action",
                    "title": "ให้ทานมากกว่า",
                    "karma_impact": 0.8
                }
            ],
            "what_if_condition": "If gave more dana"
        }
        ```
    """
    try:
        # ค้นหา parent chain
        parent_chain = await SimulationChain.find_one({"chain_id": chain_id})
        
        if not parent_chain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chain {chain_id} not found"
            )
        
        # สร้าง branched chain
        branched_chain = SimulationChain(
            scenario_id=parent_chain.scenario_id,
            event_ids=parent_chain.event_ids.copy(),
            parent_chain_id=parent_chain.chain_id,
            branch_point_event_id=branch_request.branch_point_event_id,
            status=ChainStatus.BRANCHED,
            is_what_if_branch=True,
            what_if_condition=branch_request.what_if_condition,
            meta_info={
                "branched_from": parent_chain.chain_id,
                "branch_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Process and add alternative events from branch_request
        if branch_request.alternative_events:
            try:
                logger.info(f"Processing {len(branch_request.alternative_events)} alternative events for branch")
                
                alternative_event_ids = []
                for alt_event_data in branch_request.alternative_events:
                    # Create new EnhancedSimulationEvent from alternative event data
                    # Note: EnhancedSimulationEvent is embedded, not a Document
                    # Generate event_id for the alternative event
                    import uuid
                    event_id = f"EV-{uuid.uuid4().hex[:12]}"
                    
                    new_event = EnhancedSimulationEvent(
                        event_id=event_id,
                        scenario_id=parent_chain.scenario_id,
                        chain_id=branched_chain.chain_id,  # Will be updated after chain is created
                        type=alt_event_data.get("type", "action"),
                        title=alt_event_data.get("title", "Alternative Event"),
                        description=alt_event_data.get("description", ""),
                        intensity=alt_event_data.get("intensity", 0.5),
                        karma_impact=alt_event_data.get("karma_impact", 0.0),
                        emotion_score=alt_event_data.get("emotion_score", 0.5),
                        health_delta=alt_event_data.get("health_delta", 0.0),
                        annotation=alt_event_data.get("annotation", ""),
                        teaching_note=alt_event_data.get("teaching_note", ""),
                        dhamma_ref=alt_event_data.get("dhamma_ref", ""),
                        timestamp=datetime.utcnow(),
                        payload=alt_event_data.get("payload", {})
                    )
                    
                    # Store event_id (event data will be stored in meta_info)
                    alternative_event_ids.append(event_id)
                    logger.info(f"Created alternative event: {event_id}")
                
                # Add alternative events to branched chain
                # Insert at branch point (find index of branch_point_event_id)
                try:
                    branch_idx = branched_chain.event_ids.index(branch_request.branch_point_event_id)
                    # Insert alternative events after branch point
                    for i, alt_event_id in enumerate(alternative_event_ids):
                        branched_chain.event_ids.insert(branch_idx + 1 + i, alt_event_id)
                except ValueError:
                    # Branch point not found, append to end
                    logger.warning(f"Branch point {branch_request.branch_point_event_id} not found, appending alternative events")
                    branched_chain.event_ids.extend(alternative_event_ids)
                
                # Store alternative events data in meta_info for later retrieval
                branched_chain.meta_info["alternative_events"] = alternative_event_ids
                branched_chain.meta_info["alternative_event_count"] = len(alternative_event_ids)
                branched_chain.meta_info["alternative_event_data"] = [
                    {
                        "event_id": alt_event_data.get("event_id", alternative_event_ids[i]),
                        "type": alt_event_data.get("type", "action"),
                        "title": alt_event_data.get("title", "Alternative Event"),
                        "karma_impact": alt_event_data.get("karma_impact", 0.0),
                        "emotion_score": alt_event_data.get("emotion_score", 0.5),
                        "health_delta": alt_event_data.get("health_delta", 0.0)
                    }
                    for i, alt_event_data in enumerate(branch_request.alternative_events)
                ]
                
                logger.info(f"Added {len(alternative_event_ids)} alternative events to branched chain")
                
            except Exception as e:
                logger.error(f"Error processing alternative events: {e}", exc_info=True)
                # Continue even if alternative events fail
        
        # Recalculate karma, health, emotion curves based on events in branch
        try:
            # Query all events in this chain
            events = []
            for event_id in branched_chain.event_ids:
                event = await EnhancedSimulationEvent.find_one(EnhancedSimulationEvent.event_id == event_id)
                if event:
                    events.append(event)
            
            # Recalculate curves
            karma_total = 0.0
            emotion_curve = []
            health_curve = []
            
            for event in events:
                # Accumulate karma
                karma_total += event.karma_impact
                
                # Build emotion curve (use event's emotion_impact or default)
                emotion_value = getattr(event, 'emotion_impact', 0.5)
                emotion_curve.append(emotion_value)
                
                # Build health curve (use event's health_impact or default)
                health_value = getattr(event, 'health_impact', 0.7)
                health_curve.append(health_value)
            
            # Update branched chain with recalculated values
            branched_chain.karma_total = karma_total
            branched_chain.emotion_curve = emotion_curve
            branched_chain.health_curve = health_curve
            
            # Calculate chain_health (average of health_curve)
            if health_curve:
                branched_chain.chain_health = sum(health_curve) / len(health_curve)
            
        except Exception as e:
            logger.error(f"Error recalculating curves: {e}")
            # Continue with default values
        
        await branched_chain.insert()
        
        # Add to parent's alternative_chains
        if branched_chain.chain_id not in parent_chain.alternative_chains:
            parent_chain.alternative_chains.append(branched_chain.chain_id)
            await parent_chain.save()
        
        # Generate comparison
        comparison = {
            "karma_diff": branched_chain.karma_total - parent_chain.karma_total,
            "health_diff": branched_chain.chain_health - parent_chain.chain_health,
            "outcome": "Branch created successfully"
        }
        
        return WhatIfBranchResponse(
            original_chain=ChainResponse.model_validate(parent_chain),
            branched_chain=ChainResponse.model_validate(branched_chain),
            comparison=comparison
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create what-if branch: {str(e)}"
        )


@router.post("/compare", response_model=CompareChainsResponse)
async def compare_chains(compare_request: CompareChainsRequest) -> CompareChainsResponse:
    """
    Compare Multiple Chains
    
    Args:
        compare_request: chain_ids to compare
        
    Returns:
        CompareChainsResponse: Chains พร้อม comparison matrix
        
    Example:
        ```json
        {
            "chain_ids": ["CH-001", "CH-002", "CH-003"]
        }
        ```
    """
    try:
        chains = []
        
        for chain_id in compare_request.chain_ids:
            chain = await SimulationChain.find_one({"chain_id": chain_id})
            if chain:
                chains.append(chain)
        
        if not chains:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chains found for comparison"
            )
        
        # Generate comparison matrix
        comparison_matrix = {}
        
        for chain in chains:
            comparison_matrix[chain.chain_id] = {
                "karma": chain.karma_total,
                "health": chain.chain_health,
                "event_count": len(chain.event_ids),
                "status": chain.status
            }
        
        # Calculate insights
        karma_values = [c.karma_total for c in chains]
        health_values = [c.chain_health for c in chains]
        
        best_karma_chain = max(chains, key=lambda c: c.karma_total)
        best_health_chain = max(chains, key=lambda c: c.chain_health)
        
        insights = [
            f"Best karma: {best_karma_chain.chain_id} ({best_karma_chain.karma_total:.2f})",
            f"Best health: {best_health_chain.chain_id} ({best_health_chain.chain_health:.2f})",
            f"Karma range: {min(karma_values):.2f} to {max(karma_values):.2f}",
            f"Health range: {min(health_values):.2f} to {max(health_values):.2f}"
        ]
        
        return CompareChainsResponse(
            chains=[ChainResponse.model_validate(c) for c in chains],
            comparison_matrix=comparison_matrix,
            insights=insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare chains: {str(e)}"
        )
