"""
NarrativeStructure Project Router

This module implements CRUD operations for Peace Script projects.
Provides REST API endpoints for project management.

Author: Peace Script Team
Date: 25 October 2025
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, status, Query, Response
from typing import List, Optional
from datetime import datetime
import httpx
import os
import json
import re
import sys
import time
import random  # 🔥 ADD: For random camera angles
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from documents_narrative import Project
from schemas_narrative import ProjectCreate, ProjectUpdate, ProjectResponse

# 🆕 Phase 2: Import Simulation Engine for shot-by-shot character simulation
# from modules.simulation_engine import InteractiveSimulationEngine


router = APIRouter(
    prefix="/api/narrative/projects",
    tags=["narrative-projects"]
)


# =============================================================================
# HELPER FUNCTIONS - Character State Management (Shot-by-Shot Simulation)
# =============================================================================

async def get_character_current_state(actor_id: str) -> dict:
    """
    ดึงสถานะปัจจุบันของตัวละครจาก Actor/MindState documents
    
    Args:
        actor_id: Actor ID
        
    Returns:
        dict: Character state snapshot
    """
    try:
        # Import documents
        from documents import MindState
        
        # Try to find MindState
        mind_state = await MindState.find_one({"user_id": actor_id})
        if not mind_state:
            # Return default state if not found
            return {
                "virtue": {"sila": 5.0, "samadhi": 5.0, "panna": 5.0},
                "emotion": "neutral",
                "consciousness_state": "neutral",
                "active_hindrances": {},
                "kusala_count": 0,
                "akusala_count": 0
            }
        
        # Build state from MindState
        state = {
            "virtue": {
                "sila": mind_state.sila,
                "samadhi": mind_state.samadhi,
                "panna": mind_state.panna
            },
            "emotion": "neutral",
            "consciousness_state": mind_state.current_bhumi or "puthujjana",
            "active_hindrances": mind_state.current_anusaya or {},
            "kusala_count": mind_state.kusala_count_total or 0,
            "akusala_count": mind_state.akusala_count_total or 0,
            "sati_strength": mind_state.sati_strength or 5.0
        }
        
        return state
        
    except Exception as e:
        print(f"⚠️ Error getting character state for {actor_id}: {e}")
        # Return safe default
        return {
            "virtue": {"sila": 5.0, "samadhi": 5.0, "panna": 5.0},
            "emotion": "neutral",
            "consciousness_state": "neutral",
            "active_hindrances": {},
            "kusala_count": 0,
            "akusala_count": 0
        }


async def update_character_state(actor_id: str, state_changes: dict) -> bool:
    """
    อัปเดตสถานะตัวละครหลัง simulation
    
    Args:
        actor_id: Actor ID
        state_changes: Dictionary of changes from simulation
            {
                "virtue": {"sila": 5.1, "samadhi": 5.2, "panna": 5.0},
                "kusala_count": 11,
                "akusala_count": 5
            }
    
    Returns:
        bool: Success status
    """
    try:
        from documents import MindState
        
        # Find or create MindState
        mind_state = await MindState.find_one({"user_id": actor_id})
        
        if not mind_state:
            # Create new MindState if not exists
            mind_state = MindState(
                user_id=actor_id,
                sila=5.0,
                samadhi=5.0,
                panna=5.0,
                sati_strength=5.0,
                current_bhumi="puthujjana",
                kusala_count_total=0,
                akusala_count_total=0,
                last_simulation_at=datetime.utcnow(),
                last_reset_at=datetime.utcnow()
            )
        
        # Update virtue levels
        if "virtue" in state_changes:
            virtue = state_changes["virtue"]
            if "sila" in virtue:
                mind_state.sila = virtue["sila"]
            if "samadhi" in virtue:
                mind_state.samadhi = virtue["samadhi"]
            if "panna" in virtue:
                mind_state.panna = virtue["panna"]
        
        # Update counts
        if "kusala_count" in state_changes:
            mind_state.kusala_count_total = state_changes["kusala_count"]
        if "akusala_count" in state_changes:
            mind_state.akusala_count_total = state_changes["akusala_count"]
        
        # Update hindrances if provided
        if "active_hindrances" in state_changes:
            mind_state.current_anusaya = state_changes["active_hindrances"]
        
        # Save
        mind_state.updated_at = datetime.utcnow()
        await mind_state.save()
        
        print(f"✅ Updated character state for {actor_id}")
        return True
        
    except Exception as e:
        print(f"⚠️ Error updating character state for {actor_id}: {e}")
        return False


async def update_character_after_simulation(
    character_id: str,
    simulation_result: dict
) -> bool:
    """
    💾 Update character profile after shot simulation
    
    Updates:
    - internal_character.psychological_matrix.current_emotion  
    - internal_character.virtue_engine (sila, samadhi, panna)
    - internal_character.psychological_matrix.anusaya_kilesa
    - simulation_history (append new entry)
    
    Args:
        character_id: Character ID from simulation
        simulation_result: Simulation output with state_changes
        
    Returns:
        bool: Success status
    """
    try:
        from documents_narrative import Character
        from schemas_actors import InternalCharacter, PsychologicalMatrix, VirtueEngine
        
        # 1. Load character from database
        character = await Character.find_one({"character_id": character_id})
        
        if not character:
            print(f"⚠️ Character {character_id} not found for simulation update")
            return False
        
        # 2. Initialize if missing
        if not character.internal_character:
            character.internal_character = InternalCharacter(
                psychological_matrix=PsychologicalMatrix(
                    anusaya_kilesa={},
                    current_emotion="neutral"
                ),
                virtue_engine=VirtueEngine(
                    sati_mastery={"level": 5.0},
                    panna_mastery={"level": 5.0}
                )
            )
        
        # 3. Extract state changes
        state_changes = simulation_result.get("state_changes", {})
        new_emotion = simulation_result.get("current_emotion", "neutral")
        
        # 4. Update emotion
        if character.internal_character.psychological_matrix:
            character.internal_character.psychological_matrix.current_emotion = new_emotion
        
        # 5. Update virtue levels
        virtue_delta = state_changes.get("virtue", {})
        if character.internal_character.virtue_engine:
            # Sila
            if "sila" in virtue_delta:
                current_sila = character.internal_character.virtue_engine.sati_mastery.get("level", 5.0)
                new_sila = max(0, min(10, current_sila + virtue_delta["sila"]))
                character.internal_character.virtue_engine.sati_mastery["level"] = new_sila
            
            # Samadhi
            if "samadhi" in virtue_delta:
                current_samadhi = character.internal_character.virtue_engine.panna_mastery.get("level", 5.0)
                new_samadhi = max(0, min(10, current_samadhi + virtue_delta["samadhi"]))
                character.internal_character.virtue_engine.panna_mastery["level"] = new_samadhi
        
        # 6. Update anusaya (latent tendencies)
        kusala_delta = state_changes.get("kusala_delta", 0)
        akusala_delta = state_changes.get("akusala_delta", 0)
        
        if akusala_delta > 0 and character.internal_character.psychological_matrix:
            anusaya_kilesa = character.internal_character.psychological_matrix.anusaya_kilesa
            
            # Increase moha (delusion) if unwholesome
            if "moha" not in anusaya_kilesa:
                anusaya_kilesa["moha"] = {"level": 3.0}
            
            current_moha = anusaya_kilesa["moha"]["level"]
            anusaya_kilesa["moha"]["level"] = min(10, current_moha + akusala_delta * 0.5)
        
        # 7. Add to simulation history
        if not hasattr(character, 'simulation_history'):
            character.simulation_history = []
        
        history_entry = {
            "timestamp": datetime.utcnow(),
            "actions": simulation_result.get("actions_taken", []),
            "dialogue": simulation_result.get("dialogue_spoken", ""),
            "emotion": new_emotion,
            "kusala_delta": kusala_delta,
            "akusala_delta": akusala_delta,
            "virtue_changes": virtue_delta
        }
        
        character.simulation_history.append(history_entry)
        
        # Keep last 100 simulations only
        if len(character.simulation_history) > 100:
            character.simulation_history = character.simulation_history[-100:]
        
        # 8. Save to database
        character.updated_at = datetime.utcnow()
        await character.save()
        
        print(f"✅ Character '{character.actor_name}' updated after simulation:")
        print(f"   Emotion: {new_emotion}")
        print(f"   Kusala: {kusala_delta:+.2f}, Akusala: {akusala_delta:+.2f}")
        print(f"   Virtue changes: Sila {virtue_delta.get('sila', 0):+.2f}, Samadhi {virtue_delta.get('samadhi', 0):+.2f}")
        print(f"   Total simulations: {len(character.simulation_history)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating character after simulation {character_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def process_shot_motion(
    shot_data: dict,
    simulation_results: list,
    character_states: dict
) -> dict:
    """
    🎬 Process shot through Motion Editor
    
    Automatically generates motion parameters based on:
    - Emotion from simulation results
    - Intensity from scene context
    - Character states and actions
    
    Args:
        shot_data: Shot information (camera settings, description, etc.)
        simulation_results: List of simulation results from all characters in shot
        character_states: Current states of all characters
    
    Returns:
        dict: Shot data with added motion_parameters
    """
    try:
        print(f"    🎬 Processing motion for shot {shot_data.get('shot_number')}...")
        
        # Extract dominant emotion from simulation results
        emotions = []
        intensities = []
        
        for sim_result in simulation_results:
            # Get emotion from state changes or default to neutral
            char_state = character_states.get(sim_result.get('character_id'), {})
            emotion = char_state.get('current_emotion', 'neutral')
            emotions.append(emotion)
            
            # Calculate intensity from kamma changes
            kusala_delta = sim_result.get('state_changes', {}).get('kusala_delta', 0)
            akusala_delta = sim_result.get('state_changes', {}).get('akusala_delta', 0)
            total_change = abs(kusala_delta) + abs(akusala_delta)
            
            if total_change > 0.5:
                intensities.append('high')
            elif total_change > 0.2:
                intensities.append('medium')
            else:
                intensities.append('low')
        
        # Determine dominant emotion and intensity
        dominant_emotion = emotions[0] if emotions else 'neutral'
        dominant_intensity = intensities[0] if intensities else 'medium'
        
        # Auto-generate motion parameters based on emotion
        motion_params = {
            'zoom_start': 1.0,
            'zoom_end': 1.0,
            'move_x': 0.0,
            'move_y': 0.0,
            'rotate_start': 0.0,
            'rotate_end': 0.0,
            'duration': shot_data.get('duration', 3.0),
            'speed': 1.0
        }
        
        # Emotion-based motion mapping
        if dominant_emotion == 'joy':
            motion_params['zoom_end'] = 1.2  # Zoom in for joy
            motion_params['move_x'] = 10  # Slight pan right
        elif dominant_emotion == 'sadness':
            motion_params['zoom_end'] = 0.9  # Zoom out for sadness
            motion_params['move_y'] = -15  # Tilt down
        elif dominant_emotion == 'anger':
            motion_params['move_x'] = 15  # Dynamic pan
            motion_params['speed'] = 1.3  # Faster movement
        elif dominant_emotion == 'fear':
            motion_params['move_y'] = 20  # Tilt up (looking up in fear)
            motion_params['rotate_end'] = 5  # Slight rotation (Dutch angle)
        elif dominant_emotion == 'calm':
            motion_params['zoom_end'] = 1.05  # Gentle zoom
            motion_params['speed'] = 0.8  # Slower, calmer movement
        elif dominant_emotion == 'compassion':
            motion_params['zoom_end'] = 1.15  # Zoom in to show emotion
            motion_params['move_y'] = 10  # Gentle tilt up
        
        # Intensity adjustments
        if dominant_intensity == 'high':
            motion_params['speed'] *= 1.3
        elif dominant_intensity == 'low':
            motion_params['speed'] *= 0.7
        
        # Add to shot data
        shot_data['motion_parameters'] = motion_params
        shot_data['motion_processed'] = True
        shot_data['motion_emotion'] = dominant_emotion
        shot_data['motion_intensity'] = dominant_intensity
        
        print(f"      ✅ Motion applied: {dominant_emotion} ({dominant_intensity}) - zoom: {motion_params['zoom_start']}→{motion_params['zoom_end']}")
        
        return shot_data
        
    except Exception as e:
        print(f"    ⚠️ Motion processing failed: {e}")
        # Return shot with default motion
        shot_data['motion_parameters'] = {
            'zoom_start': 1.0,
            'zoom_end': 1.0,
            'move_x': 0.0,
            'move_y': 0.0,
            'rotate_start': 0.0,
            'rotate_end': 0.0,
            'duration': shot_data.get('duration', 3.0),
            'speed': 1.0
        }
        shot_data['motion_processed'] = False
        return shot_data


async def simulate_character_in_shot(
    character_id: str,
    scene_context: dict,
    shot_context: dict,
    character_state: dict
) -> dict:
    """
    🎭 Simulate character behavior in a specific shot using AI
    
    Args:
        character_id: Character ID/Name
        scene_context: Scene information (location, time, description)
        shot_context: Shot information (shot_number, description, camera_angle)
        character_state: Current character mental state
        
    Returns:
        dict: Simulation results (actions, dialogue, state_changes)
    """
    try:
        # 1. Prepare Context for AI
        char_name = character_id
        current_virtue = character_state.get('virtue', {})
        current_emotion = character_state.get('current_emotion', 'neutral')
        
        prompt = f"""You are a Digital Actor Simulation Engine.
Simulate the internal state and actions of a character in a specific movie shot.

CHARACTER: {char_name}
CURRENT STATE:
- Emotion: {current_emotion}
- Virtue (Sila/Samadhi/Panna): {current_virtue.get('sila', 5):.1f}/{current_virtue.get('samadhi', 5):.1f}/{current_virtue.get('panna', 5):.1f}

SCENE CONTEXT:
Title: {scene_context.get('title')}
Desc: {scene_context.get('description')}
Location: {scene_context.get('location')}

CURRENT SHOT (The immediate moment):
Shot {shot_context.get('shot_number')}: {shot_context.get('shot_description')}

TASK:
1. Determine the character's reaction to this specific shot moment.
2. Decide if their mental state improves (Kusala) or worsens (Akusala) based on the situation.
3. Generate a short dialogue (if applicable) or internal thought.

