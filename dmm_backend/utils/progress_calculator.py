"""
Project Progress Calculator Helper

Calculates project completion progress based on scenes and shots

Author: Peace Script Team
Date: 26 October 2025
Version: 1.0
"""

from documents_narrative import Project, Scene, Shot
from typing import Optional


async def calculate_project_progress(project_id: str) -> float:
    """
    Calculate project progress percentage
    
    Logic:
    - A scene is considered "complete" if it has at least 1 shot
    - Progress = (completed scenes / total scenes) * 100
    - If no scenes, return 0%
    
    Args:
        project_id: Project ID to calculate progress for
        
    Returns:
        Progress percentage (0.0 - 100.0)
    """
    try:
        # Get all scenes in project
        all_scenes = await Scene.find({"project_id": project_id}).to_list()
        
        if not all_scenes:
            return 0.0
        
        total_scenes = len(all_scenes)
        completed_scenes = 0
        
        # Check each scene for shots
        for scene in all_scenes:
            scene_id = str(scene.id)
            # A scene is complete if it has at least 1 shot
            shots_count = await Shot.find({"scene_id": scene_id}).count()
            if shots_count > 0:
                completed_scenes += 1
        
        # Calculate percentage
        progress = (completed_scenes / total_scenes) * 100.0
        
        return round(progress, 2)
        
    except Exception as e:
        print(f"Error calculating progress: {e}")
        return 0.0


async def update_project_progress(project_id: str) -> Optional[float]:
    """
    Update project progress in database
    
    Args:
        project_id: Project ID to update
        
    Returns:
        New progress value or None if failed
    """
    try:
        project = await Project.find_one({"project_id": project_id})
        if not project:
            return None
        
        new_progress = await calculate_project_progress(project_id)
        
        project.progress = new_progress
        await project.save()
        
        return new_progress
        
    except Exception as e:
        print(f"Error updating project progress: {e}")
        return None
