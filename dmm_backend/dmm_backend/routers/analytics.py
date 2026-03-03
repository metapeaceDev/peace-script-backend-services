from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from documents import KammaLogEntry
from core.security import get_api_key
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_api_key)],
)


# ===== Request/Response Models =====

class AnalyticsOverviewResponse(BaseModel):
    """Overview analytics with pie chart data"""
    total_items: int = Field(..., description="Total items count")
    categories: Dict[str, int] = Field(..., description="Category distribution")
    trend: str = Field(..., description="Trend indicator (up/down/stable)")
    pie_data: List[Dict[str, Any]] = Field(..., description="Data for pie chart")
    summary: str = Field(..., description="Summary text")


class AnalyticsTimelineResponse(BaseModel):
    """Timeline analytics with bar chart data"""
    timeline: List[Dict[str, Any]] = Field(..., description="Timeline data points")
    date_range: Dict[str, str] = Field(..., description="Start and end dates")
    bar_data: List[Dict[str, Any]] = Field(..., description="Data for bar chart")


class AnalyticsHeatmapResponse(BaseModel):
    """Heatmap analytics data"""
    heatmap: List[Dict[str, Any]] = Field(..., description="Heatmap data")
    x_labels: List[str] = Field(..., description="X-axis labels")
    y_labels: List[str] = Field(..., description="Y-axis labels")
    max_value: float = Field(..., description="Maximum value for scale")


class ExportAnalyticsRequest(BaseModel):
    """Request for analytics export"""
    format: str = Field("json", description="Export format (json/csv/pdf)")
    include_charts: bool = Field(True, description="Include chart data")
    date_from: Optional[str] = Field(None, description="Start date (ISO format)")
    date_to: Optional[str] = Field(None, description="End date (ISO format)")


# ===== Existing Endpoints =====

@router.get("/kamma/by_status", response_model=Dict[str, int])
async def kamma_by_status(model_id: str):
    """Aggregate Kamma logs grouped by event_type for a model."""
    logs: List[KammaLogEntry] = await KammaLogEntry.find(KammaLogEntry.model_id == model_id).to_list()
    result: Dict[str, int] = {}
    for log in logs:
        key = getattr(log, "event_type", "unknown")
        result[key] = result.get(key, 0) + 1
    return result


@router.get("/kamma/detail", response_model=List[Dict])
async def kamma_detail(model_id: str):
    """Return raw Kamma logs for a model (basic detail view)."""
    logs = await KammaLogEntry.find(KammaLogEntry.model_id == model_id).sort("-timestamp").to_list()
    serialized = []
    for log in logs:
        serialized.append({
            "_id": str(getattr(log, "id", "")),
            "model_id": log.model_id,
            "timestamp": log.timestamp.isoformat() if getattr(log, "timestamp", None) else None,
            "event_type": getattr(log, "event_type", None),
            "description": getattr(log, "description", None),
            "impact_level": getattr(log, "impact_level", None),
            "context": getattr(log, "context", {}),
        })
    return serialized


# ===== New Analytics Endpoints =====