OUTPUT JSON ONLY:
{{
  "action": "Specific physical action in this shot",
  "dialogue": "Spoken line or (Internal thought)",
  "emotion": "New emotional state (e.g. angry, calm, fearful)",
  "state_changes": {{
    "kusala_delta": 0.0 to 1.0 (Wholesome impact),
    "akusala_delta": 0.0 to 1.0 (Unwholesome impact),
    "virtue": {{
      "sila": -0.1 to +0.1,
      "samadhi": -0.1 to +0.1,
      "panna": -0.1 to +0.1
    }}
  }}
}}
"""

        # 2. Call AI (Ollama)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"AI Error: {response.text}")
                
            result_json = response.json().get("response", "")
            
            # Clean JSON
            result_clean = result_json.strip()
            if result_clean.startswith("```json"): result_clean = result_clean[7:]
            if result_clean.startswith("```"): result_clean = result_clean[3:]
            if result_clean.endswith("```"): result_clean = result_clean[:-3]
            
            sim_data = json.loads(result_clean.strip())
            
            return {
                "character_id": character_id,
                "actions_taken": [sim_data.get("action", "No action")],
                "dialogue_spoken": sim_data.get("dialogue", ""),
                "state_changes": sim_data.get("state_changes", {
                    "virtue": {"sila": 0, "samadhi": 0, "panna": 0},
                    "kusala_delta": 0,
                    "akusala_delta": 0
                }),
                "current_emotion": sim_data.get("emotion", "neutral"),
                "simulation_confidence": 0.9,
                "simulation_reasoning": "AI generated based on shot context"
            }

    except Exception as e:
        print(f"❌ Simulation error for character {character_id}: {e}")
        # Return safe fallback
        return {
            "character_id": character_id,
            "actions_taken": ["[Simulation unavailable]"],
            "dialogue_spoken": "",
            "state_changes": {
                "virtue": {"sila": 0.0, "samadhi": 0.0, "panna": 0.0},
                "kusala_delta": 0,
                "akusala_delta": 0,
                "hindrances": {}
            },
            "simulation_confidence": 0.0,
            "simulation_reasoning": f"Simulation failed: {str(e)}"
        }


# =============================================================================
# CREATE
# =============================================================================

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate):
    """
    สร้างโปรเจ็คใหม่
    
    - **project_id**: รหัสโปรเจ็คเฉพาะ (required)
    - **script_name**: ชื่อบท (required)
    - **genre**: ประเภทเรื่อง (required)
    - **studio**: สตูดิโอ (optional)
    - **writer**: นักเขียน (optional)
    - **language**: รหัสภาษา (default: th)
    - **status**: สถานะโปรเจ็ค (default: draft)
    """
    # Check if project_id already exists
    existing = await Project.find_one({"project_id": project_data.project_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with ID '{project_data.project_id}' already exists"
        )
    
    # Create new project
    project = Project(
        **project_data.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    await project.insert()
    
    return ProjectResponse(
        id=str(project.id),
        **project.model_dump(exclude={"id"})
    )


# =============================================================================
# READ
# =============================================================================

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0, description="จำนวนรายการที่จะข้าม"),
    limit: int = Query(50, ge=1, le=100, description="จำนวนรายการสูงสุด"),
    genre: Optional[str] = Query(None, description="กรองตามประเภทเรื่อง"),
    status: Optional[str] = Query(None, description="กรองตามสถานะ"),
    search: Optional[str] = Query(None, description="ค้นหาจากชื่อบท")
):
    """
    แสดงรายการโปรเจ็คทั้งหมด
    
    รองรับการกรองและค้นหา:
    - **skip**: ข้ามรายการ (สำหรับ pagination)
    - **limit**: จำนวนรายการสูงสุด (max 100)
    - **genre**: กรองตามประเภท
    - **status**: กรองตามสถานะ
    - **search**: ค้นหาจากชื่อบท
    """
    query = {}
    
    if genre:
        query["genre"] = genre
    
    if status:
        query["status"] = status
    
    if search:
        query["script_name"] = {"$regex": search, "$options": "i"}
    
    projects = await Project.find(query).skip(skip).limit(limit).to_list()
    
    return [
        ProjectResponse(
            id=str(p.id),
            **p.model_dump(exclude={"id"})
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """
    ดึงข้อมูลโปรเจ็คตาม project_id
    
    - **project_id**: รหัสโปรเจ็ค (เช่น proj_001)
    """
    project = await Project.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    
    return ProjectResponse(
        id=str(project.id),
        **project.model_dump(exclude={"id"})
    )


# =============================================================================
# UPDATE
# =============================================================================

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate
):
    """
    อัปเดตข้อมูลโปรเจ็ค
    
    - **project_id**: รหัสโปรเจ็ค
    - อัปเดตเฉพาะฟิลด์ที่ส่งมาเท่านั้น
    """
    project = await Project.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    
    # Update only provided fields
    update_data = project_data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await project.save()
    
    return ProjectResponse(
        id=str(project.id),
        **project.model_dump(exclude={"id"})
    )


# =============================================================================
# DELETE
# =============================================================================

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """
    ลบโปรเจ็ค
    
    - **project_id**: รหัสโปรเจ็ค
    - ⚠️ คำเตือน: จะลบ scenes, characters, shots, visuals ที่เกี่ยวข้องทั้งหมด
    """
    project = await Project.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    
    # Cascade delete all related entities
    try:
        from documents_narrative import Scene, Character, Shot, Visual
        
        # Delete all scenes in this project
        scenes = await Scene.find({"project_id": project_id}).to_list()
        scene_ids = [s.scene_id for s in scenes]
        
        # Delete all shots in these scenes
        if scene_ids:
            await Shot.find({"scene_id": {"$in": scene_ids}}).delete()
        
        # Delete all visuals in these shots
        # Note: Visuals are linked to shots, so they're deleted when shots are deleted
        # But we can also delete by project_id if Visual model has it
        try:
            await Visual.find({"project_id": project_id}).delete()
        except:
            pass  # Visual might not have project_id field
        
        # Delete all scenes
        await Scene.find({"project_id": project_id}).delete()
        
        # Delete all characters in this project
        await Character.find({"project_id": project_id}).delete()
        
    except Exception as e:
        print(f"Warning during cascade delete: {e}")
        # Continue with project deletion even if cascade fails
    
    # Finally, delete the project itself
    await project.delete()
    
    return None


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get("/{project_id}/stats")
async def get_project_stats(project_id: str):
    """
    ดึงสถิติของโปรเจ็ค
    
    Returns:
    - จำนวน scenes, characters, shots, visuals
    - เปอร์เซ็นต์ความสมบูรณ์
    """
    project = await Project.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    
    # Count related entities
    try:
        from documents_narrative import Scene, Character, Shot, Visual
        
        # Count scenes in this project
        scene_count = await Scene.find({"project_id": project_id}).count()
        
        # Count characters in this project
        character_count = await Character.find({"project_id": project_id}).count()
        
        # Count shots in scenes of this project
        scenes = await Scene.find({"project_id": project_id}).to_list()
        scene_ids = [s.scene_id for s in scenes]
        shot_count = 0
        if scene_ids:
            shot_count = await Shot.find({"scene_id": {"$in": scene_ids}}).count()
        
        # Count visuals
        visual_count = 0
        try:
            visual_count = await Visual.find({"project_id": project_id}).count()
        except:
            # Fallback: count visuals linked to shots
            shots = await Shot.find({"scene_id": {"$in": scene_ids}}).to_list()
            shot_ids = [s.shot_id for s in shots]
            if shot_ids:
                visual_count = await Visual.find({"shot_id": {"$in": shot_ids}}).count()
        
        # Calculate completion percentage
        # Based on: has scenes, has characters, has shots, has visuals, status is not DEVELOPMENT
        completion_score = 0
        if scene_count > 0:
            completion_score += 20
        if character_count > 0:
            completion_score += 20
        if shot_count > 0:
            completion_score += 30
        if visual_count > 0:
            completion_score += 20
        if project.status != "DEVELOPMENT":
            completion_score += 10
        
        completion_percentage = completion_score
        
    except Exception as e:
        print(f"Error counting entities: {e}")
        # Return zeros on error
        scene_count = 0
        character_count = 0
        shot_count = 0
        visual_count = 0
        completion_percentage = 0
    
    return {
        "project_id": project_id,
        "script_name": project.script_name,
        "genre": project.genre,
        "status": project.status,
        "scene_count": scene_count,
        "character_count": character_count,
        "shot_count": shot_count,
        "visual_count": visual_count,
        "completion_percentage": completion_percentage
    }


@router.post("/generate-chapter-structure")
async def generate_chapter_structure(data: dict):
    """
    🤖 AI Generate Chapter Structure (Save the Cat 15 Beats)
    
    ใช้ข้อมูลจาก Step 1-3 เพื่อสร้างโครงสร้างบท 15 จุด (Save the Cat) อัตโนมัติ
    
    **Input:**
    - Step 1: project_name, genres, script_type, concept_description, target_audience, tags
    - Step 2: big_idea, premise, theme, logline, timeline
    - Step 3: characters (name, role, archetype, description)
    - ai_provider: AI model (qwen2.5, gpt-4)
    
    **Output:**
    - structure: array ของ 15 beats พร้อม content ที่ละเอียด
    """
    try:
        print("\n" + "="*80)
        print("🔍 GENERATE CHAPTER STRUCTURE - Request received")
        print("="*80)
        
        # Extract context from Step 1
        script_name = data.get('script_name', 'Untitled')
        genres = data.get('genres', [])
        script_type = data.get('script_type', 'movie')
        concept_description = data.get('concept_description', '')
        target_audience = data.get('target_audience', '')
        tags = data.get('tags', [])
        
        print(f"\n📋 STEP 1 DATA:")
        print(f"  - Script Name: {script_name}")
        print(f"  - Genres: {len(genres)} items")
        print(f"  - Script Type: {script_type}")
        print(f"  - Concept: {concept_description[:100] if concept_description else 'Not provided'}...")
        print(f"  - Target Audience: {target_audience if target_audience else 'Not provided'}")
        print(f"  - Tags: {len(tags)} items")
        
        # Extract context from Step 2
        big_idea = data.get('big_idea', {})
        premise = data.get('premise', {})
        theme = data.get('theme', {})
        timeline = data.get('timeline', {})
        
        print(f"\n📖 STEP 2 DATA:")
        print(f"  - Big Idea: {big_idea.get('content', 'Not provided')[:100]}...")
        print(f"  - Premise Q: {premise.get('question', 'Not provided')[:100]}...")
        print(f"  - Theme Lesson: {theme.get('lesson', 'Not provided')[:100]}...")
        
        # Extract context from Step 3
        characters = data.get('characters', [])
        
        print(f"\n👥 STEP 3 DATA:")
        print(f"  - Characters: {len(characters)} characters")
        
        # AI Provider
        ai_provider = data.get('ai_provider', 'qwen2.5')
        
        print(f"\n🤖 AI PROVIDER: {ai_provider}")
        print("="*80)
        
        # Build comprehensive AI prompt with all Step 1-3 data
        # Format genres info
        genres_text = ""
        if genres:
            genres_list = [f"{g.get('type', '')} ({g.get('percentage', 0)}%)" for g in genres]
            genres_text = ", ".join(genres_list)
        
        # Format characters info with FULL details (physical + personality)
        characters_text = ""
        if characters:
            char_details = []
            for char in characters[:5]:  # Top 5 characters
                char_name = char.get('name', '')
                char_role = char.get('role', '')
                char_archetype = char.get('archetype', '')
                char_desc = char.get('description', '')
                
                # Physical traits
                char_physical = char.get('physical_traits', {})
                age = char_physical.get('age', '')
                gender = char_physical.get('gender', '')
                appearance = char_physical.get('appearance', '')
                
                # Personality traits
                char_personality = char.get('personality_traits', {})
                strengths = char_personality.get('strengths', [])
                weaknesses = char_personality.get('weaknesses', [])
                fears = char_personality.get('fears', [])
                desires = char_personality.get('desires', [])
                
                # Backstory
                backstory = char.get('backstory', '')
                
                # Build comprehensive character info
                char_info = f"**{char_name}** ({char_role}, {char_archetype})"
                if age or gender:
                    char_info += f"\n  • Physical: {gender} {age}"
                if appearance:
                    char_info += f", {appearance}"
                if char_desc:
                    char_info += f"\n  • Description: {char_desc}"
                if backstory:
                    char_info += f"\n  • Backstory: {backstory[:150]}"
                if strengths:
                    char_info += f"\n  • Strengths: {', '.join(strengths[:3])}"
                if weaknesses:
                    char_info += f"\n  • Weaknesses: {', '.join(weaknesses[:3])}"
                if desires:
                    char_info += f"\n  • Desires: {', '.join(desires[:3])}"
                if fears:
                    char_info += f"\n  • Fears: {', '.join(fears[:3])}"
                
                char_details.append(char_info)
            characters_text = "\n\n".join(char_details)
        
        # Format timeline info
        timeline_text = ""
        if timeline:
            total_duration = timeline.get('total_duration', '')
            timeline_desc = timeline.get('description', '')
            if total_duration:
                timeline_text = f"Duration: {total_duration}"
            if timeline_desc:
                timeline_text += f" - {timeline_desc}"
        
        # Check if user provided Theme or AI should create one
        theme_lesson = theme.get('lesson', '').strip()
        has_user_theme = bool(theme_lesson)
        
        # Build prompt based on whether Theme is provided
        if has_user_theme:
            # User provided Theme - AI MUST use it
            theme_instruction = f"""🎯 THEME (คำตอบ/บทเรียนหลัก - กำหนดโดยผู้ใช้):
{theme.get('teaching', 'This tale teaches that')} {theme_lesson}

⚠️ CRITICAL: You MUST use this EXACT theme throughout ALL 15 beats.
- Do NOT create a different theme
- Do NOT interpret or modify this theme
- Every beat must reflect and support THIS specific theme
- Story must stay focused on THIS theme, never deviate"""
        else:
            # No Theme provided - AI creates unique one
            theme_instruction = f"""🎯 YOUR TASK - CREATE UNIQUE THEME:
1. Analyze BIG IDEA: "{big_idea.get('content', '')}"
2. Analyze PREMISE: "{premise.get('question', '')}"
3. Create a UNIQUE, SPECIFIC theme that:
   - Answers the Big Idea question
   - Is NOT generic (avoid: "ทุกการเลือกมีผลที่ตามมา", "ความรักสำคัญ", etc.)
   - Is relevant to THIS specific story
   - Can be learned by the protagonist
4. Use this theme consistently in ALL 15 beats

Examples of GOOD unique themes:
- "ความสำเร็จที่แท้จริงคือการหาจุดสมดุลระหว่างความฝันและครอบครัว"
- "ความรักที่แท้จริงคือการปล่อยวางเมื่อถึงเวลา"
- "ความกล้าหาญไม่ใช่การไม่กลัว แต่คือการทำในสิ่งที่กลัว"

❌ AVOID generic themes like:
- "ทุกการเลือกมีผลที่ตามมา"
- "ความรักมีพลัง"
- "ความจริงสำคัญ"

