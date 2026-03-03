"""
Production Management API Router

Provides endpoints for production planning and breakdown management.
Implements the 3-table breakdown system from Peace Script workflow (STEP 5):
- Breakdown Q: Production queue management
- Scene Breakdown: Scene-level production details  
- Crew Sheet: Crew and equipment management

Author: Peace Script Team
Date: 18 November 2568
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from datetime import date, time, datetime
from pydantic import BaseModel, Field

from documents_production import (
    ProductionQueue,
    SceneBreakdown,
    CrewSheet,
    PropsInventory,
    ProductionStatus,
    LocationType,
    ShootingPeriod,
    PropCategory,
    CrewMember,
    CastMember,
    ExtraRequirement,
    PropItem,
    EquipmentItem
)

router = APIRouter(prefix="/api/production", tags=["production"])


# ============================================================================
# Schemas
# ============================================================================

class ProductionQueueCreate(BaseModel):
    """Create production queue request"""
    queue_number: int = Field(..., ge=1)
    project_id: str
    company_name: str = "Peace Studio"
    theme: Optional[str] = None
    filming_date: date
    call_time: time = Field(default=time(6, 0))
    location: str
    breakdown_by: str = "Peace Script System"
    director: str
    first_ad: str
    first_ad_phone: Optional[str] = None
    pm_phone: Optional[str] = None
    weather_forecast: Optional[str] = None
    backup_location: Optional[str] = None
    notes: Optional[str] = None


class SceneBreakdownCreate(BaseModel):
    """Create scene breakdown request"""
    queue_id: str
    scene_id: str
    scene_number: int = Field(..., ge=1)
    shooting_time: int = Field(..., ge=1)
    estimated_duration: Optional[float] = None
    location: str
    int_ext: LocationType
    day_night: ShootingPeriod
    set_name: str
    scene_name: str
    description: Optional[str] = None
    cast: List[CastMember] = []
    extras: List[ExtraRequirement] = []
    props: List[PropItem] = []
    costumes: List[str] = []
    special_requirements: Optional[str] = None
    camera_notes: Optional[str] = None
    lighting_notes: Optional[str] = None
    sound_notes: Optional[str] = None
    remarks: Optional[str] = None


class CrewSheetCreate(BaseModel):
    """Create crew sheet request"""
    queue_id: str
    crew: List[CrewMember] = []
    actors: List[CastMember] = []
    extras: List[ExtraRequirement] = []
    equipment: List[EquipmentItem] = []
    on_location_time: Optional[time] = None
    ready_to_shoot_time: Optional[time] = None
    wrap_time: Optional[time] = None
    total_extras: int = 0
    total_costumes: int = 0
    total_props: int = 0
    support_notes: Optional[str] = None
    special_notes: Optional[str] = None
    estimated_budget: Optional[float] = None


class PropCreate(BaseModel):
    """Create prop request"""
    project_id: str
    name: str
    category: PropCategory
    description: Optional[str] = None
    quantity_needed: int = Field(..., ge=1)
    quantity_available: int = Field(default=0, ge=0)
    source: Optional[str] = None
    supplier: Optional[str] = None
    cost_estimate: Optional[float] = None
    scenes_used: List[str] = []
    usage_notes: Optional[str] = None
    status: str = "needed"
    storage_location: Optional[str] = None
    responsible_person: Optional[str] = None
    reference_images: List[str] = []
    notes: Optional[str] = None


# ============================================================================
# Production Queue Endpoints
# ============================================================================

@router.post("/queues")
async def create_production_queue(data: ProductionQueueCreate):
    """
    Create a new production queue (Breakdown Q - Part 1)
    
    **Request Body:**
    - queue_number: Queue sequence number
    - project_id: Reference to parent project
    - filming_date: Scheduled filming date
    - location: Filming location
    - director: Director name
    - first_ad: First AD name
    - And more...
    
    **Returns:** Created queue with generated queue_id
    """
    try:
        # Generate queue_id
        queue_id = f"Q{data.queue_number:03d}"
        
        # Create queue
        queue = ProductionQueue(
            queue_id=queue_id,
            **data.dict()
        )
        
        await queue.insert()
        
        return {
            "success": True,
            "queue_id": queue_id,
            "queue": queue.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues")
async def list_production_queues(
    project_id: Optional[str] = Query(None),
    status: Optional[ProductionStatus] = Query(None),
    filming_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    List production queues with filters
    
    **Query Parameters:**
    - project_id: Filter by project
    - status: Filter by status
    - filming_date: Filter by filming date
    - skip: Pagination offset
    - limit: Results per page
    
    **Returns:** List of queues
    """
    try:
        query = {}
        
        if project_id:
            query["project_id"] = project_id
        if status:
            query["status"] = status
        if filming_date:
            query["filming_date"] = filming_date
        
        queues = await ProductionQueue.find(query).skip(skip).limit(limit).to_list()
        total = await ProductionQueue.find(query).count()
        
        return {
            "success": True,
            "total": total,
            "queues": [q.dict() for q in queues]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/{queue_id}")
async def get_production_queue(queue_id: str):
    """Get production queue by ID"""
    try:
        queue = await ProductionQueue.find_one({"queue_id": queue_id})
        
        if not queue:
            raise HTTPException(status_code=404, detail=f"Queue {queue_id} not found")
        
        return {
            "success": True,
            "queue": queue.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/queues/{queue_id}")
async def update_production_queue(queue_id: str, data: dict = Body(...)):
    """Update production queue"""
    try:
        queue = await ProductionQueue.find_one({"queue_id": queue_id})
        
        if not queue:
            raise HTTPException(status_code=404, detail=f"Queue {queue_id} not found")
        
        # Update fields
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await queue.update({"$set": update_data})
        
        # Fetch updated queue
        updated_queue = await ProductionQueue.find_one({"queue_id": queue_id})
        
        if not updated_queue:
            raise HTTPException(status_code=404, detail="Queue not found after update")
        
        return {
            "success": True,
            "queue": updated_queue.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/queues/{queue_id}")
async def delete_production_queue(queue_id: str):
    """Delete production queue"""
    try:
        queue = await ProductionQueue.find_one({"queue_id": queue_id})
        
        if not queue:
            raise HTTPException(status_code=404, detail=f"Queue {queue_id} not found")
        
        # Also delete related breakdowns and crew sheets
        await SceneBreakdown.find({"queue_id": queue_id}).delete()
        await CrewSheet.find({"queue_id": queue_id}).delete()
        
        await queue.delete()
        
        return {
            "success": True,
            "message": f"Queue {queue_id} and related data deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Scene Breakdown Endpoints
# ============================================================================

@router.post("/breakdowns")
async def create_scene_breakdown(data: SceneBreakdownCreate):
    """
    Create scene breakdown (Part 2 of breakdown system)
    
    **Request Body:**
    - queue_id: Reference to production queue
    - scene_id: Reference to scene
    - scene_number: Scene number
    - shooting_time: Estimated shooting time (minutes)
    - location: Specific location
    - int_ext: INT/EXT
    - day_night: D/N
    - cast: Cast members in this scene
    - props: Props needed
    - And more...
    
    **Returns:** Created breakdown
    """
    try:
        # Generate breakdown_id
        breakdown_id = f"BD_{data.queue_id}_S{data.scene_number:03d}"
        
        breakdown = SceneBreakdown(
            breakdown_id=breakdown_id,
            **data.dict()
        )
        
        await breakdown.insert()
        
        return {
            "success": True,
            "breakdown_id": breakdown_id,
            "breakdown": breakdown.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakdowns")
async def list_scene_breakdowns(
    queue_id: Optional[str] = Query(None),
    scene_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List scene breakdowns with filters"""
    try:
        query = {}
        
        if queue_id:
            query["queue_id"] = queue_id
        if scene_id:
            query["scene_id"] = scene_id
        
        breakdowns = await SceneBreakdown.find(query).skip(skip).limit(limit).to_list()
        total = await SceneBreakdown.find(query).count()
        
        return {
            "success": True,
            "total": total,
            "breakdowns": [b.dict() for b in breakdowns]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakdowns/{breakdown_id}")
async def get_scene_breakdown(breakdown_id: str):
    """Get scene breakdown by ID"""
    try:
        breakdown = await SceneBreakdown.find_one({"breakdown_id": breakdown_id})
        
        if not breakdown:
            raise HTTPException(status_code=404, detail=f"Breakdown {breakdown_id} not found")
        
        return {
            "success": True,
            "breakdown": breakdown.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Crew Sheet Endpoints
# ============================================================================

@router.post("/crew-sheets")
async def create_crew_sheet(data: CrewSheetCreate):
    """
    Create crew sheet (Part 3 of breakdown system)
    
    **Request Body:**
    - queue_id: Reference to production queue
    - crew: List of crew members
    - actors: List of actors
    - equipment: Equipment needed
    - And more...
    
    **Returns:** Created crew sheet
    """
    try:
        # Generate sheet_id
        sheet_id = f"CS_{data.queue_id}"
        
        sheet = CrewSheet(
            sheet_id=sheet_id,
            **data.dict()
        )
        
        await sheet.insert()
        
        return {
            "success": True,
            "sheet_id": sheet_id,
            "crew_sheet": sheet.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crew-sheets/{queue_id}")
async def get_crew_sheet(queue_id: str):
    """Get crew sheet for a queue"""
    try:
        sheet = await CrewSheet.find_one({"queue_id": queue_id})
        
        if not sheet:
            raise HTTPException(status_code=404, detail=f"Crew sheet for queue {queue_id} not found")
        
        return {
            "success": True,
            "crew_sheet": sheet.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Props Inventory Endpoints
# ============================================================================

@router.post("/props")
async def create_prop(data: PropCreate):
    """
    Add prop to inventory
    
    **Request Body:**
    - project_id: Reference to project
    - name: Prop name
    - category: Prop category
    - quantity_needed: How many needed
    - source: Where to get it
    - And more...
    
    **Returns:** Created prop
    """
    try:
        # Generate prop_id
        existing_count = await PropsInventory.find({"project_id": data.project_id}).count()
        prop_id = f"PROP_{data.project_id}_{existing_count + 1:03d}"
        
        prop = PropsInventory(
            prop_id=prop_id,
            **data.dict()
        )
        
        await prop.insert()
        
        return {
            "success": True,
            "prop_id": prop_id,
            "prop": prop.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/props")
async def list_props(
    project_id: Optional[str] = Query(None),
    category: Optional[PropCategory] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List props with filters"""
    try:
        query = {}
        
        if project_id:
            query["project_id"] = project_id
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        
        props = await PropsInventory.find(query).skip(skip).limit(limit).to_list()
        total = await PropsInventory.find(query).count()
        
        return {
            "success": True,
            "total": total,
            "props": [p.dict() for p in props]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/props/{prop_id}")
async def get_prop(prop_id: str):
    """Get prop by ID"""
    try:
        prop = await PropsInventory.find_one({"prop_id": prop_id})
        
        if not prop:
            raise HTTPException(status_code=404, detail=f"Prop {prop_id} not found")
        
        return {
            "success": True,
            "prop": prop.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/props/{prop_id}")
async def update_prop(prop_id: str, data: dict = Body(...)):
    """Update prop"""
    try:
        prop = await PropsInventory.find_one({"prop_id": prop_id})
        
        if not prop:
            raise HTTPException(status_code=404, detail=f"Prop {prop_id} not found")
        
        # Update fields
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await prop.update({"$set": update_data})
        
        # Fetch updated prop
        updated_prop = await PropsInventory.find_one({"prop_id": prop_id})
        
        if not updated_prop:
            raise HTTPException(status_code=404, detail="Prop not found after update")
        
        return {
            "success": True,
            "prop": updated_prop.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Analytics & Reports
# ============================================================================

@router.get("/queues/{queue_id}/summary")
async def get_queue_summary(queue_id: str):
    """
    Get complete summary for a production queue
    
    Includes:
    - Queue details
    - All scene breakdowns
    - Crew sheet
    - Consolidated props/equipment lists
    
    **Returns:** Complete production package for the queue
    """
    try:
        # Get queue
        queue = await ProductionQueue.find_one({"queue_id": queue_id})
        if not queue:
            raise HTTPException(status_code=404, detail=f"Queue {queue_id} not found")
        
        # Get breakdowns
        breakdowns = await SceneBreakdown.find({"queue_id": queue_id}).to_list()
        
        # Get crew sheet
        crew_sheet = await CrewSheet.find_one({"queue_id": queue_id})
        
        # Consolidate props from all breakdowns
        all_props = {}
        for bd in breakdowns:
            for prop in bd.props:
                # PropItem is a BaseModel, use attribute access
                prop_name = prop.name
                if prop_name in all_props:
                    all_props[prop_name]["quantity"] += (prop.quantity or 1)
                else:
                    all_props[prop_name] = prop.dict()
        
        # Calculate totals
        total_shooting_time = sum(bd.shooting_time for bd in breakdowns)
        total_scenes = len(breakdowns)
        
        return {
            "success": True,
            "queue": queue.dict(),
            "breakdowns": [bd.dict() for bd in breakdowns],
            "crew_sheet": crew_sheet.dict() if crew_sheet else None,
            "consolidated_props": list(all_props.values()),
            "summary": {
                "total_scenes": total_scenes,
                "total_shooting_time_minutes": total_shooting_time,
                "estimated_hours": round(total_shooting_time / 60, 1),
                "total_props": len(all_props)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/production-report")
async def get_production_report(project_id: str):
    """
    Generate complete production report for a project
    
    Includes:
    - All queues
    - All breakdowns
    - Complete props inventory
    - Budget summary
    
    **Returns:** Complete production report
    """
    try:
        # Get all queues for project
        queues = await ProductionQueue.find({"project_id": project_id}).to_list()
        
        # Get all props for project
        props = await PropsInventory.find({"project_id": project_id}).to_list()
        
        # Calculate budget
        total_props_cost = sum(p.cost_estimate or 0 for p in props)
        
        # Calculate crew/equipment budget
        total_queue_budget = 0.0
        for q in queues:
            sheet = await CrewSheet.find_one({"queue_id": q.queue_id})
            if sheet and sheet.estimated_budget:
                total_queue_budget += sheet.estimated_budget
        
        return {
            "success": True,
            "project_id": project_id,
            "total_queues": len(queues),
            "queues": [q.dict() for q in queues],
            "props_inventory": [p.dict() for p in props],
            "budget_summary": {
                "props_cost": total_props_cost,
                "crew_equipment_budget": total_queue_budget,
                "total_estimated": total_props_cost + total_queue_budget
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def production_health_check():
    """Health check endpoint"""
    try:
        queue_count = await ProductionQueue.find({}).count()
        breakdown_count = await SceneBreakdown.find({}).count()
        props_count = await PropsInventory.find({}).count()
        
        return {
            "status": "healthy",
            "service": "Production Management System",
            "version": "1.0",
            "collections": {
                "queues": queue_count,
                "breakdowns": breakdown_count,
                "props": props_count
            }
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