@router.get("/project/{project_id}/overview", response_model=AnalyticsOverviewResponse)
async def get_project_overview(
    project_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get project overview analytics with pie chart data.
    
    Analyzes:
    - Total items (kamma logs, events, etc.)
    - Category distribution
    - Trend analysis
    - Pie chart data for visualization
    """
    try:
        # Get kamma logs for project
        logs = await KammaLogEntry.find(
            KammaLogEntry.model_id == project_id
        ).to_list()
        
        # Calculate category distribution
        categories = {}
        for log in logs:
            event_type = getattr(log, "event_type", "unknown")
            categories[event_type] = categories.get(event_type, 0) + 1
        
        # Prepare pie chart data
        pie_data = [
            {
                "name": category,
                "value": count,
                "percentage": round((count / len(logs) * 100), 2) if logs else 0
            }
            for category, count in categories.items()
        ]
        
        # Calculate trend (simple: compare recent vs older)
        if len(logs) >= 10:
            recent_count = len([l for l in logs[:len(logs)//2]])
            older_count = len([l for l in logs[len(logs)//2:]])
            trend = "up" if recent_count > older_count else "down" if recent_count < older_count else "stable"
        else:
            trend = "stable"
        
        return AnalyticsOverviewResponse(
            total_items=len(logs),
            categories=categories,
            trend=trend,
            pie_data=pie_data,
            summary=f"Total {len(logs)} items across {len(categories)} categories"
        )
        
    except Exception as e:
        logger.error(f"Error getting project overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}/timeline", response_model=AnalyticsTimelineResponse)
async def get_project_timeline(
    project_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    group_by: str = Query("day", description="Group by: day, week, month")
):
    """
    Get project timeline analytics with bar chart data.
    
    Returns timeline data grouped by day/week/month for bar chart visualization.
    """
    try:
        # Get logs within date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logs = await KammaLogEntry.find(
            KammaLogEntry.model_id == project_id
        ).to_list()
        
        # Filter by date
        filtered_logs = [
            log for log in logs 
            if hasattr(log, 'timestamp') and log.timestamp and 
            start_date <= log.timestamp <= end_date
        ]
        
        # Group by period
        timeline_data = {}
        for log in filtered_logs:
            if group_by == "day":
                key = log.timestamp.strftime("%Y-%m-%d")
            elif group_by == "week":
                key = log.timestamp.strftime("%Y-W%W")
            else:  # month
                key = log.timestamp.strftime("%Y-%m")
            
            if key not in timeline_data:
                timeline_data[key] = {"date": key, "count": 0, "types": {}}
            
            timeline_data[key]["count"] += 1
            event_type = getattr(log, "event_type", "unknown")
            timeline_data[key]["types"][event_type] = timeline_data[key]["types"].get(event_type, 0) + 1
        
        # Convert to list and sort
        timeline_list = sorted(timeline_data.values(), key=lambda x: x["date"])
        
        # Prepare bar chart data
        bar_data = [
            {
                "period": item["date"],
                "total": item["count"],
                **item["types"]  # Spread types as separate bars
            }
            for item in timeline_list
        ]
        
        return AnalyticsTimelineResponse(
            timeline=timeline_list,
            date_range={
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            bar_data=bar_data
        )
        
    except Exception as e:
        logger.error(f"Error getting project timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}/heatmap", response_model=AnalyticsHeatmapResponse)
async def get_project_heatmap(
    project_id: str,
    metric: str = Query("activity", description="Metric to visualize: activity, intensity, impact")
):
    """
    Get project heatmap analytics.
    
    Returns heatmap data showing activity/intensity patterns by day and hour.
    """
    try:
        logs = await KammaLogEntry.find(
            KammaLogEntry.model_id == project_id
        ).to_list()
        
        # Initialize heatmap grid (7 days x 24 hours)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = [f"{h:02d}:00" for h in range(24)]
        heatmap_grid = [[0 for _ in range(24)] for _ in range(7)]
        
        # Fill heatmap
        for log in logs:
            if hasattr(log, 'timestamp') and log.timestamp:
                day_idx = log.timestamp.weekday()  # 0=Monday
                hour_idx = log.timestamp.hour
                
                if metric == "activity":
                    heatmap_grid[day_idx][hour_idx] += 1
                elif metric == "intensity":
                    intensity = getattr(log, "impact_level", 1)
                    heatmap_grid[day_idx][hour_idx] += intensity
                elif metric == "impact":
                    impact = abs(getattr(log, "impact_level", 1))
                    heatmap_grid[day_idx][hour_idx] += impact
        
        # Find max value for scale
        max_value = max(max(row) for row in heatmap_grid) if heatmap_grid else 1
        
        # Convert to heatmap data format
        heatmap_data = []
        for day_idx, day in enumerate(days):
            for hour_idx, hour in enumerate(hours):
                heatmap_data.append({
                    "day": day,
                    "hour": hour,
                    "value": heatmap_grid[day_idx][hour_idx],
                    "normalized": round(heatmap_grid[day_idx][hour_idx] / max_value, 3) if max_value > 0 else 0
                })
        
        return AnalyticsHeatmapResponse(
            heatmap=heatmap_data,
            x_labels=hours,
            y_labels=days,
            max_value=max_value
        )
        
    except Exception as e:
        logger.error(f"Error getting project heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/{project_id}/export")
async def export_project_analytics(
    project_id: str,
    request: ExportAnalyticsRequest
):
    """
    Export project analytics in various formats.
    
    Supports JSON, CSV, and PDF formats with optional chart data.
    """
    try:
        # Get all analytics data
        overview = await get_project_overview(project_id)
        timeline = await get_project_timeline(project_id)
        heatmap = await get_project_heatmap(project_id)
        
        if request.format == "json":
            export_data = {
                "project_id": project_id,
                "exported_at": datetime.utcnow().isoformat(),
                "overview": overview.model_dump() if request.include_charts else {"total_items": overview.total_items},
                "timeline": timeline.model_dump() if request.include_charts else {"date_range": timeline.date_range},
                "heatmap": heatmap.model_dump() if request.include_charts else {"max_value": heatmap.max_value}
            }
            return {
                "success": True,
                "format": "json",
                "data": export_data
            }
        
        elif request.format == "csv":
            # Simple CSV format for timeline data
            csv_data = "date,count,type\n"
            for item in timeline.timeline:
                for type_name, count in item.get("types", {}).items():
                    csv_data += f"{item['date']},{count},{type_name}\n"
            
            return {
                "success": True,
                "format": "csv",
                "data": csv_data,
                "filename": f"analytics_{project_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        
        elif request.format == "pdf":
            # Placeholder for PDF generation
            return {
                "success": True,
                "format": "pdf",
                "message": "PDF export will be implemented with reportlab library",
                "data": {
                    "project_id": project_id,
                    "total_items": overview.total_items,
                    "date_range": timeline.date_range
                }
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