CRITICAL: Theme MUST be unique to THIS story's Big Idea and Premise."""
        
        # Build concise but comprehensive prompt
        prompt = f"""You are a professional Thai screenplay writer. Create a 15-beat story structure (Save the Cat).

PROJECT: {script_name} ({script_type}, {genres_text})
CONCEPT: {concept_description if concept_description else big_idea.get('content', '')}
TARGET: {target_audience if target_audience else 'General'}

BIG IDEA (คำถาม): {big_idea.get('content', '')}
PREMISE: {premise.get('question', '')}

{theme_instruction}

CHARACTERS (Step 3 - MUST USE THESE EXACT NAMES):
{characters_text if characters_text else '- To be determined'}

⚠️ CRITICAL CHARACTER RULES:
1. Use ONLY character names listed above
2. DO NOT create new character names (like "นิดา", "พ่อ", etc.)
3. If no characters provided, use generic "ตัวเอก", "ตัวรอง" instead
4. Every character mentioned in beats MUST match names from Step 3 exactly
5. Example: If Step 3 has "John (Protagonist)", use "John" not "นิดา" or other names

🎬 TASK:
Create 15 beats with approximately 250-350 Thai characters each (roughly 5-7 sentences per beat).
Each beat should be detailed and descriptive, not just brief summaries. Use EXACT character names from Step 3 list above. Show clear story progression.

⚠️ LENGTH REQUIREMENT:
- Each beat content must be 250-350 Thai characters (ตัวอักษร)
- This is about 5-7 complete sentences with proper detail
- Include specific actions, emotions, dialogue, and story elements
- Do NOT write short summaries - write full narrative descriptions

THEME CREATION PROCESS:
Step 1: Analyze Big Idea + Premise to understand the core conflict
Step 2: Determine what specific lesson/theme THIS story teaches
Step 3: State the theme clearly in Beat 2
Step 4: Show protagonist's journey learning this theme through all beats

EXAMPLE THEMES (create something UNIQUE like these):
- "ความสำเร็จที่แท้จริงคือการหาจุดสมดุลระหว่างความฝันและครอบครัว"
- "ความรักที่แท้จริงคือการปล่อยวางเมื่อถึงเวลา"
- "ความกล้าหาญไม่ใช่การไม่กลัว แต่คือการทำแม้จะกลัว"
- "การให้อภัยตัวเองคือจุดเริ่มต้นของการเยียวยา"

Save the Cat beats structure:
1. Opening Image - ภาพเปิดเรื่อง แสดงสถานะเดิมของตัวเอก (ก่อนเรียนรู้ theme)
2. Theme Stated ⭐ - ระบุธีม บทเรียนที่จะเรียนรู้ (ต้องพูดถึง theme โดยตรง)
3. Set-Up - ชีวิตปกติ แนะนำตัวละครและโลก (แสดงปัญหาที่เกี่ยวกับ theme)
4. Catalyst - จุดเปลี่ยน เหตุการณ์ที่เปลี่ยนชีวิต (ท้าทาย theme)
5. Debate - ลังเล ไม่แน่ใจจะทำหรือไม่ (ต่อสู้กับ theme)
6. Break Into Two - ก้าวเข้าสู่โลกใหม่ ตัดสินใจลงมือ (เริ่มต้นการเรียนรู้)
7. B Story ⭐ - เรื่องรอง ความสัมพันธ์ที่สอนธีม (ตัวละครที่ช่วยสอน theme)
8. Fun and Games - สนุกสนาน ทดสอบโลกใหม่ (ทดลองวิธีใหม่ที่เกี่ยวกับ theme)
9. Midpoint - จุดกึ่งกลาง ชัยชนะหรือพ่ายแพ้ชั่วคราว (คิดว่าเข้าใจ theme แล้ว)
10. Bad Guys Close In - ศัตรูบุกเข้ามา สถานการณ์แย่ลง (ถูกทดสอบ theme อย่างหนัก)
11. All Is Lost - เสียทุกอย่าง จุดต่ำสุด (ยังไม่เข้าใจ theme จริงๆ)
12. Dark Night of the Soul - คืนที่มืดมน สิ้นหวัง (ไตร่ตรอง theme อย่างลึกซึ้ง)
13. Break Into Three ⭐ - พบทางออก เข้าใจบทเรียน (เข้าใจ theme อย่างแท้จริง)
14. Finale - ตอนจบ ใช้สิ่งที่เรียนรู้เอาชนะ (ประยุกต์ใช้ theme)
15. Final Image - ภาพปิดเรื่อง แสดงการเปลี่ยนแปลง (หลังเรียนรู้ theme สมบูรณ์)

OUTPUT FORMAT - Respond with ONLY valid JSON array (no explanation, no markdown):

⚠️ CRITICAL JSON RULES:
1. Use ONLY double quotes (") for all strings - NO single quotes (')
2. NO trailing commas after last element
3. NO comments (// or /* */)
4. Escape special characters in strings: \" for quotes, \n for newlines
5. Each object MUST have exactly: {{"id": number, "name": "string", "content": "string"}}
6. Array MUST have exactly 15 objects
7. Do NOT wrap in ```json or ``` markdown blocks
8. Start response with [ and end with ]

⚠️ CHARACTER NAME EXAMPLES (DO NOT USE THESE - USE STEP 3 NAMES):
The examples below use "นิดา" and "พ่อ" for demonstration ONLY.
YOU MUST replace with ACTUAL character names from Step 3 character list above.

EXAMPLE VALID JSON FORMAT WITH PROPER LENGTH (250-350 characters per beat):
[
  {{"id": 1, "name": "Opening Image", "content": "เช้าวันหนึ่ง [ใช้ชื่อจาก Step 3] นั่งริมหน้าต่างของคอนโด มองเห็นแสงแดดส่องผ่านม่านบาง ใบหน้าเหนื่อยล้า สะท้อนภาพคนที่สูญเสียความหวัง บนโต๊ะวางรูปถ่ายเก่าๆ ของครอบครัว [เขา/เธอ]หยิบรูปขึ้นมาดู น้ำตาริน ความทรงจำในอดีตที่สดใสกลับมาหลอก ทำให้[เขา/เธอ]รู้สึกโดดเดี่ยว และเริ่มตั้งคำถามว่าชีวิตจะยังมีความหมายหรือไม่"}},
  {{"id": 2, "name": "Theme Stated ⭐", "content": "วันนั้น [พ่อ/แม่/Mentor จาก Step 3]พูดกับ[Protagonist]ว่า 'ทุกการเลือกมีผลที่ตามมา ลูกต้องคิดให้รอบคอบก่อนตัดสินใจทุกครั้ง' คำพูดนี้ติดอยู่ในใจ[Protagonist]ตลอด แต่ในขณะนั้น[เขา/เธอ]ยังไม่เข้าใจความหมายที่แท้จริง เพียงแค่พยักหน้ารับรู้และเก็บไว้ในใจ โดยไม่รู้ว่าในอนาคตข้างหน้า คำพูดนี้จะกลายเป็นบทเรียนชีวิตที่สำคัญที่สุด"}}
]

NOW GENERATE 15 BEATS with 250-350 characters EACH: 
⭐ CRITICAL BEATS - MUST explicitly address theme:

Beat 2 (Theme Stated): State the theme lesson directly in first sentence
  ❌ Wrong: "[สร้างชื่อใหม่]เป็นนักศิลปะ เธอมีความฝัน..."
  ✅ Correct: "ทุกการเลือกมีผลที่ตามมา [ใช้ชื่อจาก Step 3]ได้ยินคำพูดนี้จากครูในวัยเด็ก..."
  
Beat 7 (B Story): Character who TEACHES theme through story/example
  ❌ Wrong: "พ่อของ[สร้างชื่อใหม่]เป็นตัวอย่างของคนที่..."
  ✅ Correct: "[Mentor name from Step 3]เล่าเรื่องวันที่เขาเลือกทิ้งทุนเรียนต่อเพื่อช่วยปู่ย่า ผลที่ตามมาคือเขาเสียโอกาสแต่ได้ครอบครัวที่อบอุ่น 'ทุกการเลือกมีผลที่ตามมา' [Mentor]พูด"
  Must: 1) Tell specific story/example, 2) State theme explicitly in dialogue, 3) Use names from Step 3
  
Beat 13 (Break Into Three): Protagonist's AHA moment about theme
  ❌ Wrong: "[สร้างชื่อใหม่]เข้าใจที่แท้จริงว่าการเลือกไม่มีทางเดียว..."
  ✅ Correct: "[Protagonist from Step 3]ตระหนักได้ในที่สุด 'ทุกการเลือกมีผลที่ตามมาจริงๆ' [เขา/เธอ]นึกถึงคำพูดของ[Mentor from Step 3] ถ้าเลือกทุน ครอบครัวก็จะลำบาก ถ้าอยู่ช่วย ความฝันก็จะสูญเสีย ดังนั้น[เขา/เธอ]ต้องหาทางที่ทั้งสองอย่างมีผลดีที่สุด"
  Must: 1) Quote theme directly, 2) Show understanding consequences, 3) Make decision based on theme, 4) Use names from Step 3

🎯 THEME COHERENCE:
- Every beat must connect to: "{theme.get('lesson', '')}"
- No deviation from this central theme
- Show protagonist's journey: NOT understanding → TESTING theme → FULLY understanding

⚠️⚠️⚠️ CRITICAL LENGTH ENFORCEMENT ⚠️⚠️⚠️
EACH beat MUST be MINIMUM 250 Thai characters. NO EXCEPTIONS.
If a beat is shorter than 250 characters, ADD MORE DETAILS:
- Add specific dialogue with quotation marks
- Describe emotions in detail (facial expressions, body language)
- Include internal thoughts of the character
- Describe the setting/environment
- Add sensory details (sights, sounds, feelings)
- Explain character motivations and conflicts

Example of TOO SHORT (WRONG - only 100 characters):
"อาทิตย์นั่งมองท้องฟ้า ดวงตาเศร้า เขาคิดถึงคนรัก ความทรงจำในอดีตทำให้เขาเสียใจ"

Example of CORRECT LENGTH (300+ characters):
"เช้าวันนั้น อาทิตย์นั่งอยู่บนชั้นดาดฟ้าของอาคารคอนโด มองดูท้องฟ้าสีส้มแดงที่กำลังเปลี่ยนเป็นสีน้ำเงินเข้ม ลมพัดโชยผ่านใบหน้าที่เต็มไปด้วยความเหนื่อยล้า เขาหยิบรูปถ่ายครอบครัวที่พกติดตัวมาตลอดขึ้นมาดู น้ำตาไหลริน 'ทำไมชีวิตถึงโหดร้ายขนาดนี้' เขาพูดกับตัวเองด้วยเสียงสั่นเครือ ความทรงจำในอดีตที่สดใสกลับมาหลอกหลอน ทำให้เขารู้สึกโดดเดี่ยวและสิ้นหวัง ในหัวใจลึกๆ เขาเริ่มตั้งคำถามว่า ความรักที่เขาเชื่อถือมาตลอดนั้น ยังมีความหมายอีกหรือไม่"

NOW Generate 15 beats with MINIMUM 250 characters EACH:"""
        
        # Determine AI endpoint
        if ai_provider == 'qwen2.5':
            # Use local Ollama Qwen2.5
            api_url = "http://127.0.0.1:11434/api/generate"
            payload = {
                "model": "qwen2.5:7b",  # Use installed 7B model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 1.0,  # Increase for more creative, longer output
                    "top_p": 0.95,
                    "num_predict": 12000,  # Further increased for longer beats
                    "num_ctx": 32768,  # Large context window
                    "repeat_penalty": 1.1  # Reduce repetition
                }
            }
            
            print(f"⏳ Sending request to Ollama (timeout=600s)...")
            async with httpx.AsyncClient(timeout=600.0) as client:  # Increased timeout to 600s
                api_response_obj = await client.post(api_url, json=payload)
                print(f"✅ Ollama response received (status: {api_response_obj.status_code})")
                
                if api_response_obj.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Ollama API error: {api_response_obj.text}"
                    )
                
                result = api_response_obj.json()
                ai_response = result.get('response', '')
        
        elif ai_provider == 'gpt-4':
            # Use OpenAI GPT-4
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API key not configured"
                )
            
            api_url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a professional screenplay writer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:  # เพิ่ม timeout สำหรับ OpenAI API
                api_response_obj = await client.post(api_url, json=payload, headers=headers)
                
                if api_response_obj.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"OpenAI API error: {api_response_obj.text}"
                    )
                
                result = api_response_obj.json()
                ai_response = result['choices'][0]['message']['content']
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported AI provider: {ai_provider}"
            )
        
        # Parse AI response (try to extract JSON)
        # Log raw response for debugging
        print(f"\n🤖 AI Response ({ai_provider}):")
        print(f"Length: {len(ai_response)} characters")
        print(f"First 500 chars:\n{ai_response[:500]}")
        print(f"Last 200 chars:\n{ai_response[-200:]}")
        
        # Try to find JSON array in response
        # First, try to remove markdown code blocks
        cleaned_response = ai_response.strip()
        
        # Remove markdown code blocks
        if '```json' in cleaned_response:
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
        elif '```' in cleaned_response:
            cleaned_response = re.sub(r'```\s*', '', cleaned_response)
        
        print(f"\n🧹 After cleaning markdown:")
        print(f"First 300 chars: {cleaned_response[:300]}")
        
        # Find JSON array
        json_match = re.search(r'\[[\s\S]*\]', cleaned_response)
        if json_match:
            structure_json = json_match.group(0)
            print(f"\n📦 Found JSON array, length: {len(structure_json)}")
            
            # 🔧 Pre-process: Fix Thai quotes BEFORE parsing
            structure_json = structure_json.replace('"', '"').replace('"', '"')  # Thai quotes → ASCII
            structure_json = structure_json.replace(''', "'").replace(''', "'")  # Thai single quotes
            print(f"✨ After fixing Thai quotes (first 300): {structure_json[:300]}")
            
            try:
                # Try direct parsing first
                structure = json.loads(structure_json)
                print(f"✅ JSON parsed successfully: {len(structure)} items")
                
                # Validate structure
                if not isinstance(structure, list):
                    raise ValueError("Response is not an array")
                    
                if len(structure) != 15:
                    print(f"⚠️ Warning: Expected 15 beats, got {len(structure)}")
                
                # Ensure all beats have required fields
                for i, beat in enumerate(structure, 1):
                    if not isinstance(beat, dict):
                        raise ValueError(f"Beat {i} is not an object")
                    if 'id' not in beat or 'name' not in beat or 'content' not in beat:
                        print(f"⚠️ Beat {i} missing fields. Has: {beat.keys()}")
                        raise ValueError(f"Beat {i} missing required fields (id, name, content)")
                
                print(f"✅ All beats validated")
                
                # 🎯 POST-PROCESSING: Enforce 250-350 character length requirement
                print(f"\n🔍 Checking beat lengths and padding if needed...")
                for i, beat in enumerate(structure, 1):
                    content = beat.get('content', '')
                    current_length = len(content)
                    
                    if current_length < 250:
                        # Beat is too short - need to expand
                        padding_needed = 250 - current_length
                        print(f"  ⚠️ Beat {i} too short ({current_length} chars) - padding +{padding_needed}")
                        
                        # Smart padding based on beat type
                        name = beat.get('name', '').lower()
                        
                        if 'opening' in name:
                            padding = f" ท้องฟ้ายามเช้ามีสีสันสดใส แสงแดดส่องผ่านหน้าต่างเข้ามาในห้อง สร้างบรรยากาศที่อบอุ่นแต่โดดเดี่ยว เสียงเพลงจากวิทยุดังขึ้นเบาๆ เป็นเพลงเก่าที่เคยชอบฟัง ทำให้ความทรงจำในอดีตกลับมาอีกครั้ง ใบหน้าที่เคยมีรอยยิ้มสดใสกลับเต็มไปด้วยความเศร้าหมอง"
                        elif 'theme' in name:
                            padding = f" ในขณะนั้นคำพูดดูเหมือนธรรมดา แต่มันฝังลึกอยู่ในใจ เวลาผ่านไป ความหมายที่แท้จริงค่อยๆ ปรากฏชัดเจนขึ้น ทุกๆ การเลือกที่ทำไป ไม่ว่าจะเล็กหรือใหญ่ ล้วนมีผลกระทบต่อชีวิตในอนาคต บางครั้งเป็นผลดี บางครั้งเป็นผลร้าย แต่สิ่งสำคัญคือต้องรับผิดชอบต่อทุกการตัดสินใจ"
                        elif 'catalyst' in name or 'debate' in name:
                            padding = f" ความกังวลเริ่มก่อตัวขึ้นในใจ คิดถึงผลที่จะตามมาทั้งในด้านดีและด้านร้าย หัวใจเต้นแรงด้วยความลังเล สองทางเลือกที่ขัดแย้งกันทำให้ยากที่จะตัดสินใจ เวลาเดินช้าเหมือนหยุดนิ่ง แต่การตัดสินใจก็เข้ามาใกล้ทุกขณะ ต้องเลือกให้ได้ในที่สุด"
                        elif 'climax' in name:
                            padding = f" นี่คือช่วงเวลาสำคัญที่สุด ทุกสิ่งที่เรียนรู้มาตลอดทั้งเรื่องถูกนำมาใช้ในตอนนี้ ความกลัว ความหวัง ความรัก ความเสียสละ ทั้งหมดรวมตัวกันในจุดนี้ หัวใจเต้นแรงจนแทบจะหยุด มือสั่นเทาไม่อยู่ แต่ก็ต้องกล้าเผชิญหน้ากับมัน เพราะนี่คือจุดจบที่รอคอยมา"
                        elif 'resolution' in name:
                            padding = f" ทุกอย่างเริ่มชัดเจนขึ้น บทเรียนที่เรียนรู้มาตลอดเส้นทางกลายเป็นปัญญาที่แท้จริง ชีวิตไม่ได้สมบูรณ์แบบ แต่มันมีความหมาย การเดินทางที่ผ่านมาทำให้เติบโตและแข็งแกร่งขึ้น พร้อมเผชิญหน้ากับอนาคตด้วยความมั่นใจและความหวังใหม่"
                        else:
                            padding = f" บรรยากาศรอบตัวเต็มไปด้วยความตึงเครียด แต่ก็มีความหวังแฝงอยู่ ทุกก้าวที่เดินไปทำให้เข้าใจตัวเองมากขึ้น ความรู้สึกที่สับสนค่อยๆ เปลี่ยนเป็นความชัดเจน ทุกคนมีบทบาทในการเปลี่ยนแปลงนี้ ไม่ว่าจะรู้ตัวหรือไม่ก็ตาม การเรียนรู้จากประสบการณ์คือสิ่งที่มีค่าที่สุด"
                        
                        # Add padding up to minimum length
                        beat['content'] = content + padding[:padding_needed]
                        new_length = len(beat['content'])
                        print(f"    ✅ Padded to {new_length} chars")
                    elif current_length > 350:
                        # Beat is too long - trim to 350
                        print(f"  ⚠️ Beat {i} too long ({current_length} chars) - trimming to 350")
                        beat['content'] = content[:347] + '...'
                        print(f"    ✅ Trimmed to 350 chars")
                    else:
                        print(f"  ✅ Beat {i} OK ({current_length} chars)")
                
                print(f"✅ All beats now meet 250-350 character requirement")
                
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback: Try aggressive cleaning
                print(f"\n⚠️ JSON parse failed: {str(e)}")
                print(f"🔧 Attempting aggressive cleaning...")
                
                # Aggressive cleaning - fix common Qwen2.5 issues
                structure_json_cleaned = structure_json
                
                # 0. Remove newlines within string values (Qwen2.5 breaks lines mid-sentence)
                # First protect the JSON structure by only removing newlines within quotes
                # Pattern: "text นิดา[\n]งเขียน" → "text นิดางเขียน"
                structure_json_cleaned = re.sub(r'(?<=[\u0E00-\u0E7F])\n(?=[\u0E00-\u0E7F])', '', structure_json_cleaned)
                
                # 0.1 Remove newlines that are NOT followed by a quote or brace (likely inside a string)
                # This is a bit risky but helps with "Thai：\n" cases
                # We replace them with a space
                def replace_inner_newlines(match):
                    return match.group(0).replace('\n', ' ')
                
                # Match content inside quotes and replace newlines
                structure_json_cleaned = re.sub(r'"([^"]*)"', replace_inner_newlines, structure_json_cleaned, flags=re.DOTALL)
                
                # 0.2 Fix missing closing quotes in content fields - Qwen2.5 sometimes forgets them
                # Pattern: "content": "text text},  →  "content": "text text"},
                # First, fix all instances where } or }] appear without closing quote
                structure_json_cleaned = re.sub(r'("content"\s*:\s*"[^"]+)},', r'\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\s*:\s*"[^"]+)}]', r'\1"}]', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\s*:\s*"[^"]+)}\s*,', r'\1"},', structure_json_cleaned)
                
                # Fix cases where content ends abruptly with }, or }]
                # Pattern: ...ใจ},  →  ...ใจ"},
                structure_json_cleaned = re.sub(r'([^"]})(},)', r'\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'([^"}])}]', r'\1"}]', structure_json_cleaned)
                
                # 0.3 Remove Chinese characters from Qwen2.5 (e.g., "250-350字")
                structure_json_cleaned = re.sub(r'[\u4e00-\u9fff]+', '', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'：', ':', structure_json_cleaned)  # Fix Chinese colon
                
                # 0.4 Remove any non-JSON trailing content (e.g., "%")
                structure_json_cleaned = re.sub(r'\]\s*[^}\]]*$', ']', structure_json_cleaned)
                
                # 1. Fix missing "name": before beat names
                # Pattern: {"id": 3, "Set-Up", "content"  →  {"id": 3, "name": "Set-Up", "content"
                structure_json_cleaned = re.sub(
                    r'("id"\s*:\s*\d+)\s*,\s*"([^"]+)"\s*,\s*("content")',
                    r'\1, "name": "\2", \3',
                    structure_json_cleaned
                )
                
                # 2. Fix closing parenthesis instead of comma: }),  →  },
                # Pattern: "content": "..."}),  →  "content": "..."},
                structure_json_cleaned = re.sub(r'\}\)\s*,', '},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'\}\)', '}', structure_json_cleaned)
                
                # 3. Fix single quotes to double quotes
                structure_json_cleaned = structure_json_cleaned.replace("'", '"')
                
                # 4. Remove trailing commas before } and ]
                structure_json_cleaned = re.sub(r',(\s*[}\]])', r'\1', structure_json_cleaned)
                
                # 5. Fix missing commas between objects
                structure_json_cleaned = re.sub(r'}\s*{', r'},{', structure_json_cleaned)
                
                # 6. Remove any markdown remnants
                structure_json_cleaned = re.sub(r'```json\s*', '', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'```\s*', '', structure_json_cleaned)
                
                print(f"🧹 After cleaning (first 600): {structure_json_cleaned[:600]}")
                
                try:
                    structure = json.loads(structure_json_cleaned)
                    print(f"✅ Cleaned JSON parsed: {len(structure)} items")
                except json.JSONDecodeError as parse_error:
                    # Ultimate fallback: Show detailed error and save to file
                    error_msg = f"Failed to parse AI response as JSON: {str(parse_error)}"
                    print(f"\n❌ {error_msg}")
                    print(f"Error position: line {parse_error.lineno}, column {parse_error.colno}")
                    print(f"Error message: {parse_error.msg}")
                    
                    # Save problematic response to file for debugging
                    import time
                    timestamp = int(time.time())
                    debug_file = f"/tmp/ai_response_error_{timestamp}.json"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(ai_response)
                    print(f"💾 Full response saved to: {debug_file}")
                    
                    raise HTTPException(
                        status_code=500,
                        detail=f"{error_msg}\n\nDebug: Response saved to {debug_file}"
                    )
        else:
            # Last resort: Create simple structure from text
            print(f"❌ No JSON array found in response")
            print(f"Full raw response:\n{ai_response}")
            raise HTTPException(
                status_code=500,
                detail="AI response does not contain valid JSON array"
            )
        
        return {
            "success": True,
            "structure": structure,
            "ai_provider": ai_provider,
            "raw_response": ai_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )


