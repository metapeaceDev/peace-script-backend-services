"""
Simulation Clusters Router - Cluster Management & Batch Analytics
=================================================================
ตามแผน Peace Script V.14 - Step 2.2.48-50, 2.2.84-85

Router นี้จัดการ:
- CRUD operations สำหรับ Clusters
- Batch analytics (aggregate karma, health, outcomes)
- Scenario grouping (จัดกลุ่ม scenarios เพื่อเปรียบเทียบ)
- Export cluster data (PDF, CSV, JSON)

Routes:
    POST   /api/v1/simulation-clusters/              - สร้าง cluster ใหม่
    GET    /api/v1/simulation-clusters/              - List clusters
    GET    /api/v1/simulation-clusters/{id}          - Get cluster by ID
    PATCH  /api/v1/simulation-clusters/{id}          - Update cluster
    DELETE /api/v1/simulation-clusters/{id}          - Delete cluster
    POST   /api/v1/simulation-clusters/{id}/scenarios - Add scenarios to cluster
    GET    /api/v1/simulation-clusters/{id}/analytics - Get cluster analytics
    POST   /api/v1/simulation-clusters/{id}/export    - Export cluster data
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from documents_simulation import SimulationCluster
from schemas_simulation import (
    ClusterCreate,
    ClusterUpdate,
    ClusterResponse,
    ClusterAnalyticsResponse,
    ExportRequest,
    ExportResponse
)

router = APIRouter(prefix="/api/v1/simulation-clusters", tags=["Simulation Clusters"])


@router.post("/", response_model=ClusterResponse, status_code=status.HTTP_201_CREATED)
async def create_cluster(cluster_data: ClusterCreate) -> ClusterResponse:
    """
    สร้าง Simulation Cluster ใหม่
    
    Args:
        cluster_data: ข้อมูล cluster (title, scenario_ids, etc.)
        
    Returns:
        ClusterResponse: Cluster ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "title": "Karma Comparison Study",
            "description": "Compare different dana scenarios",
            "scenario_ids": ["SC-001", "SC-002", "SC-003"]
        }
        ```
    """
    try:
        cluster = SimulationCluster(
            title=cluster_data.title,
            description=cluster_data.description,
            scenario_ids=cluster_data.scenario_ids or [],
            chain_ids=cluster_data.chain_ids or [],
            teaching_pack_id=getattr(cluster_data, 'teaching_pack_id', None),
            dhamma_themes=getattr(cluster_data, 'dhamma_themes', []),
            meta_log=getattr(cluster_data, 'meta_info', {})  # ✅ ใช้ getattr เพื่อ handle optional field
        )
        
        await cluster.insert()
        
        return ClusterResponse.model_validate(cluster)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create cluster: {str(e)}"
        )


@router.get("/", response_model=List[ClusterResponse])
async def list_clusters(
    search: Optional[str] = Query(None, description="Search in title/description"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[ClusterResponse]:
    """
    List Simulation Clusters
    
    Query Parameters:
        - search: full-text search
        - limit, skip: pagination
        
    Returns:
        List[ClusterResponse]: รายการ clusters
    """
    try:
        query = {}
        
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        clusters = await SimulationCluster.find(query).skip(skip).limit(limit).to_list()
        
        return [ClusterResponse.model_validate(c) for c in clusters]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list clusters: {str(e)}"
        )


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: str) -> ClusterResponse:
    """
    Get Cluster by ID
    
    Args:
        cluster_id: CL-xxxxx
        
    Returns:
        ClusterResponse: Cluster data พร้อม scenarios, analytics
    """
    try:
        cluster = await SimulationCluster.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        return ClusterResponse.model_validate(cluster)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cluster: {str(e)}"
        )


@router.patch("/{cluster_id}", response_model=ClusterResponse)
async def update_cluster(cluster_id: str, update_data: ClusterUpdate) -> ClusterResponse:
    """
    Update Cluster
    
    Args:
        cluster_id: CL-xxxxx
        update_data: ข้อมูลที่ต้องการอัปเดต
        
    Returns:
        ClusterResponse: Cluster ที่อัปเดตแล้ว
    """
    try:
        cluster = await SimulationCluster.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        update_dict = update_data.model_dump(exclude_none=True)
        
        for field, value in update_dict.items():
            setattr(cluster, field, value)
        
        cluster.updated_at = datetime.utcnow()
        await cluster.save()
        
        return ClusterResponse.model_validate(cluster)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cluster: {str(e)}"
        )


@router.delete("/{cluster_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cluster(cluster_id: str):
    """
    Delete Cluster
    
    Args:
        cluster_id: CL-xxxxx
        
    Note:
        - ลบ cluster (scenarios ยังคงอยู่)
    """
    try:
        cluster = await SimulationCluster.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        await cluster.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete cluster: {str(e)}"
        )


@router.post("/{cluster_id}/scenarios", response_model=ClusterResponse)
async def add_scenarios_to_cluster(
    cluster_id: str,
    scenario_ids: List[str]
) -> ClusterResponse:
    """
    Add Scenarios to Cluster
    
    Args:
        cluster_id: CL-xxxxx
        scenario_ids: List of SC-xxxxx to add
        
    Returns:
        ClusterResponse: Updated cluster
        
    Example:
        ```json
        ["SC-001", "SC-002", "SC-003"]
        ```
    """
    try:
        cluster = await SimulationCluster.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        # Add unique scenario_ids
        for scenario_id in scenario_ids:
            if scenario_id not in cluster.scenario_ids:
                cluster.scenario_ids.append(scenario_id)
        
        cluster.updated_at = datetime.utcnow()
        await cluster.save()
        
        return ClusterResponse.model_validate(cluster)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add scenarios: {str(e)}"
        )


@router.get("/{cluster_id}/analytics", response_model=ClusterAnalyticsResponse)
async def get_cluster_analytics(cluster_id: str) -> ClusterAnalyticsResponse:
    """
    Get Cluster Analytics
    
    Args:
        cluster_id: CL-xxxxx
        
    Returns:
        ClusterAnalyticsResponse: Aggregate karma, health, emotion, outcome distribution
        
    Process:
        - Aggregate metrics จาก scenarios
        - Calculate outcome distribution
        - Generate insights
    """
    try:
        cluster = await SimulationCluster.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        # Fetch scenarios และคำนวณ analytics จริง
        from documents import SimulationHistory
        
        # Get all simulation results for scenarios in this cluster
        scenarios_data = []
        total_karma = 0.0
        total_health = 0.0
        total_emotion = 0.0
        outcome_counts = {"kusala": 0, "akusala": 0, "neutral": 0}
        
        for scenario_id in cluster.scenario_ids:
            # Query simulations for this scenario
            simulations = await SimulationHistory.find({
                "scenario_id": scenario_id
            }).to_list()
            
            if simulations:
                # Calculate average metrics for this scenario
                scenario_karma = sum(s.kamma_generated for s in simulations if hasattr(s, 'kamma_generated')) / len(simulations) if simulations else 0.0
                scenario_health = sum(s.virtue_change for s in simulations if hasattr(s, 'virtue_change')) / len(simulations) if simulations else 0.0
                
                # Count choice types
                for sim in simulations:
                    if hasattr(sim, 'choice_type'):
                        choice_type = sim.choice_type
                        if choice_type in outcome_counts:
                            outcome_counts[choice_type] += 1
                
                scenarios_data.append({
                    "scenario_id": scenario_id,
                    "simulation_count": len(simulations),
                    "avg_karma": scenario_karma,
                    "avg_health": scenario_health
                })
                
                total_karma += scenario_karma * len(simulations)
                total_health += scenario_health * len(simulations)
        
        # Calculate aggregates
        total_simulations = sum(s["simulation_count"] for s in scenarios_data)
        aggregate_karma = total_karma / total_simulations if total_simulations > 0 else 0.0
        aggregate_health = total_health / total_simulations if total_simulations > 0 else 0.0
        aggregate_emotion = (aggregate_health + aggregate_karma) / 2.0  # Simplified emotion calculation
        
        # Update cluster with calculated values
        cluster.aggregate_karma = aggregate_karma
        cluster.aggregate_health = aggregate_health
        cluster.emotion_avg = aggregate_emotion
        
        # Calculate outcome distribution percentages
        total_outcomes = sum(outcome_counts.values())
        if total_outcomes > 0:
            cluster.outcome_distribution = {
                "kusala": round((outcome_counts["kusala"] / total_outcomes) * 100, 1),
                "akusala": round((outcome_counts["akusala"] / total_outcomes) * 100, 1),
                "neutral": round((outcome_counts["neutral"] / total_outcomes) * 100, 1)
            }
        
        await cluster.save()
        
        # Generate insights
        insights = [
            f"Cluster contains {len(cluster.scenario_ids)} scenarios",
            f"Total simulations analyzed: {total_simulations}",
            f"Aggregate karma: {aggregate_karma:.2f}",
            f"Average health: {aggregate_health:.2f}",
            f"Average emotion: {aggregate_emotion:.2f}"
        ]
        
        if cluster.aggregate_karma > 0:
            insights.append("Overall positive karma trend")
        elif cluster.aggregate_karma < 0:
            insights.append("Overall negative karma - review scenarios")
        
        return ClusterAnalyticsResponse(
            cluster_id=cluster.cluster_id,
            aggregate_karma=cluster.aggregate_karma,
            aggregate_health=cluster.aggregate_health,
            emotion_avg=cluster.emotion_avg,
            outcome_distribution=cluster.outcome_distribution,
            comparison_matrix=cluster.comparison_matrix,
            insights=insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cluster analytics: {str(e)}"
        )


@router.post("/{cluster_id}/export", response_model=ExportResponse)
async def export_cluster(cluster_id: str, export_request: ExportRequest) -> ExportResponse:
    """
    Export Cluster Data
    
    Args:
        cluster_id: CL-xxxxx
        export_request: format (json, csv, pdf), include_analytics
        
    Returns:
        ExportResponse: export_url, filename, format
        
    Example:
        ```json
        {
            "format": "pdf",
            "include_analytics": true,
            "include_scenarios": true
        }
        ```
    """
    try:
        cluster = await SimulationCluster.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        # Implement actual export logic
        import json
        from pathlib import Path
        
        # Create exports directory if not exists
        export_dir = Path("exports/clusters")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        format_type = getattr(export_request, 'format', 'json')
        filename = f"cluster-{cluster_id}-{timestamp}.{format_type}"
        filepath = export_dir / filename
        
        # Prepare export data
        export_data = {
            "cluster_id": cluster.cluster_id,
            "name": cluster.name,
            "description": cluster.description,
            "created_at": cluster.created_at.isoformat() if cluster.created_at else None,
            "updated_at": cluster.updated_at.isoformat() if cluster.updated_at else None,
            "scenario_ids": cluster.scenario_ids,
            "analytics": {
                "aggregate_karma": cluster.aggregate_karma,
                "aggregate_health": cluster.aggregate_health,
                "emotion_avg": cluster.emotion_avg,
                "outcome_distribution": cluster.outcome_distribution,
            } if getattr(export_request, 'include_analytics', True) else None
        }
        
        # Add scenarios data if requested
        if getattr(export_request, 'include_scenarios', False):
            from documents import SimulationHistory
            scenarios_detail = []
            
            for scenario_id in cluster.scenario_ids:
                simulations = await SimulationHistory.find({
                    "scenario_id": scenario_id
                }).to_list()
                
                scenarios_detail.append({
                    "scenario_id": scenario_id,
                    "simulation_count": len(simulations),
                    "simulations": [
                        {
                            "simulation_id": s.simulation_id,
                            "timestamp": s.timestamp.isoformat() if hasattr(s, 'timestamp') else None,
                            "choice_type": s.choice_type if hasattr(s, 'choice_type') else None,
                            "kamma_generated": s.kamma_generated if hasattr(s, 'kamma_generated') else 0.0
                        }
                        for s in simulations[:10]  # Limit to 10 most recent
                    ]
                })
            
            export_data["scenarios"] = scenarios_detail
        
        # Export based on format
        if format_type == "json":
            # JSON export
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        elif format_type == "csv":
            # CSV export (simplified)
            import csv
            csv_filepath = export_dir / f"cluster-{cluster_id}-{timestamp}.csv"
            
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Cluster ID', 'Name', 'Aggregate Karma', 'Aggregate Health', 'Emotion Avg'])
                writer.writerow([
                    cluster.cluster_id,
                    cluster.name,
                    cluster.aggregate_karma,
                    cluster.aggregate_health,
                    cluster.emotion_avg
                ])
                
                if cluster.scenario_ids:
                    writer.writerow([])
                    writer.writerow(['Scenario IDs'])
                    for sid in cluster.scenario_ids:
                        writer.writerow([sid])
            
            filepath = csv_filepath
            
        elif format_type == "pdf":
            # PDF export (basic text-based)
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                pdf_filepath = export_dir / f"cluster-{cluster_id}-{timestamp}.pdf"
                c = canvas.Canvas(str(pdf_filepath), pagesize=letter)
                
                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(100, 750, f"Cluster Report: {cluster.name}")
                
                # Content
                c.setFont("Helvetica", 12)
                y = 700
                c.drawString(100, y, f"Cluster ID: {cluster.cluster_id}")
                y -= 20
                c.drawString(100, y, f"Description: {cluster.description}")
                y -= 30
                c.drawString(100, y, "Analytics:")
                y -= 20
                c.drawString(120, y, f"Aggregate Karma: {cluster.aggregate_karma:.2f}")
                y -= 20
                c.drawString(120, y, f"Aggregate Health: {cluster.aggregate_health:.2f}")
                y -= 20
                c.drawString(120, y, f"Emotion Average: {cluster.emotion_avg:.2f}")
                y -= 30
                c.drawString(100, y, f"Scenarios: {len(cluster.scenario_ids)}")
                
                c.save()
                filepath = pdf_filepath
                
            except ImportError:
                # Fallback to text file if reportlab not available
                txt_filepath = export_dir / f"cluster-{cluster_id}-{timestamp}.txt"
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Cluster Report: {cluster.name}\n")
                    f.write(f"{'='*50}\n\n")
                    f.write(f"Cluster ID: {cluster.cluster_id}\n")
                    f.write(f"Description: {cluster.description}\n\n")
                    f.write(f"Analytics:\n")
                    f.write(f"  Aggregate Karma: {cluster.aggregate_karma:.2f}\n")
                    f.write(f"  Aggregate Health: {cluster.aggregate_health:.2f}\n")
                    f.write(f"  Emotion Average: {cluster.emotion_avg:.2f}\n\n")
                    f.write(f"Scenarios ({len(cluster.scenario_ids)}):\n")
                    for sid in cluster.scenario_ids:
                        f.write(f"  - {sid}\n")
                filepath = txt_filepath
                format_type = "txt"
        
        # Generate accessible URL (relative path)
        export_url = f"/exports/clusters/{filepath.name}"
        
        filename = f"cluster-{cluster_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.{export_request.format}"
        export_url = f"/exports/{filename}"
        
        return ExportResponse(
            export_url=export_url,
            filename=filename,
            format=export_request.format,
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export cluster: {str(e)}"
        )
