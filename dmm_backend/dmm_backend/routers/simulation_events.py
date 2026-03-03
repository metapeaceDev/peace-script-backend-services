"""
Simulation Events Router - Event Management
===========================================
ตามแผน Peace Script V.14 - Step 2.2.48-50, 2.2.84-85

Router นี้จัดการ:
- CRUD operations สำหรับ Events
- Event annotations (บันทึกเพิ่มเติม)
- AI insights (วิเคราะห์ event ด้วย AI)
- Event linking (parent-child relationships)

Routes:
    POST   /api/v1/simulation-events/           - สร้าง event ใหม่
    GET    /api/v1/simulation-events/           - List events
    GET    /api/v1/simulation-events/{id}       - Get event by ID
    PATCH  /api/v1/simulation-events/{id}       - Update event
    DELETE /api/v1/simulation-events/{id}       - Delete event
    POST   /api/v1/simulation-events/{id}/annotate  - Add annotation
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from documents_simulation import (
    Scenario,
    EnhancedSimulationEvent,
    EventType
)
from documents import DigitalMindModel
from schemas_simulation import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventAnnotateRequest
)
from modules.kamma_engine import log_new_kamma, check_and_trigger_pending_kamma
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/simulation-events", tags=["Simulation Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate) -> EventResponse:
    """
    สร้าง Simulation Event ใหม่
    
    Args:
        event_data: ข้อมูล event (type, title, intensity, karma_impact, etc.)
        
    Returns:
        EventResponse: Event ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "scenario_id": "SC-001",
            "type": "action",
            "title": "ให้ทาน",
            "description": "ให้อาหารกับผู้ขอทาน",
            "intensity": 0.8,
            "karma_impact": 0.5,
            "emotion_score": 0.9
        }
        ```
    """
    try:
        # ค้นหา scenario
        scenario = await Scenario.find_one({"scenario_id": event_data.scenario_id})
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {event_data.scenario_id} not found"
            )
        
        # สร้าง event instance
        event = EnhancedSimulationEvent(
            scenario_id=event_data.scenario_id,
            type=event_data.type,
            title=event_data.title,
            description=event_data.description,
            timestamp=event_data.timestamp or datetime.utcnow(),
            parent_event_id=event_data.parent_event_id,
            chain_id=event_data.chain_id,
            intensity=event_data.intensity or 0.5,
            karma_impact=event_data.karma_impact,
            emotion_score=event_data.emotion_score,
            health_delta=event_data.health_delta,
            annotation=event_data.annotation,
            teaching_note=event_data.teaching_note,
            dhamma_ref=event_data.dhamma_ref,
            payload=event_data.payload or {}
        )
        
        # เพิ่ม event_id เข้า scenario
        scenario.event_ids.append(event.event_id)
        
        # Update parent event (link child)
        if event.parent_event_id:
            for existing_event in scenario.events:
                if existing_event.event_id == event.parent_event_id:
                    existing_event.child_event_ids.append(event.event_id)
                    break
        
        # เพิ่ม event เข้า scenario.events
        scenario.events.append(event)
        
        await scenario.save()
        
        # ===================================================================
        # KAMMA INTEGRATION: Log simulation event as kamma (Step 2.2.5)
        # ===================================================================
        try:
            # Assume scenario has model_id or get from context
            # For now, use scenario owner if available in payload
            model_id = event_data.payload.get("model_id") if event_data.payload else None
            
            if model_id:
                profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
                if profile:
                    profile_dict = profile.model_dump()
                    
                    # Determine kusala based on karma_impact and event type
                    is_kusala = (event.karma_impact or 0) > 0
                    intensity = abs(event.karma_impact or 0.5)
                    
                    # Log kamma
                    kamma_id = log_new_kamma(
                        profile=profile_dict,
                        action_type="simulation",
                        details={
                            "event_id": event.event_id,
                            "event_type": str(event.type),
                            "title": event.title,
                            "scenario_id": event.scenario_id
                        },
                        is_kusala=is_kusala,
                        intensity=intensity,
                        trace_parent=None
                    )
                    
                    # Check and trigger any pending kamma
                    triggered = check_and_trigger_pending_kamma(
                        profile=profile_dict,
                        event_type="simulation",
                        event_detail={
                            "event": event.title.lower(),
                            "intensity": event.intensity,
                            "karma_impact": event.karma_impact
                        }
                    )
                    
                    # Update profile with new kamma state
                    profile.CoreProfile = profile_dict.get("CoreProfile", {})
                    await profile.save()
                    
                    logger.info(f"Kamma logged for simulation event: {kamma_id}, triggered: {len(triggered)}")
        except Exception as kamma_err:
            # Don't fail event creation if kamma logging fails
            logger.warning(f"Failed to log kamma for simulation event: {kamma_err}")
        
        return EventResponse.model_validate(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@router.get("/", response_model=List[EventResponse])
async def list_events(
    scenario_id: Optional[str] = Query(None, description="Filter by scenario"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    chain_id: Optional[str] = Query(None, description="Filter by chain"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[EventResponse]:
    """
    List Simulation Events พร้อม filters
    
    Query Parameters:
        - scenario_id: SC-xxxxx
        - event_type: karma, action, dream, teaching, qa, etc.
        - chain_id: CH-xxxxx
        - search: full-text search
        - limit, skip: pagination
        
    Returns:
        List[EventResponse]: รายการ events
    """
    try:
        # Build query สำหรับ scenario
        query = {}
        
        if scenario_id:
            query["scenario_id"] = scenario_id
        
        # ค้นหา scenarios
        scenarios = await Scenario.find(query).to_list()
        
        # รวม events จากทุก scenarios
        all_events = []
        for scenario in scenarios:
            for event in scenario.events:
                # Apply filters
                if event_type and event.type != event_type:
                    continue
                if chain_id and event.chain_id != chain_id:
                    continue
                if search:
                    search_lower = search.lower()
                    if search_lower not in event.title.lower() and \
                       (not event.description or search_lower not in event.description.lower()):
                        continue
                
                all_events.append(event)
        
        # Pagination
        paginated = all_events[skip:skip + limit]
        
        return [EventResponse.model_validate(e) for e in paginated]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str) -> EventResponse:
    """
    Get Event by ID
    
    Args:
        event_id: EV-xxxxx
        
    Returns:
        EventResponse: Event data พร้อม parent/child relationships
    """
    try:
        # ค้นหา scenario ที่มี event นี้
        scenarios = await Scenario.find({"event_ids": event_id}).to_list()
        
        if not scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        # หา event ใน scenario.events
        for scenario in scenarios:
            for event in scenario.events:
                if event.event_id == event_id:
                    return EventResponse.model_validate(event)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found in scenario events"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event: {str(e)}"
        )


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, update_data: EventUpdate) -> EventResponse:
    """
    Update Event
    
    Args:
        event_id: EV-xxxxx
        update_data: ข้อมูลที่ต้องการอัปเดต
        
    Returns:
        EventResponse: Event ที่อัปเดตแล้ว
    """
    try:
        # ค้นหา scenario
        scenarios = await Scenario.find({"event_ids": event_id}).to_list()
        
        if not scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        # Update event
        scenario = scenarios[0]
        event_updated = False
        
        for event in scenario.events:
            if event.event_id == event_id:
                # Update fields
                update_dict = update_data.model_dump(exclude_none=True)
                for field, value in update_dict.items():
                    setattr(event, field, value)
                
                event_updated = True
                break
        
        if not event_updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found in scenario"
            )
        
        scenario.updated_at = datetime.utcnow()
        await scenario.save()
        
        # Return updated event
        for event in scenario.events:
            if event.event_id == event_id:
                return EventResponse.model_validate(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """
    Delete Event
    
    Args:
        event_id: EV-xxxxx
        
    Note:
        - ลบ event จาก scenario.events
        - อัปเดต parent/child relationships
    """
    try:
        scenarios = await Scenario.find({"event_ids": event_id}).to_list()
        
        if not scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        scenario = scenarios[0]
        
        # ลบ event_id จาก event_ids
        scenario.event_ids = [eid for eid in scenario.event_ids if eid != event_id]
        
        # ลบ event จาก events array
        scenario.events = [e for e in scenario.events if e.event_id != event_id]
        
        # อัปเดต parent/child links
        for event in scenario.events:
            if event.parent_event_id == event_id:
                event.parent_event_id = None
            event.child_event_ids = [cid for cid in event.child_event_ids if cid != event_id]
        
        scenario.updated_at = datetime.utcnow()
        await scenario.save()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )


@router.post("/{event_id}/annotate", response_model=EventResponse)
async def annotate_event(event_id: str, annotate_request: EventAnnotateRequest) -> EventResponse:
    """
    Add Annotation to Event
    
    Args:
        event_id: EV-xxxxx
        annotate_request: annotation text, teaching note, Dhamma reference
        
    Returns:
        EventResponse: Event พร้อม annotation
        
    Example:
        ```json
        {
            "annotation": "จุดนี้สำคัญ: การให้ทานเกิดจากเจตนาบริสุทธิ์",
            "teaching_note": "สอนเรื่องเจตนาในการให้",
            "dhamma_ref": "AN 3.65 - กัลยาณิมิตตตา"
        }
        ```
    """
    try:
        scenarios = await Scenario.find({"event_ids": event_id}).to_list()
        
        if not scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        scenario = scenarios[0]
        event_found = False
        
        for event in scenario.events:
            if event.event_id == event_id:
                # Add annotations
                if annotate_request.annotation:
                    event.annotation = annotate_request.annotation
                    
                if annotate_request.teaching_note:
                    event.teaching_note = annotate_request.teaching_note
                    
                if annotate_request.dhamma_ref:
                    event.dhamma_ref = annotate_request.dhamma_ref
                    
                if annotate_request.ai_insight:
                    event.ai_insight = annotate_request.ai_insight
                
                event_found = True
                break
        
        if not event_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found in scenario"
            )
        
        scenario.updated_at = datetime.utcnow()
        await scenario.save()
        
        # Return annotated event
        for event in scenario.events:
            if event.event_id == event_id:
                return EventResponse.model_validate(event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to annotate event: {str(e)}"
        )