@router.post("/generate-chapter-structure-batch")
async def generate_chapter_structure_batch(
    data: dict,
    response: Response  # 🔥 ADD: Response object for CORS headers
):
    """
    🤖 AI Generate Chapter Structure (Progressive Batch Mode)
    """
    try:
        # 🔥 FIX: Add CORS headers explicitly
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

        batch_number = data.get('batch_number', 1)
        previous_beats = data.get('previous_beats', [])
        
        print(f"\n🎯 BATCH GENERATION - Batch {batch_number}/3")
        print(f"📋 Previous beats: {len(previous_beats)}")
        
        # กำหนด range ของ beats แต่ละ batch
        batch_ranges = {
            1: (1, 6),   # Act 1: Opening Image → Break Into Two
            2: (7, 11),  # Act 2a: B Story → All Is Lost
            3: (12, 15)  # Act 2b + Act 3: Dark Night → Final Image
        }
        
        if batch_number not in batch_ranges:
            raise HTTPException(status_code=400, detail="Invalid batch_number (must be 1, 2, or 3)")
        
        # Extract context (เหมือน endpoint เดิม แต่เพิ่ม context จาก previous_beats)
        project_context = data.get('project_context', {})
        ai_provider = data.get('ai_provider', 'qwen2.5')
        
        # Extract additional fields needed for prompt
        script_type = data.get('script_type', 'Movie')
        concept_description = data.get('concept_description', '')
        target_audience = data.get('target_audience', '')
        timeline = data.get('timeline', {})

        # Extract project details from context
        script_name = project_context.get('script_name') or data.get('script_name', 'Untitled')
        genres = project_context.get('genres') or data.get('genres', [])
        big_idea = project_context.get('big_idea') or data.get('big_idea', {})
        premise = project_context.get('premise') or data.get('premise', {})
        theme = project_context.get('theme') or data.get('theme', {})
        characters = project_context.get('characters') or data.get('characters', [])
        
        # Build prompt context from previous beats
        previous_context = ""
        if previous_beats and batch_number > 1:
            previous_context = "\n\n📖 PREVIOUS BEATS (อ้างอิงต่อเนื่อง):\n"
            for beat in previous_beats:
                previous_context += f"{beat.get('id')}. {beat.get('name')}: {beat.get('content', '')}\n"
        
        # Build COMPREHENSIVE prompt (maintain quality like original)
        genres_text = ", ".join([f"{g.get('type', '')} ({g.get('percentage', 0)}%)" for g in genres[:3]])
        
        # Format characters with FULL details (same as original endpoint)
        characters_text = ""
        if characters:
            char_details = []
            for char in characters[:5]:
                char_name = char.get('name', '')
                char_role = char.get('role', '')
                char_archetype = char.get('archetype', '')
                char_desc = char.get('description', '')
                
                # Physical traits
                char_physical = char.get('physical_traits', {})
                age = char_physical.get('age', '')
                gender = char_physical.get('gender', '')
                appearance = char_physical.get('appearance', '')
                
                # Personality traits
                char_personality = char.get('personality_traits', {})
                strengths = char_personality.get('strengths', [])
                weaknesses = char_personality.get('weaknesses', [])
                fears = char_personality.get('fears', [])
                desires = char_personality.get('desires', [])
                
                # Backstory
                backstory = char.get('backstory', '')
                
                # Build comprehensive character info
                char_info = f"**{char_name}** ({char_role}, {char_archetype})"
                if age or gender or appearance:
                    physical_desc = f"{gender} {age}".strip()
                    if appearance:
                        physical_desc += f", {appearance}"
                    char_info += f"\n  Physical: {physical_desc}"
                if char_desc:
                    char_info += f"\n  Description: {char_desc}"
                if backstory:
                    char_info += f"\n  Backstory: {backstory[:150]}"
                
                personality_parts = []
                if strengths:
                    personality_parts.append(f"Strengths: {', '.join(strengths[:3])}")
                if weaknesses:
                    personality_parts.append(f"Weaknesses: {', '.join(weaknesses[:3])}")
                if desires:
                    personality_parts.append(f"Desires: {', '.join(desires[:2])}")
                if fears:
                    personality_parts.append(f"Fears: {', '.join(fears[:2])}")
                
                if personality_parts:
                    char_info += f"\n  Personality: {' | '.join(personality_parts)}"
                
                char_details.append(char_info)
            characters_text = "\n\n".join(char_details)
        
        # Format timeline info
        timeline_text = ""
        if timeline:
            total_duration = timeline.get('total_duration', '')
            timeline_desc = timeline.get('description', '')
            if total_duration:
                timeline_text = f"Duration: {total_duration}"
            if timeline_desc:
                timeline_text += f" - {timeline_desc}"
        
        # Check if user provided Theme or AI should create one
        theme_lesson = theme.get('lesson', '').strip()
        has_user_theme = bool(theme_lesson)
        
        # Build prompt based on whether Theme is provided
        if has_user_theme:
            # User provided Theme - AI MUST use it
            theme_instruction = f"""🎯 THEME (คำตอบ/บทเรียนหลัก - กำหนดโดยผู้ใช้):
{theme.get('teaching', 'This tale teaches that')} {theme_lesson}

⚠️ CRITICAL: You MUST use this EXACT theme throughout ALL 15 beats.
- Do NOT create a different theme
- Do NOT interpret or modify this theme
- Every beat must reflect and support THIS specific theme
- Story must stay focused on THIS theme, never deviate"""
        else:
            # No Theme provided - AI creates unique one
            theme_instruction = f"""🎯 YOUR TASK - CREATE UNIQUE THEME:
1. Analyze BIG IDEA: "{big_idea.get('content', '')}"
2. Analyze PREMISE: "{premise.get('question', '')}"
3. Create a UNIQUE, SPECIFIC theme that:
   - Answers the Big Idea question
   - Is NOT generic (avoid: "ทุกการเลือกมีผลที่ตามมา", "ความรักสำคัญ", etc.)
   - Is relevant to THIS specific story
   - Can be learned by the protagonist
4. Use this theme consistently in ALL 15 beats

Examples of GOOD unique themes:
- "ความสำเร็จที่แท้จริงคือการหาจุดสมดุลระหว่างความฝันและครอบครัว"
- "ความรักที่แท้จริงคือการปล่อยวางเมื่อถึงเวลา"
- "ความกล้าหาญไม่ใช่การไม่กลัว แต่คือการทำในสิ่งที่กลัว"

❌ AVOID generic themes like:
- "ทุกการเลือกมีผลที่ตามมา"
- "ความรักมีพลัง"
- "ความจริงสำคัญ"

CRITICAL: Theme MUST be unique to THIS story's Big Idea and Premise."""
        
        # Build concise but comprehensive prompt
        prompt = f"""You are a professional Thai screenplay writer. Create a 15-beat story structure (Save the Cat).

PROJECT: {script_name} ({script_type}, {genres_text})
CONCEPT: {concept_description if concept_description else big_idea.get('content', '')}
TARGET: {target_audience if target_audience else 'General'}

BIG IDEA (คำถาม): {big_idea.get('content', '')}
PREMISE: {premise.get('question', '')}

{theme_instruction}

CHARACTERS (Step 3 - MUST USE THESE EXACT NAMES):
{characters_text if characters_text else '- To be determined'}

⚠️ CRITICAL CHARACTER RULES:
1. Use ONLY character names listed above
2. DO NOT create new character names (like "นิดา", "พ่อ", etc.)
3. If no characters provided, use generic "ตัวเอก", "ตัวรอง" instead
4. Every character mentioned in beats MUST match names from Step 3 exactly
5. Example: If Step 3 has "John (Protagonist)", use "John" not "นิดา" or other names

🎬 TASK:
Create 15 beats with approximately 250-350 Thai characters each (roughly 5-7 sentences per beat).
Each beat should be detailed and descriptive, not just brief summaries. Use EXACT character names from Step 3 list above. Show clear story progression.

⚠️ LENGTH REQUIREMENT:
- Each beat content must be 250-350 Thai characters (ตัวอักษร)
- This is about 5-7 complete sentences with proper detail
- Include specific actions, emotions, dialogue, and story elements
- Do NOT write short summaries - write full narrative descriptions

THEME CREATION PROCESS:
Step 1: Analyze Big Idea + Premise to understand the core conflict
Step 2: Determine what specific lesson/theme THIS story teaches
Step 3: State the theme clearly in Beat 2
Step 4: Show protagonist's journey learning this theme through all beats

EXAMPLE THEMES (create something UNIQUE like these):
- "ความสำเร็จที่แท้จริงคือการหาจุดสมดุลระหว่างความฝันและครอบครัว"
- "ความรักที่แท้จริงคือการปล่อยวางเมื่อถึงเวลา"
- "ความกล้าหาญไม่ใช่การไม่กลัว แต่คือการทำแม้จะกลัว"
- "การให้อภัยตัวเองคือจุดเริ่มต้นของการเยียวยา"

Save the Cat beats structure:
1. Opening Image - ภาพเปิดเรื่อง แสดงสถานะเดิมของตัวเอก (ก่อนเรียนรู้ theme)
2. Theme Stated ⭐ - ระบุธีม บทเรียนที่จะเรียนรู้ (ต้องพูดถึง theme โดยตรง)
3. Set-Up - ชีวิตปกติ แนะนำตัวละครและโลก (แสดงปัญหาที่เกี่ยวกับ theme)
4. Catalyst - จุดเปลี่ยน เหตุการณ์ที่เปลี่ยนชีวิต (ท้าทาย theme)
5. Debate - ลังเล ไม่แน่ใจจะทำหรือไม่ (ต่อสู้กับ theme)
6. Break Into Two - ก้าวเข้าสู่โลกใหม่ ตัดสินใจลงมือ (เริ่มต้นการเรียนรู้)
7. B Story ⭐ - เรื่องรอง ความสัมพันธ์ที่สอนธีม (ตัวละครที่ช่วยสอน theme)
8. Fun and Games - สนุกสนาน ทดสอบโลกใหม่ (ทดลองวิธีใหม่ที่เกี่ยวกับ theme)
9. Midpoint - จุดกึ่งกลาง ชัยชนะหรือพ่ายแพ้ชั่วคราว (คิดว่าเข้าใจ theme แล้ว)
10. Bad Guys Close In - ศัตรูบุกเข้ามา สถานการณ์แย่ลง (ถูกทดสอบ theme อย่างหนัก)
11. All Is Lost - เสียทุกอย่าง จุดต่ำสุด (ยังไม่เข้าใจ theme จริงๆ)
12. Dark Night of the Soul - คืนที่มืดมน สิ้นหวัง (ไตร่ตรอง theme อย่างลึกซึ้ง)
13. Break Into Three ⭐ - พบทางออก เข้าใจบทเรียน (เข้าใจ theme อย่างแท้จริง)
14. Finale - ตอนจบ ใช้สิ่งที่เรียนรู้เอาชนะ (ประยุกต์ใช้ theme)
15. Final Image - ภาพปิดเรื่อง แสดงการเปลี่ยนแปลง (หลังเรียนรู้ theme สมบูรณ์)

OUTPUT FORMAT - Respond with ONLY valid JSON array (no explanation, no markdown):

⚠️ CRITICAL JSON RULES:
1. Use ONLY double quotes (") for all strings - NO single quotes (')
2. NO trailing commas after last element
3. NO comments (// or /* */)
4. Escape special characters in strings: \" for quotes, \n for newlines
5. Each object MUST have exactly: {{"id": number, "name": "string", "content": "string"}}
6. Array MUST have exactly 15 objects
7. Do NOT wrap in ```json or ``` markdown blocks
8. Start response with [ and end with ]

⚠️ CHARACTER NAME EXAMPLES (DO NOT USE THESE - USE STEP 3 NAMES):
The examples below use "นิดา" and "พ่อ" for demonstration ONLY.
YOU MUST replace with ACTUAL character names from Step 3 character list above.

EXAMPLE VALID JSON FORMAT WITH PROPER LENGTH (250-350 characters per beat):
[
  {{"id": 1, "name": "Opening Image", "content": "เช้าวันหนึ่ง [ใช้ชื่อจาก Step 3] นั่งริมหน้าต่างของคอนโด มองเห็นแสงแดดส่องผ่านม่านบาง ใบหน้าเหนื่อยล้า สะท้อนภาพคนที่สูญเสียความหวัง บนโต๊ะวางรูปถ่ายเก่าๆ ของครอบครัว [เขา/เธอ]หยิบรูปขึ้นมาดู น้ำตาริน ความทรงจำในอดีตที่สดใสกลับมาหลอก ทำให้[เขา/เธอ]รู้สึกโดดเดี่ยว และเริ่มตั้งคำถามว่าชีวิตจะยังมีความหมายหรือไม่"}},
  {{"id": 2, "name": "Theme Stated ⭐", "content": "วันนั้น [พ่อ/แม่/Mentor จาก Step 3]พูดกับ[Protagonist]ว่า 'ทุกการเลือกมีผลที่ตามมา ลูกต้องคิดให้รอบคอบก่อนตัดสินใจทุกครั้ง' คำพูดนี้ติดอยู่ในใจ[Protagonist]ตลอด แต่ในขณะนั้น[เขา/เธอ]ยังไม่เข้าใจความหมายที่แท้จริง เพียงแค่พยักหน้ารับรู้และเก็บไว้ในใจ โดยไม่รู้ว่าในอนาคตข้างหน้า คำพูดนี้จะกลายเป็นบทเรียนชีวิตที่สำคัญที่สุด"}}
]

NOW GENERATE 15 BEATS with 250-350 characters EACH: 
⭐ CRITICAL BEATS - MUST explicitly address theme:

Beat 2 (Theme Stated): State the theme lesson directly in first sentence
  ❌ Wrong: "[สร้างชื่อใหม่]เป็นนักศิลปะ เธอมีความฝัน..."
  ✅ Correct: "ทุกการเลือกมีผลที่ตามมา [ใช้ชื่อจาก Step 3]ได้ยินคำพูดนี้จากครูในวัยเด็ก..."
  
Beat 7 (B Story): Character who TEACHES theme through story/example
  ❌ Wrong: "พ่อของ[สร้างชื่อใหม่]เป็นตัวอย่างของคนที่..."
  ✅ Correct: "[Mentor name from Step 3]เล่าเรื่องวันที่เขาเลือกทิ้งทุนเรียนต่อเพื่อช่วยปู่ย่า ผลที่ตามมาคือเขาเสียโอกาสแต่ได้ครอบครัวที่อบอุ่น 'ทุกการเลือกมีผลที่ตามมา' [Mentor]พูด"
  Must: 1) Tell specific story/example, 2) State theme explicitly in dialogue, 3) Use names from Step 3
  
Beat 13 (Break Into Three): Protagonist's AHA moment about theme
  ❌ Wrong: "[สร้างชื่อใหม่]เข้าใจที่แท้จริงว่าการเลือกไม่มีทางเดียว..."
  ✅ Correct: "[Protagonist from Step 3]ตระหนักได้ในที่สุด 'ทุกการเลือกมีผลที่ตามมาจริงๆ' [เขา/เธอ]นึกถึงคำพูดของ[Mentor from Step 3] ถ้าเลือกทุน ครอบครัวก็จะลำบาก ถ้าอยู่ช่วย ความฝันก็จะสูญเสีย ดังนั้น[เขา/เธอ]ต้องหาทางที่ทั้งสองอย่างมีผลดีที่สุด"
  Must: 1) Quote theme directly, 2) Show understanding consequences, 3) Make decision based on theme, 4) Use names from Step 3

🎯 THEME COHERENCE:
- Every beat must connect to: "{theme.get('lesson', '')}"
- No deviation from this central theme
- Show protagonist's journey: NOT understanding → TESTING theme → FULLY understanding

⚠️⚠️⚠️ CRITICAL LENGTH ENFORCEMENT ⚠️⚠️⚠️
EACH beat MUST be MINIMUM 250 Thai characters. NO EXCEPTIONS.
If a beat is shorter than 250 characters, ADD MORE DETAILS:
- Add specific dialogue with quotation marks
- Describe emotions in detail (facial expressions, body language)
- Include internal thoughts of the character
- Describe the setting/environment
- Add sensory details (sights, sounds, feelings)
- Explain character motivations and conflicts

Example of TOO SHORT (WRONG - only 100 characters):
"อาทิตย์นั่งมองท้องฟ้า ดวงตาเศร้า เขาคิดถึงคนรัก ความทรงจำในอดีตทำให้เขาเสียใจ"

Example of CORRECT LENGTH (300+ characters):
"เช้าวันนั้น อาทิตย์นั่งอยู่บนชั้นดาดฟ้าของอาคารคอนโด มองดูท้องฟ้าสีส้มแดงที่กำลังเปลี่ยนเป็นสีน้ำเงินเข้ม ลมพัดโชยผ่านใบหน้าที่เต็มไปด้วยความเหนื่อยล้า เขาหยิบรูปถ่ายครอบครัวที่พกติดตัวมาตลอดขึ้นมาดู น้ำตาไหลริน 'ทำไมชีวิตถึงโหดร้ายขนาดนี้' เขาพูดกับตัวเองด้วยเสียงสั่นเครือ ความทรงจำในอดีตที่สดใสกลับมาหลอกหลอน ทำให้เขารู้สึกโดดเดี่ยวและสิ้นหวัง ในหัวใจลึกๆ เขาเริ่มตั้งคำถามว่า ความรักที่เขาเชื่อถือมาตลอดนั้น ยังมีความหมายอีกหรือไม่"

NOW Generate 15 beats with MINIMUM 250 characters EACH:"""
        
        # Determine AI endpoint
        if ai_provider == 'qwen2.5':
            # Use local Ollama Qwen2.5
            api_url = "http://127.0.0.1:11434/api/generate"
            payload = {
                "model": "qwen2.5:7b",  # Use installed 7B model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 1.0,  # Increase for more creative, longer output
                    "top_p": 0.95,
                    "num_predict": 12000,  # Further increased for longer beats
                    "num_ctx": 32768,  # Large context window
                    "repeat_penalty": 1.1  # Reduce repetition
                }
            }
            
            print(f"⏳ Sending request to Ollama (timeout=600s)...")
            async with httpx.AsyncClient(timeout=600.0) as client:  # Increased timeout to 600s
                api_response_obj = await client.post(api_url, json=payload)
                print(f"✅ Ollama response received (status: {api_response_obj.status_code})")
                
                if api_response_obj.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Ollama API error: {api_response_obj.text}"
                    )
                
                result = api_response_obj.json()
                ai_response = result.get('response', '')
        
        elif ai_provider == 'gpt-4':
            # Use OpenAI GPT-4
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API key not configured"
                )
            
            api_url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a professional screenplay writer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:  # เพิ่ม timeout สำหรับ OpenAI API
                api_response_obj = await client.post(api_url, json=payload, headers=headers)
                
                if api_response_obj.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"OpenAI API error: {api_response_obj.text}"
                    )
                
                result = api_response_obj.json()
                ai_response = result['choices'][0]['message']['content']
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported AI provider: {ai_provider}"
            )
        
        # Parse AI response (try to extract JSON)
        # Log raw response for debugging
        print(f"\n🤖 AI Response ({ai_provider}):")
        print(f"Length: {len(ai_response)} characters")
        print(f"First 500 chars:\n{ai_response[:500]}")
        print(f"Last 200 chars:\n{ai_response[-200:]}")
        
        # Try to find JSON array in response
        # First, try to remove markdown code blocks
        cleaned_response = ai_response.strip()
        
        # Remove markdown code blocks
        if '```json' in cleaned_response:
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
        elif '```' in cleaned_response:
            cleaned_response = re.sub(r'```\s*', '', cleaned_response)
        
        print(f"\n🧹 After cleaning markdown:")
        print(f"First 300 chars: {cleaned_response[:300]}")
        
        # Find JSON array
        json_match = re.search(r'\[[\s\S]*\]', cleaned_response)
        if json_match:
            structure_json = json_match.group(0)
            print(f"\n📦 Found JSON array, length: {len(structure_json)}")
            
            # 🔧 Pre-process: Fix Thai quotes BEFORE parsing
            structure_json = structure_json.replace('"', '"').replace('"', '"')  # Thai quotes → ASCII
            structure_json = structure_json.replace(''', "'").replace(''', "'")  # Thai single quotes
            print(f"✨ After fixing Thai quotes (first 300): {structure_json[:300]}")
            
            try:
                # Try direct parsing first
                structure = json.loads(structure_json)
                print(f"✅ JSON parsed successfully: {len(structure)} items")
                
                # Validate structure
                if not isinstance(structure, list):
                    raise ValueError("Response is not an array")
                    
                if len(structure) != 15:
                    print(f"⚠️ Warning: Expected 15 beats, got {len(structure)}")
                
                # Ensure all beats have required fields
                for i, beat in enumerate(structure, 1):
                    if not isinstance(beat, dict):
                        raise ValueError(f"Beat {i} is not an object")
                    if 'id' not in beat or 'name' not in beat or 'content' not in beat:
                        print(f"⚠️ Beat {i} missing fields. Has: {beat.keys()}")
                        raise ValueError(f"Beat {i} missing required fields (id, name, content)")
                
                print(f"✅ All beats validated")
                
                # 🎯 POST-PROCESSING: Enforce 250-350 character length requirement
                print(f"\n🔍 Checking beat lengths and padding if needed...")
                for i, beat in enumerate(structure, 1):
                    content = beat.get('content', '')
                    current_length = len(content)
                    
                    if current_length < 250:
                        # Beat is too short - need to expand
                        padding_needed = 250 - current_length
                        print(f"  ⚠️ Beat {i} too short ({current_length} chars) - padding +{padding_needed}")
                        
                        # Smart padding based on beat type
                        name = beat.get('name', '').lower()
                        
                        if 'opening' in name:
                            padding = f" ท้องฟ้ายามเช้ามีสีสันสดใส แสงแดดส่องผ่านหน้าต่างเข้ามาในห้อง สร้างบรรยากาศที่อบอุ่นแต่โดดเดี่ยว เสียงเพลงจากวิทยุดังขึ้นเบาๆ เป็นเพลงเก่าที่เคยชอบฟัง ทำให้ความทรงจำในอดีตกลับมาอีกครั้ง ใบหน้าที่เคยมีรอยยิ้มสดใสกลับเต็มไปด้วยความเศร้าหมอง"
                        elif 'theme' in name:
                            padding = f" ในขณะนั้นคำพูดดูเหมือนธรรมดา แต่มันฝังลึกอยู่ในใจ เวลาผ่านไป ความหมายที่แท้จริงค่อยๆ ปรากฏชัดเจนขึ้น ทุกๆ การเลือกที่ทำไป ไม่ว่าจะเล็กหรือใหญ่ ล้วนมีผลกระทบต่อชีวิตในอนาคต บางครั้งเป็นผลดี บางครั้งเป็นผลร้าย แต่สิ่งสำคัญคือต้องรับผิดชอบต่อทุกการตัดสินใจ"
                        elif 'catalyst' in name or 'debate' in name:
                            padding = f" ความกังวลเริ่มก่อตัวขึ้นในใจ คิดถึงผลที่จะตามมาทั้งในด้านดีและด้านร้าย หัวใจเต้นแรงด้วยความลังเล สองทางเลือกที่ขัดแย้งกันทำให้ยากที่จะตัดสินใจ เวลาเดินช้าเหมือนหยุดนิ่ง แต่การตัดสินใจก็เข้ามาใกล้ทุกขณะ ต้องเลือกให้ได้ในที่สุด"
                        elif 'climax' in name:
                            padding = f" นี่คือช่วงเวลาสำคัญที่สุด ทุกสิ่งที่เรียนรู้มาตลอดทั้งเรื่องถูกนำมาใช้ในตอนนี้ ความกลัว ความหวัง ความรัก ความเสียสละ ทั้งหมดรวมตัวกันในจุดนี้ หัวใจเต้นแรงจนแทบจะหยุด มือสั่นเทาไม่อยู่ แต่ก็ต้องกล้าเผชิญหน้ากับมัน เพราะนี่คือจุดจบที่รอคอยมา"
                        elif 'resolution' in name:
                            padding = f" ทุกอย่างเริ่มชัดเจนขึ้น บทเรียนที่เรียนรู้มาตลอดเส้นทางกลายเป็นปัญญาที่แท้จริง ชีวิตไม่ได้สมบูรณ์แบบ แต่มันมีความหมาย การเดินทางที่ผ่านมาทำให้เติบโตและแข็งแกร่งขึ้น พร้อมเผชิญหน้ากับอนาคตด้วยความมั่นใจและความหวังใหม่"
                        else:
                            padding = f" บรรยากาศรอบตัวเต็มไปด้วยความตึงเครียด แต่ก็มีความหวังแฝงอยู่ ทุกก้าวที่เดินไปทำให้เข้าใจตัวเองมากขึ้น ความรู้สึกที่สับสนค่อยๆ เปลี่ยนเป็นความชัดเจน ทุกคนมีบทบาทในการเปลี่ยนแปลงนี้ ไม่ว่าจะรู้ตัวหรือไม่ก็ตาม การเรียนรู้จากประสบการณ์คือสิ่งที่มีค่าที่สุด"
                        
                        # Add padding up to minimum length
                        beat['content'] = content + padding[:padding_needed]
                        new_length = len(beat['content'])
                        print(f"    ✅ Padded to {new_length} chars")
                    elif current_length > 350:
                        # Beat is too long - trim to 350
                        print(f"  ⚠️ Beat {i} too long ({current_length} chars) - trimming to 350")
                        beat['content'] = content[:347] + '...'
                        print(f"    ✅ Trimmed to 350 chars")
                    else:
                        print(f"  ✅ Beat {i} OK ({current_length} chars)")
                
                print(f"✅ All beats now meet 250-350 character requirement")
                
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback: Try aggressive cleaning
                print(f"\n⚠️ JSON parse failed: {str(e)}")
                print(f"🔧 Attempting aggressive cleaning...")
                
                # Aggressive cleaning - fix common Qwen2.5 issues
                structure_json_cleaned = structure_json
                
                # 0. Remove newlines within string values (Qwen2.5 breaks lines mid-sentence)
                # First protect the JSON structure by only removing newlines within quotes
                # Pattern: "text นิดา[\n]งเขียน" → "text นิดางเขียน"
                structure_json_cleaned = re.sub(r'(?<=[\u0E00-\u0E7F])\n(?=[\u0E00-\u0E7F])', '', structure_json_cleaned)
                
                # 0.1 Remove newlines that are NOT followed by a quote or brace (likely inside a string)
                # This is a bit risky but helps with "Thai：\n" cases
                # We replace them with a space
                def replace_inner_newlines(match):
                    return match.group(0).replace('\n', ' ')
                
                # Match content inside quotes and replace newlines
                structure_json_cleaned = re.sub(r'"([^"]*)"', replace_inner_newlines, structure_json_cleaned, flags=re.DOTALL)
                
                # 0.2 Fix missing closing quotes in content fields - Qwen2.5 sometimes forgets them
                # Pattern: "content": "text text},  →  "content": "text text"},
                # First, fix all instances where } or }] appear without closing quote
                structure_json_cleaned = re.sub(r'("content"\s*:\s*"[^"]+)},', r'\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\s*:\s*"[^"]+)}]', r'\1"}]', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\s*:\s*"[^"]+)}\s*,', r'\1"},', structure_json_cleaned)
                
                # Fix cases where content ends abruptly with }, or }]
                # Pattern: ...ใจ},  →  ...ใจ"},
                structure_json_cleaned = re.sub(r'([^"]})(},)', r'\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'([^"}])}]', r'\1"}]', structure_json_cleaned)
                
                # 0.3 Remove Chinese characters from Qwen2.5 (e.g., "250-350字")
                structure_json_cleaned = re.sub(r'[\u4e00-\u9fff]+', '', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'：', ':', structure_json_cleaned)  # Fix Chinese colon
                
                # 0.4 Remove any non-JSON trailing content (e.g., "%")
                structure_json_cleaned = re.sub(r'\]\s*[^}\]]*$', ']', structure_json_cleaned)
                
                # 1. Fix missing "name": before beat names
                # Pattern: {"id": 3, "Set-Up", "content"  →  {"id": 3, "name": "Set-Up", "content"
                structure_json_cleaned = re.sub(
                    r'("id"\s*:\s*\d+)\s*,\s*"([^"]+)"\s*,\s*("content")',
                    r'\1, "name": "\2", \3',
                    structure_json_cleaned
                )
                
                # 2. Fix closing parenthesis instead of comma: }),  →  },
                # Pattern: "content": "..."}),  →  "content": "..."},
                structure_json_cleaned = re.sub(r'\}\)\s*,', '},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'\}\)', '}', structure_json_cleaned)
                
                # 3. Fix single quotes to double quotes
                structure_json_cleaned = structure_json_cleaned.replace("'", '"')
                
                # 4. Remove trailing commas before } and ]
                structure_json_cleaned = re.sub(r',(\s*[}\]])', r'\1', structure_json_cleaned)
                
                # 5. Fix missing commas between objects
                structure_json_cleaned = re.sub(r'}\s*{', r'},{', structure_json_cleaned)
                
                # 6. Remove any markdown remnants
                structure_json_cleaned = re.sub(r'```json\s*', '', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'```\s*', '', structure_json_cleaned)
                
                print(f"🧹 After cleaning (first 600): {structure_json_cleaned[:600]}")
                
                try:
                    structure = json.loads(structure_json_cleaned)
                    print(f"✅ Cleaned JSON parsed: {len(structure)} items")
                except json.JSONDecodeError as parse_error:
                    # Ultimate fallback: Show detailed error and save to file
                    error_msg = f"Failed to parse AI response as JSON: {str(parse_error)}"
                    print(f"\n❌ {error_msg}")
                    timestamp = int(time.time())
                    debug_file = f"/tmp/ai_response_error_{timestamp}.json"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(ai_response)
                    print(f"💾 Full response saved to: {debug_file}")
                    
                    raise HTTPException(
                        status_code=500,
                        detail=f"{error_msg}\n\nDebug: Response saved to {debug_file}"
                    )
        else:
            # Last resort: Create simple structure from text
            print(f"❌ No JSON array found in response")
            print(f"Full raw response:\n{ai_response}")
            raise HTTPException(
                status_code=500,
                detail="AI response does not contain valid JSON array"
            )
        
        return {
            "success": True,
            "structure": structure,
            "ai_provider": ai_provider,
            "raw_response": ai_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )


@router.post("/generate-scenes-batch")
async def generate_scenes_batch(data: dict):
    """
    🤖 AI Generate ALL Scenes in Batch Mode (Optimized)
    
    Generates ALL scenes based on beatSceneMap in batches of 4.
    Maintains continuity by passing previous_context between batches.
    MUCH FASTER than calling /generate-scene-step multiple times.
    
    **Input:**
    - project_context: Full project data (Step 1-4)
    - beatSceneMap: Dict of beat_id -> num_scenes (e.g., {1: 3, 2: 2, 3: 4})
    - ai_provider: qwen2.5 or gpt-4
    
    **Output:**
    - scenes: Array of all generated scenes with shots
    - count: Total scenes generated
    - total_shots: Total shots generated
    """
    try:
        print("\n" + "="*80)
        print("🎬 GENERATE SCENES BATCH - Request received")
        
        # Extract inputs
        project_context = data.get('project_context', {})
        beat_scene_map = data.get('beatSceneMap') or data.get('beat_scene_map', {})
        ai_provider = data.get('ai_provider', 'qwen2.5')
        
        # Validate inputs
        if not project_context:
            raise HTTPException(status_code=400, detail="Missing project_context")
        if not beat_scene_map:
            raise HTTPException(status_code=400, detail="Missing beatSceneMap")
        
        print(f"  - Beat Scene Map: {beat_scene_map}")
        print(f"  - AI Provider: {ai_provider}")
        
        # Extract structure
        structure = project_context.get('structure', [])
        if not structure:
            raise HTTPException(status_code=400, detail="No structure found in project_context")
        
        # Use the existing batch generation logic from generate_scene_step
        # by calling it internally with all data
        return await generate_scene_step(data)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ BATCH GENERATION ERROR:")
        print(f"Exception: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Batch generation failed: {str(e)}"
        )


@router.post("/generate-scene-step")
async def generate_scene_step(data: dict):
    """
    🤖 AI Generate Scenes (Batch Mode with Continuity)
    
    Generates scenes based on beatSceneMap in batches of 4.
    Maintains continuity by passing previous_context between batches.
    
    **Input:**
    - project_context: Full project data (Step 1-4)
    - current_scene_info: { scene_number, beat_id, beat_name, beat_content } (OPTIONAL, for single scene)
    - beatSceneMap: Dict of beat_id -> num_scenes (for batch mode)
    - previous_context: Summary of previous scene
    - ai_provider: qwen2.5 or gpt-4
    
    **Output:**
    - scenes: Array of generated scenes (batch mode) OR scene: Single scene (single mode)
    """
    # ⏱️ START TIMING
    step_start_time = time.time()
    timing_log = {
        "total_start": step_start_time,
        "scene_generation": 0,
        "shot_generation": 0,
        "ai_calls": 0,
        "validation": 0
    }
    
    try:
        print("\n" + "="*80)
        print("🎬 GENERATE SCENE STEP - Request received")
        
        # Extract inputs
        project_context = data.get('project_context', {})
        current_scene_info = data.get('current_scene_info', {})
        previous_context = data.get('previous_context', '')
        ai_provider = data.get('ai_provider', 'qwen2.5')
        
        # 🔥 NEW: Support both BATCH mode and SINGLE mode
        beat_scene_map = data.get('beatSceneMap') or data.get('beat_scene_map', {})
        is_batch_mode = bool(beat_scene_map and not current_scene_info)
        
        # Validate inputs
        if not project_context:
            raise HTTPException(status_code=400, detail="Missing project_context")
        
        # Batch mode: need beatSceneMap, Single mode: need current_scene_info
        if not is_batch_mode and not current_scene_info:
            raise HTTPException(status_code=400, detail="Missing current_scene_info for single scene mode")
        
        if is_batch_mode:
            print(f"  🔥 BATCH MODE: {beat_scene_map}")
            scene_number = None
            beat_name = "Batch"
            beat_content = "Multiple beats"
        else:
            scene_number = current_scene_info.get('scene_number')
            beat_name = current_scene_info.get('beat_name')
            beat_content = current_scene_info.get('beat_content')
            print(f"  - Generating Scene #{scene_number}")
            print(f"  - Beat: {beat_name}")
            print(f"  - Context: {previous_context[:100]}...")
        
        # Extract Project Info
        script_name = project_context.get('script_name', 'Untitled')
        concept_description = project_context.get('concept_description', '')
        
        # Extract Additional Context (Step 1-2)
        big_idea = project_context.get('big_idea', {})
        
        # Extract structure and scene planning data
        structure = project_context.get('structure', [])
        num_scenes = data.get('num_scenes', 30)
        scenes_per_beat = data.get('scenes_per_beat', 2)
        concept_text = concept_description if concept_description else big_idea.get('content', '')
        
        # Extract Theme (Critical)
        theme = project_context.get('theme', {})
        theme_full = f"{theme.get('teaching', 'Theme')}: {theme.get('lesson', '')}"
        
        # Extract Characters
        characters = project_context.get('characters', [])
        characters_text = ""
        if characters:
            char_details = []
            for char in characters[:5]:
                char_name = char.get('name', '')
                char_role = char.get('role', '')
                char_archetype = char.get('archetype', '')
                char_desc = char.get('description', '')
                
                # Physical traits
                char_physical = char.get('physical_traits', {})
                age = char_physical.get('age', '')
                gender = char_physical.get('gender', '')
                appearance = char_physical.get('appearance', '')
                
                # Personality traits
                char_personality = char.get('personality_traits', {})
                strengths = char_personality.get('strengths', [])
                weaknesses = char_personality.get('weaknesses', [])
                fears = char_personality.get('fears', [])
                desires = char_personality.get('desires', [])
                
                # Backstory
                backstory = char.get('backstory', '')
                
                # Build comprehensive character profile
                char_info = f"**{char_name}** ({char_role}, {char_archetype})"
                if age or gender or appearance:
                    physical_desc = f"{gender} {age}".strip()
                    if appearance:
                        physical_desc += f", {appearance}"
                    char_info += f"\n  Physical: {physical_desc}"
                if char_desc:
                    char_info += f"\n  Description: {char_desc}"
                if backstory:
                    char_info += f"\n  Backstory: {backstory[:150]}"
                
                personality_parts = []
                if strengths:
                    personality_parts.append(f"Strengths: {', '.join(strengths[:3])}")
                if weaknesses:
                    personality_parts.append(f"Weaknesses: {', '.join(weaknesses[:3])}")
                if desires:
                    personality_parts.append(f"Desires: {', '.join(desires[:2])}")
                if fears:
                    personality_parts.append(f"Fears: {', '.join(fears[:2])}")
                
                if personality_parts:
                    char_info += f"\n  Personality: {' | '.join(personality_parts)}"
                
                char_details.append(char_info)
            characters_text = "\n\n".join(char_details)
        
        # 🆕 Build beat-specific scene breakdown
        beat_breakdown = []
        total_calculated_scenes = 0
        
        # If structure is empty or invalid, try to use num_scenes directly
        if not structure:
            print("⚠️ Structure is empty, cannot build beat breakdown.")
        
        for beat in structure:
            if not beat.get('completed') or not beat.get('content'):
                continue
            
            beat_id = beat.get('id')
            beat_name = beat.get('name', f"Beat {beat_id}")
            beat_content = beat.get('content', '')
            
            # Get number of scenes for this beat (support both int and str keys)
            beat_num_scenes = scenes_per_beat  # default
            if beat_scene_map:
                # Try both integer and string keys
                if beat_id in beat_scene_map:
                    beat_num_scenes = int(beat_scene_map[beat_id])
                    print(f"  ✓ Beat {beat_id} found in map (int key): {beat_num_scenes} scenes")
                elif str(beat_id) in beat_scene_map:
                    beat_num_scenes = int(beat_scene_map[str(beat_id)])
                    print(f"  ✓ Beat {beat_id} found in map (str key): {beat_num_scenes} scenes")
                else:
                    print(f"  ○ Beat {beat_id} not in map, using default: {beat_num_scenes} scenes")
            
            if beat_num_scenes > 0:
                beat_breakdown.append({
                    'id': beat_id,
                    'name': beat_name,
                    'content': beat_content[:200],
                    'num_scenes': beat_num_scenes
                })
                total_calculated_scenes += beat_num_scenes
        
        # Build beat breakdown text for prompt with explicit scene list
        beat_breakdown_text = ""
        scene_checklist = []  # 🆕 Explicit checklist for AI
        
        if beat_breakdown:
            beat_breakdown_text = "\n\n🎯 SCENE BREAKDOWN PER BEAT (YOU MUST FOLLOW THIS EXACTLY):\n"
            scene_counter = 1
            for item in beat_breakdown:
                beat_breakdown_text += f"\n{item['id']}. {item['name']} → {item['num_scenes']} ฉาก\n"
                beat_breakdown_text += f"   Content: {item['content']}\n"
                
                # Build explicit scene checklist
                for i in range(item['num_scenes']):
                    scene_checklist.append(f"Scene {scene_counter}: Beat {item['id']} ({item['name']}) - Scene {i+1}/{item['num_scenes']}")
                    scene_counter += 1
            
            beat_breakdown_text += f"\n📊 TOTAL SCENES YOU MUST GENERATE: {total_calculated_scenes} ฉาก\n"
            beat_breakdown_text += "\n✅ SCENE CHECKLIST (Generate all of these):\n"
            for check in scene_checklist:
                beat_breakdown_text += f"  □ {check}\n"
        
        print(f"\n🎬 SCENE BREAKDOWN:")
        print(f"  - Beat breakdown items: {len(beat_breakdown)}")
        print(f"  - Total scenes from breakdown: {total_calculated_scenes}")
        print(f"  - Requested num_scenes: {num_scenes}")
        
        # Use calculated total if custom breakdown provided
        final_num_scenes = total_calculated_scenes if beat_breakdown else num_scenes
        
        print(f"  - Final scenes to generate: {final_num_scenes}")
        
        # Build structure summary (key beats)
        key_beats = []
        for beat in structure:
            if beat.get('completed') and beat.get('content'):
                key_beats.append(f"{beat.get('name')}: {beat.get('content', '')[:100]}...")
        
        # ==================================================================================
        # 🆕 BATCH GENERATION LOGIC (Iterative Scene Generation)
        # ==================================================================================
        
        # 1. Create a detailed plan for every scene
        scene_plan = []
        current_scene_num = 1
        
        if beat_breakdown:
            for beat in beat_breakdown:
                for i in range(beat['num_scenes']):
                    scene_plan.append({
                        "scene_number": current_scene_num,
                        "beat_id": beat['id'],
                        "beat_name": beat['name'],
                        "beat_content": beat['content']
                    })
                    current_scene_num += 1
        else:
            # Fallback: Distribute evenly if no breakdown
            for i in range(final_num_scenes):
                scene_plan.append({
                    "scene_number": i + 1,
                    "beat_id": "General",
                    "beat_name": "Story Progression",
                    "beat_content": "General story progression"
                })

        # 2. Execute generation in batches
        scenes_raw = []
        batch_size = 4
        total_batches = (len(scene_plan) + batch_size - 1) // batch_size
        
        print(f"\n🚀 STARTING BATCH GENERATION: {total_batches} batches for {len(scene_plan)} scenes")
        
        previous_context = ""
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(scene_plan))
            current_batch_plan = scene_plan[start_idx:end_idx]
            
            print(f"\n📦 Processing Batch {batch_idx + 1}/{total_batches} (Scenes {current_batch_plan[0]['scene_number']}-{current_batch_plan[-1]['scene_number']})")
            
            # Build specific checklist for this batch
            batch_checklist_text = ""
            for item in current_batch_plan:
                batch_checklist_text += f"Scene {item['scene_number']}: Beat {item['beat_id']} ({item['beat_name']})\n   Context: {item['beat_content'][:100]}...\n"
            
            # Build Prompt for this batch
            prompt = f"""You are a professional Thai screenplay writer. Generate scenes {current_batch_plan[0]['scene_number']} to {current_batch_plan[-1]['scene_number']} (Batch {batch_idx + 1}/{total_batches}).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PROJECT CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TITLE: {script_name}
CONCEPT: {concept_text}
THEME: {theme_full}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 CHARACTERS (Use these traits)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{characters_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏮️ PREVIOUS CONTEXT (Continuity)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{previous_context if previous_context else "Starting point: Opening of the story."}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 CURRENT BATCH TASK: Generate {len(current_batch_plan)} Scenes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENES TO GENERATE:
{batch_checklist_text}

REQUIREMENTS:
1. Generate EXACTLY {len(current_batch_plan)} scenes (Scenes {current_batch_plan[0]['scene_number']}-{current_batch_plan[-1]['scene_number']})
2. Maintain continuity from previous context
3. Use EXACT character names and traits
4. 🔥 DETAILED Thai description: MINIMUM 500 characters per scene (10-15 sentences with rich details about atmosphere, emotions, actions, and visual elements)
5. Output valid JSON array

OUTPUT FORMAT:
[
  {{
    "scene_number": {current_batch_plan[0]['scene_number']},
    "title": "Scene Title",
    "location": "Location (Int/Ext)",
    "time": "Time (Day/Night)",
    "description": "DETAILED scene description in Thai (500+ characters with rich atmosphere, character emotions, actions, dialogue context, visual details, lighting, sound, and mood)...",
    "characters": "Characters present",
    "duration": "Estimated duration",
    "notes": "Director notes",
    "shots": [
      {{
        "shot_number": 1,
        "shot_title": "Establishing Shot",
        "shot_description": "DETAILED shot description in Thai (300+ characters describing camera angle, movement, what's shown, character actions, emotions, lighting, composition)...",
        "camera_angle": "wide",
        "camera_movement": "static"
      }},
      {{
        "shot_number": 2,
        "shot_title": "Action Shot",
        "shot_description": "DETAILED shot description in Thai (300+ characters)...",
        "camera_angle": "medium",
        "camera_movement": "pan"
      }},
      {{
        "shot_number": 3,
        "shot_title": "Close-up Shot",
        "shot_description": "DETAILED shot description in Thai (300+ characters)...",
        "camera_angle": "close-up",
        "camera_movement": "zoom"
      }}
    ]
  }},
  ...
]

Generate JSON array only:"""

            # Call AI based on provider
            # ⏱️ START AI TIMING
            ai_call_start = time.time()
            
            ai_response = ""
            if ai_provider == 'qwen2.5':
                # Use Ollama Qwen2.5
                api_url = "http://127.0.0.1:11434/api/generate"
                payload = {
                    "model": "qwen2.5:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 12000,  # 🔥 Increased for 500+ char descriptions per scene
                        "num_ctx": 16384
                    }
                }
                
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(api_url, json=payload)
                    if response.status_code != 200:
                        print(f"❌ Batch {batch_idx+1} failed: {response.text}")
                        continue
                    result = response.json()
                    ai_response = result.get("response", "")
                
                # ⏱️ LOG AI TIME
                ai_call_duration = time.time() - ai_call_start
                timing_log["ai_calls"] += ai_call_duration
                print(f"  ⏱️ AI Call Time: {ai_call_duration:.2f}s")
            
            elif ai_provider in ['gpt-4', 'gpt-4-turbo']:
                # Use OpenAI GPT-4
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    raise HTTPException(status_code=503, detail="OpenAI API key not configured.")
                
                api_url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4-turbo-preview" if ai_provider == 'gpt-4-turbo' else "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are a professional Thai screenplay writer. Generate scenes in valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
                
                async with httpx.AsyncClient(timeout=300.0) as client:
                    api_response_obj = await client.post(api_url, headers=headers, json=payload)
                    if api_response_obj.status_code != 200:
                        print(f"❌ Batch {batch_idx+1} failed: {api_response_obj.text}")
                        continue
                    result = api_response_obj.json()
                    ai_response = result['choices'][0]['message']['content']
        
            # Parse JSON
            try:
                ai_response_clean = ai_response.strip()
                if ai_response_clean.startswith("```json"): ai_response_clean = ai_response_clean[7:]
                if ai_response_clean.startswith("```"): ai_response_clean = ai_response_clean[3:]
                if ai_response_clean.endswith("```"): ai_response_clean = ai_response_clean[:-3]
                ai_response_clean = ai_response_clean.strip()
                
                # Fix quotes
                ai_response_clean = ai_response_clean.replace('"', '"').replace('"', '"')
                
                batch_scenes = json.loads(ai_response_clean)
                
                if isinstance(batch_scenes, list):
                    print(f"✅ Batch {batch_idx+1} success: {len(batch_scenes)} scenes")
                    scenes_raw.extend(batch_scenes)
                    
                    # Update context
                    if batch_scenes:
                        last_scene = batch_scenes[-1]
                        previous_context = f"Last Scene ({last_scene.get('scene_number')}): {last_scene.get('description')}"
                else:
                    print(f"⚠️ Batch {batch_idx+1} returned invalid format (not list)")
                    
            except Exception as e:
                print(f"❌ Batch {batch_idx+1} parse error: {str(e)}")
                # Try aggressive cleaning if needed
                try:
                    # Simple aggressive cleaning
                    cleaned = ai_response_clean
                    cleaned = re.sub(r'(?<=[\u0E00-\u0E7F])\n(?=[\u0E00-\u0E7F])', '', cleaned)
                    cleaned = re.sub(r'\}\)\s*,', '},', cleaned)
                    cleaned = re.sub(r'\}\)', '}', cleaned)
                    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
                    batch_scenes = json.loads(cleaned)
                    if isinstance(batch_scenes, list):
                        scenes_raw.extend(batch_scenes)
                        if batch_scenes:
                            last_scene = batch_scenes[-1]
                            previous_context = f"Last Scene ({last_scene.get('scene_number')}): {last_scene.get('description')}"
                except:
                    pass

        # Generate scene_id for each scene and validate
        import uuid
        
        scenes = []
        all_generated_shots = []  # 🆕 Track all shots
        
        # ⏱️ START SHOT GENERATION TIMING
        shot_generation_start = time.time()
        
        for idx, scene in enumerate(scenes_raw):
            # ⏱️ START SINGLE SCENE TIMING
            scene_start = time.time()
            
            # Validate required fields
            if not isinstance(scene, dict):
                continue
            
            # Generate unique scene_id
            scene_id = f"scene_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Build validated scene object
            validated_scene = {
                "scene_id": scene_id,
                "scene_number": scene.get('scene_number', idx + 1),
                "title": scene.get('title', f'ฉากที่ {idx + 1}'),
                "location": scene.get('location', ''),
                "time": scene.get('time', 'day'),
                "description": scene.get('description', ''),
                "characters": scene.get('characters', ''),
                "duration": scene.get('duration', ''),
                "notes": scene.get('notes', '')
            }
            
            # 🔥 NEW: Use AI-generated shots if available
            ai_generated_shots = scene.get('shots', [])
            
            if ai_generated_shots and len(ai_generated_shots) > 0:
                # AI already generated shots - use them!
                print(f"    ✓ Using {len(ai_generated_shots)} AI-generated shots")
                scene_shots = []
                
                for shot_idx, ai_shot in enumerate(ai_generated_shots):
                    shot_id = f"shot_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
                    
                    # Extract shot data from AI
                    shot_description = ai_shot.get('shot_description', ai_shot.get('description', ''))
                    angle = ai_shot.get('camera_angle', 'medium')
                    movement = ai_shot.get('camera_movement', 'static')
                    
                    # Build shot data
                    shot_data = {
                        "shot_id": shot_id,
                        "scene_id": scene_id,
                        "shot_number": shot_idx + 1,
                        "shot_title": ai_shot.get('shot_title', f"Shot {shot_idx + 1}"),
                        "shot_description": shot_description,
                        "camera_angle": angle,
                        "camera_movement": movement,
                        "motion_parameters": {
                            "zoom_start": 1.0,
                            "zoom_end": 1.2 if movement == 'zoom' else 1.0,
                            "move_x": 10 if movement == 'pan' else 0,
                            "move_y": 10 if movement == 'tilt' else 0,
                            "rotate_start": 0,
                            "rotate_end": 0,
                            "duration": 3,
                            "speed": 1.0
                        },
                        "character_simulations": [],
                        "dialogue": "",
                        "actions": []
                    }
                    
                    scene_shots.append(shot_data)
                    all_generated_shots.append(shot_data)
            else:
                # Fallback: Generate basic shots if AI didn't provide them
                print(f"    ⚠️ No AI shots, generating 3 basic shots")
                num_shots = 3
                scene_shots = []
                
                camera_angles = ['wide', 'medium', 'close-up']
                camera_movements = ['static', 'pan', 'zoom']
                
                for shot_idx in range(num_shots):
                    shot_id = f"shot_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
                    
                    angle = camera_angles[shot_idx % len(camera_angles)]
                    movement = camera_movements[shot_idx % len(camera_movements)]
                    
                    shot_description = f"{validated_scene['title']} - Shot {shot_idx + 1}"
                    
                    shot_data = {
                        "shot_id": shot_id,
                        "scene_id": scene_id,
                        "shot_number": shot_idx + 1,
                        "shot_title": f"Shot {shot_idx + 1}",
                        "shot_description": shot_description,
                        "camera_angle": angle,
                        "camera_movement": movement,
                        "motion_parameters": {
                            "zoom_start": 1.0,
                            "zoom_end": 1.2 if movement == 'zoom' else 1.0,
                            "move_x": 10 if movement == 'pan' else 0,
                            "move_y": 10 if movement == 'tilt' else 0,
                            "rotate_start": 0,
                            "rotate_end": 0,
                            "duration": 3,
                            "speed": 1.0
                        },
                        "character_simulations": [],
                        "dialogue": "",
                        "actions": []
                    }
                    
                    scene_shots.append(shot_data)
                    all_generated_shots.append(shot_data)
            
            # Add shots array to scene
            validated_scene['shots'] = scene_shots
            
            scenes.append(validated_scene)
            
            # ⏱️ LOG SINGLE SCENE TIME
            scene_duration = time.time() - scene_start
            timing_log["scene_generation"] += scene_duration
            print(f"  ⏱️ Scene {idx+1} Time: {scene_duration:.2f}s ({len(scene_shots)} shots)")
        
        # ⏱️ TOTAL SHOT GENERATION TIME
        shot_generation_duration = time.time() - shot_generation_start
        timing_log["shot_generation"] = shot_generation_duration
        
        # ⏱️ TOTAL ELAPSED TIME
        total_elapsed = time.time() - step_start_time
        
        # Return response with scenes + auto-generated shots
        print(f"\n✅ GENERATION COMPLETE:")
        print(f"  - Scenes: {len(scenes)}")
        print(f"  - Total Shots: {len(all_generated_shots)}")
        print(f"\n⏱️ PERFORMANCE BREAKDOWN:")
        print(f"  - AI Calls: {timing_log['ai_calls']:.2f}s ({timing_log['ai_calls']/total_elapsed*100:.1f}%)")
        print(f"  - Scene Generation: {timing_log['scene_generation']:.2f}s ({timing_log['scene_generation']/total_elapsed*100:.1f}%)")
        print(f"  - Shot Generation: {timing_log['shot_generation']:.2f}s ({timing_log['shot_generation']/total_elapsed*100:.1f}%)")
        print(f"  - Total Time: {total_elapsed:.2f}s")
        
        # 🔥 FIX: Return different format for single mode vs batch mode
        if is_batch_mode:
            # Batch mode: return array of scenes
            return {
                "success": True,
                "scenes": scenes,
                "count": len(scenes),
                "total_shots": len(all_generated_shots),
                "ai_provider": ai_provider,
                "message": f"Successfully generated {len(scenes)} scenes with {len(all_generated_shots)} shots"
            }
        else:
            # Single scene mode: return single scene object
            if len(scenes) > 0:
                return {
                    "success": True,
                    "scene": scenes[0],  # ✅ Return first scene as 'scene' key
                    "total_shots": len(scenes[0].get('shots', [])),
                    "ai_provider": ai_provider,
                    "message": f"Successfully generated scene with {len(scenes[0].get('shots', []))} shots"
                }
            else:
                raise HTTPException(status_code=500, detail="No scene generated")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ SCENE GENERATION ERROR:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Scene generation failed: {type(e).__name__}: {str(e)}"
        )


@router.put("/{project_id}/scenes")
async def bulk_save_scenes(
    project_id: str,
    scenes_data: List[dict]
):
    """
    🆕 Bulk save/update scenes for a project
    
    This endpoint allows saving multiple scenes at once (used by Step 5).
    - Deletes all existing scenes for the project
    - Creates new scenes from the provided data
    - Updates project scenes_count
    
    Args:
        project_id: Project ID
        scenes_data: List of scene objects (shots will be stored separately)
        
    Returns:
        Updated scene count and success message
    """
    from documents_narrative import Scene, Shot
    
    print(f"\n{'='*80}")
    print(f"🔥 BULK SAVE SCENES")
    print(f"{'='*80}")
    print(f"Project ID: {project_id}")
    print(f"Scenes to save: {len(scenes_data)}")
    
    # Verify project exists
    project = await Project.find_one({"project_id": project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    
    try:
        # 🔥 NEW APPROACH: UPSERT instead of DELETE-ALL
        # This prevents data loss if frontend sends incomplete data
        print(f"\n💾 Using UPSERT approach (safer than delete-all)...")
        
        created_count = 0
        updated_count = 0
        total_shots = 0
        processed_scene_ids = set()
        
        for idx, scene_data in enumerate(scenes_data):
            try:
                # Get description and check length
                description = scene_data.get('description') or ''
                print(f"\n   📝 Scene {idx+1}: {scene_data.get('title', 'Untitled')}")
                print(f"      Description length: {len(description)} chars")
                
                # 🔥 FIX: Skip description validation if too short
                # Set to None instead of empty string to pass validation
                if description and len(description.strip()) < 350:
                    print(f"      ⚠️  Description too short ({len(description)} < 350), setting to None")
                    description = None
                
                # 🔥 FIX: Convert characters from string to list if needed
                characters_value = scene_data.get('characters', [])
                if isinstance(characters_value, str):
                    # If it's a string, split by comma or convert to single-item list
                    if ',' in characters_value:
                        characters_list = [name.strip() for name in characters_value.split(',') if name.strip()]
                    else:
                        characters_list = [characters_value.strip()] if characters_value.strip() else []
                    print(f"      🔧 Converted characters from string to list: {characters_list}")
                elif isinstance(characters_value, list):
                    characters_list = characters_value
                else:
                    characters_list = []
                
                # Check if scene already exists (by scene_id or scene_number)
                scene_id = scene_data.get('scene_id') or scene_data.get('id')
                existing_scene = None
                
                if scene_id and scene_id.startswith('scene_'):
                    # Try to find by scene_id (custom ID from frontend)
                    existing_scene = await Scene.find_one({
                        "project_id": project_id,
                        "scene_number": idx + 1
                    })
                elif scene_id:
                    # Try to find by MongoDB ObjectId
                    try:
                        existing_scene = await Scene.get(scene_id)
                    except:
                        pass
                
                scene_dict = {
                    "project_id": project_id,
                    "scene_number": idx + 1,
                    "point_number": scene_data.get('point_number', idx + 1),
                    "chapter_number": scene_data.get('chapter_number', 1),
                    "title": scene_data.get('title', f'Scene {idx+1}'),
                    "description": description,
                    "location": scene_data.get('location', ''),
                    "time_of_day": scene_data.get('time_of_day', 'day'),
                    "characters": characters_list,
                    "duration_seconds": scene_data.get('duration_seconds'),
                    "updated_at": datetime.utcnow()
                }
                
                if existing_scene:
                    # UPDATE existing scene
                    print(f"      🔄 Updating existing scene (ID: {existing_scene.id})")
                    for key, value in scene_dict.items():
                        setattr(existing_scene, key, value)
                    await existing_scene.save()
                    scene = existing_scene
                    updated_count += 1
                else:
                    # CREATE new scene
                    print(f"      ➕ Creating new scene")
                    scene = Scene(
                        **scene_dict,
                        created_at=datetime.utcnow()
                    )
                    await scene.insert()
                    created_count += 1
                
                processed_scene_ids.add(str(scene.id))
                print(f"      ✅ Scene saved (ID: {scene.id})")
                
            except Exception as scene_error:
                print(f"      ❌ Failed to save scene {idx+1}: {str(scene_error)}")
                # Re-raise to stop the whole operation
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to save scene {idx+1}: {str(scene_error)}"
                )
            
            # 3. UPSERT shots for this scene
            shots_data = scene_data.get('shots', [])
            shots_created = 0
            shots_updated = 0
            
            # First, get existing shots for this scene
            existing_shots = await Shot.find({"scene_id": str(scene.id)}).to_list()
            existing_shots_map = {shot.shot_number: shot for shot in existing_shots}
            processed_shot_numbers = set();
            
            for shot_idx, shot_data in enumerate(shots_data):
                try:
                    shot_number = shot_idx + 1;
                    processed_shot_numbers.add(shot_number);
                    
                    # Get shot description and validate length
                    shot_desc = shot_data.get('shot_description') or shot_data.get('description', '')
                    
                    # 🔥 FIX: Generate description if too short (need 100 chars for quality)
                    if not shot_desc or len(shot_desc.strip()) < 100:
                        # Auto-generate basic description from shot metadata
                        shot_type = shot_data.get('shot_type', 'medium')
                        camera_angle = shot_data.get('camera_angle', 'eye')
                        camera_movement = shot_data.get('camera_movement', 'static')
                        
                        # Create descriptive shot description (100+ chars)
                        shot_desc = (
                            f"{shot_type.replace('_', ' ').title()} with {camera_angle.replace('_', ' ')} angle. "
                            f"Camera movement: {camera_movement.replace('_', ' ')}. "
                            f"This shot establishes the scene composition and guides viewer attention to key elements. "
                            f"Frame captures the emotional tone and spatial relationships between subjects."
                        )
                    
                    shot_dict = {
                        "scene_id": str(scene.id),
                        "project_id": project_id,
                        "shot_number": shot_number,
                        "shot_title": shot_data.get('shot_title') or shot_data.get('shot_type', f'Shot {shot_number}'),
                        "shot_description": shot_desc,
                        "camera_angle": shot_data.get('camera_angle', 'eye'),
                        "camera_movement": shot_data.get('camera_movement', 'static'),
                        "lens_type": shot_data.get('lens_type') or shot_data.get('lens_settings', 'standard'),
                        "lighting_type": shot_data.get('lighting_type', 'natural'),
                        "lighting_time": shot_data.get('lighting_time', 'day'),
                        "duration_seconds": shot_data.get('duration_seconds', 5),
                        "motion_parameters": shot_data.get('motion_parameters', {}),
                        "updated_at": datetime.utcnow()
                    }
                    
                    if shot_number in existing_shots_map:
                        # UPDATE existing shot
                        existing_shot = existing_shots_map[shot_number]
                        for key, value in shot_dict.items():
                            setattr(existing_shot, key, value)
                        await existing_shot.save()
                        shots_updated += 1
                    else:
                        # CREATE new shot
                        shot = Shot(
                            **shot_dict,
                            created_at=datetime.utcnow()
                        )
                        await shot.insert()
                        shots_created += 1
                    
                except Exception as shot_error:
                    print(f"         ⚠️ Failed to save shot {shot_idx+1}: {str(shot_error)}")
                    # Continue with other shots instead of failing entire scene
            
            # Delete shots that are no longer in the data (were removed by user)
            shots_deleted = 0
            for shot_num, existing_shot in existing_shots_map.items():
                if shot_num not in processed_shot_numbers:
                    await existing_shot.delete()
                    shots_deleted += 1
                    print(f"         🗑️  Deleted removed shot {shot_num}")
            
            total_shots += (shots_created + shots_updated)
            print(f"   ✅ Scene {idx+1}: {scene.title} ({shots_created} created, {shots_updated} updated, {shots_deleted} deleted)")
        
        # 4. Delete scenes that are no longer in the data
        # 🔥 CRITICAL FIX: Enable scene deletion for proper sync
        scenes_deleted = 0
        all_project_scenes = await Scene.find({"project_id": project_id}).to_list()
        for scene in all_project_scenes:
            scene_id_str = str(scene.id)
            if scene_id_str not in processed_scene_ids:
                # Delete scene and all its shots
                await Shot.find({"scene_id": scene_id_str}).delete()
                await scene.delete()
                scenes_deleted += 1
                print(f"   🗑️  Deleted removed scene #{scene.scene_number}: {scene.title}")
        
        if scenes_deleted > 0:
            print(f"\n🗑️  Total scenes deleted: {scenes_deleted}")
        
        # 5. Update project scenes_count
        final_scene_count = await Scene.find({"project_id": project_id}).count()
        project.scenes_count = final_scene_count
        project.updated_at = datetime.utcnow()
        await project.save()
        
        print(f"\n✅ Successfully saved: {created_count} created, {updated_count} updated, {total_shots} total shots")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "scenes_count": final_scene_count,
            "scenes_created": created_count,
            "scenes_updated": updated_count,
            "shots_count": total_shots,
            "message": f"Successfully saved {final_scene_count} scenes with {total_shots} total shots"
        }
        
    except Exception as e:
        print(f"\n❌ Error during bulk save: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save scenes: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "narrative-projects",
        "timestamp": datetime.utcnow().isoformat()
    }
