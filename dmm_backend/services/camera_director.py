"""
Camera Director Service - AI-powered camera shot planning and suggestion engine
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import random
import httpx
import json
import os


class CameraDirector:
    """
    AI-powered camera director that suggests camera angles, lenses, and movements
    based on simulation context (emotion, intensity, dhamma references, etc.)
    """
    
    # Emotion to camera angle mapping
    EMOTION_TO_ANGLE = {
        "compassion": "close_up",
        "calm": "eye_level",
        "anger": "low",
        "fear": "high",
        "joy": "birds_eye",
        "sadness": "dutch",
        "confusion": "handheld",
        "concentration": "pov",
    }
    
    # Intensity to movement mapping
    INTENSITY_TO_MOVEMENT = {
        "very_low": "static",
        "low": "slow_pan",
        "medium": "dolly",
        "high": "handheld",
        "very_high": "whip_pan",
    }
    
    # Camera angles available
    CAMERA_ANGLES = [
        "eye_level", "high", "low", "dutch", 
        "birds_eye", "worms_eye", "pov", "over_shoulder"
    ]
    
    # Movement types
    MOVEMENT_TYPES = [
        "static", "pan", "tilt", "dolly", "crane", "handheld",
        "steadicam", "drone", "zoom", "rack_focus", "whip_pan", "orbit"
    ]
    
    # Shot types
    SHOT_TYPES = [
        "extreme_close_up", "close_up", "medium_close_up", "medium",
        "medium_wide", "full", "wide", "extreme_wide", "establishing"
    ]
    
    # Lens focal lengths (mm)
    LENS_TYPES = {
        "fisheye": (8, 15),
        "wide": (16, 35),
        "standard": (40, 60),
        "portrait": (70, 105),
        "telephoto": (135, 300),
        "super_telephoto": (400, 600),
    }
    
    def __init__(self):
        """Initialize camera director"""
        self.preset_library: Dict[str, Dict[str, Any]] = {}
        self._load_default_presets()
    
    def _load_default_presets(self):
        """Load default camera presets"""
        self.preset_library = {
            "dramatic_entrance": {
                "camera_angle": "low",
                "shot_type": "full",
                "movement_type": "dolly",
                "lens_settings": {"focal_length_mm": 24, "aperture": "f/2.8", "lens_type": "wide"},
                "description": "Dramatic entrance shot from low angle"
            },
            "intimate_conversation": {
                "camera_angle": "eye_level",
                "shot_type": "medium_close_up",
                "movement_type": "static",
                "lens_settings": {"focal_length_mm": 50, "aperture": "f/1.8", "lens_type": "standard"},
                "description": "Intimate conversation at eye level"
            },
            "contemplative_moment": {
                "camera_angle": "over_shoulder",
                "shot_type": "close_up",
                "movement_type": "slow_pan",
                "lens_settings": {"focal_length_mm": 85, "aperture": "f/1.4", "lens_type": "portrait"},
                "description": "Contemplative moment with shallow depth"
            },
            "action_sequence": {
                "camera_angle": "dutch",
                "shot_type": "medium_wide",
                "movement_type": "handheld",
                "lens_settings": {"focal_length_mm": 35, "aperture": "f/2.8", "lens_type": "wide"},
                "description": "Dynamic action with handheld movement"
            },
            "establishing_shot": {
                "camera_angle": "birds_eye",
                "shot_type": "extreme_wide",
                "movement_type": "drone",
                "lens_settings": {"focal_length_mm": 16, "aperture": "f/5.6", "lens_type": "wide"},
                "description": "Establishing shot from above"
            }
        }
    
    async def plan_shot(
        self,
        simulation_id: str,
        event_id: str,
        context: Dict[str, Any],
        preset_name: Optional[str] = None,
        generate_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Create a complete camera plan for an event
        
        Args:
            simulation_id: ID of the simulation
            event_id: ID of the event
            context: Context dict with emotion, intensity, dhamma_ref, etc.
            preset_name: Optional preset to use
            generate_ai: Whether to generate AI suggestions
        
        Returns:
            Complete camera plan dict
        """
        # Use preset if provided
        if preset_name and preset_name in self.preset_library:
            preset = self.preset_library[preset_name]
            plan = {
                "simulation_id": simulation_id,
                "event_id": event_id,
                "preset_name": preset_name,
                "camera_angle": preset["camera_angle"],
                "shot_type": preset["shot_type"],
                "movement_type": preset["movement_type"],
                "lens_settings": preset["lens_settings"],
                "context": context,
                "ai_generated": False,
                "created_at": datetime.utcnow()
            }
            return plan
        
        # Generate AI suggestions
        if generate_ai:
            ai_metadata = await self._generate_ai_suggestions(context)
            
            plan = {
                "simulation_id": simulation_id,
                "event_id": event_id,
                "camera_angle": ai_metadata["suggested_angle"],
                "shot_type": ai_metadata["suggested_shot_type"],
                "movement_type": ai_metadata["suggested_movement"],
                "lens_settings": ai_metadata["suggested_lens"],
                "context": context,
                "ai_metadata": ai_metadata,
                "ai_generated": True,
                "created_at": datetime.utcnow()
            }
            return plan
        
        # Default fallback
        return {
            "simulation_id": simulation_id,
            "event_id": event_id,
            "camera_angle": "eye_level",
            "shot_type": "medium",
            "movement_type": "static",
            "lens_settings": {"focal_length_mm": 50, "aperture": "f/2.8", "lens_type": "standard"},
            "context": context,
            "ai_generated": False,
            "created_at": datetime.utcnow()
        }
    
    async def _generate_ai_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI suggestions based on context
        
        Args:
            context: Context dict with emotion, intensity, dhamma_ref, etc.
        
        Returns:
            AI metadata with suggestions and reasoning
        """
        emotion = context.get("emotion", "neutral")
        intensity = context.get("intensity", "medium")
        dhamma_ref = context.get("dhamma_ref", None)
        
        # Suggest camera angle based on emotion
        suggested_angle = self._suggest_angle(emotion, intensity)
        
        # Suggest lens based on context
        suggested_lens = self._suggest_lens(emotion, intensity, dhamma_ref)
        
        # Suggest movement based on intensity
        suggested_movement = self._suggest_movement(intensity, emotion)
        
        # Suggest shot type based on emotion and intensity
        suggested_shot_type = self._suggest_shot_type(emotion, intensity)
        
        # Calculate confidence
        confidence = self._calculate_confidence(context)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            emotion, intensity, suggested_angle, suggested_lens, 
            suggested_movement, suggested_shot_type
        )
        
        return {
            "suggested_angle": suggested_angle,
            "suggested_lens": suggested_lens,
            "suggested_movement": suggested_movement,
            "suggested_shot_type": suggested_shot_type,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    def _suggest_angle(self, emotion: str, intensity: str) -> str:
        """Suggest camera angle based on emotion"""
        # Primary: emotion-based
        if emotion.lower() in self.EMOTION_TO_ANGLE:
            return self.EMOTION_TO_ANGLE[emotion.lower()]
        
        # Fallback: intensity-based
        if "high" in intensity.lower():
            return random.choice(["low", "dutch", "handheld"])
        elif "low" in intensity.lower():
            return "eye_level"
        
        return "eye_level"
    
    def _suggest_lens(self, emotion: str, intensity: str, dhamma_ref: Optional[str]) -> Dict[str, Any]:
        """Suggest lens settings based on context"""
        # Portrait for intimate/emotional moments
        if emotion.lower() in ["compassion", "sadness", "calm"]:
            return {
                "focal_length_mm": 85,
                "aperture": "f/1.8",
                "lens_type": "portrait"
            }
        
        # Wide for action/high intensity
        if "high" in intensity.lower():
            return {
                "focal_length_mm": 24,
                "aperture": "f/2.8",
                "lens_type": "wide"
            }
        
        # Standard for balanced scenes
        return {
            "focal_length_mm": 50,
            "aperture": "f/2.8",
            "lens_type": "standard"
        }
    
    def _suggest_movement(self, intensity: str, emotion: str) -> str:
        """Suggest camera movement based on intensity and emotion"""
        # Map intensity to movement
        intensity_key = intensity.lower().replace(" ", "_")
        if intensity_key in self.INTENSITY_TO_MOVEMENT:
            return self.INTENSITY_TO_MOVEMENT[intensity_key]
        
        # Emotion-based movement
        if emotion.lower() in ["anger", "fear"]:
            return "handheld"
        elif emotion.lower() in ["calm", "concentration"]:
            return "static"
        elif emotion.lower() == "joy":
            return "dolly"
        
        return "static"
    
    def _suggest_shot_type(self, emotion: str, intensity: str) -> str:
        """Suggest shot type based on emotion and intensity"""
        # Intimate emotions → closer shots
        if emotion.lower() in ["compassion", "sadness", "concentration"]:
            return random.choice(["close_up", "medium_close_up"])
        
        # High intensity → wider shots
        if "high" in intensity.lower():
            return random.choice(["medium_wide", "wide"])
        
        # Default: medium shot
        return "medium"
    
    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate AI confidence score (0.0-1.0)"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we have good context
        if "emotion" in context:
            confidence += 0.2
        if "intensity" in context:
            confidence += 0.15
        if "dhamma_ref" in context:
            confidence += 0.1
        if "character_name" in context:
            confidence += 0.05
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _generate_reasoning(
        self, 
        emotion: str, 
        intensity: str, 
        angle: str, 
        lens: Dict[str, Any], 
        movement: str, 
        shot_type: str
    ) -> str:
        """Generate human-readable reasoning for the suggestions"""
        reasons = []
        
        # Angle reasoning
        if emotion.lower() in self.EMOTION_TO_ANGLE:
            reasons.append(f"Using {angle} angle to convey {emotion}")
        
        # Lens reasoning
        if lens["lens_type"] == "portrait":
            reasons.append(f"Portrait lens ({lens['focal_length_mm']}mm) for intimate feel")
        elif lens["lens_type"] == "wide":
            reasons.append(f"Wide lens ({lens['focal_length_mm']}mm) for dynamic action")
        
        # Movement reasoning
        if movement == "static":
            reasons.append("Static camera for stable composition")
        elif movement == "handheld":
            reasons.append("Handheld movement for dynamic energy")
        elif movement == "dolly":
            reasons.append("Dolly movement for smooth progression")
        
        # Shot type reasoning
        if "close" in shot_type:
            reasons.append(f"{shot_type.replace('_', ' ').title()} to focus on emotion")
        elif "wide" in shot_type:
            reasons.append(f"{shot_type.replace('_', ' ').title()} for spatial context")
        
        return ". ".join(reasons) + "."
    
    async def process_feedback(
        self,
        plan_id: str,
        feedback_type: str,
        original_suggestion: Dict[str, Any],
        correction: Optional[Dict[str, Any]] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user feedback for AI learning
        
        Args:
            plan_id: ID of the camera plan
            feedback_type: "good", "not_good", or "modify"
            original_suggestion: Original AI suggestion
            correction: User's correction (if feedback_type == "modify")
            context: Original context
        
        Returns:
            Feedback record for storage
        """
        feedback_record = {
            "plan_id": plan_id,
            "feedback_type": feedback_type,
            "original_suggestion": original_suggestion,
            "correction": correction,
            "context": context or {},
            "created_at": datetime.utcnow(),
            "accepted": feedback_type == "good",
            "should_reinforce": feedback_type == "good",
            "should_penalize": feedback_type == "not_good"
        }
        
        # Generate reasoning for the feedback
        if feedback_type == "good":
            feedback_record["reasoning"] = "User accepted AI suggestion"
        elif feedback_type == "not_good":
            feedback_record["reasoning"] = "User rejected AI suggestion"
        elif feedback_type == "modify" and correction:
            changes = []
            for key in correction:
                if key in original_suggestion and correction[key] != original_suggestion[key]:
                    changes.append(f"{key}: {original_suggestion[key]} → {correction[key]}")
            feedback_record["reasoning"] = f"User modified: {', '.join(changes)}"
        
        return feedback_record
    
    def get_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """Get a preset by name"""
        return self.preset_library.get(preset_name)
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """List all available presets"""
        return [
            {"name": name, **preset}
            for name, preset in self.preset_library.items()
        ]
    
    def save_preset(self, preset_name: str, preset_data: Dict[str, Any]) -> bool:
        """Save a new preset"""
        self.preset_library[preset_name] = preset_data
        return True
    
    async def direct_scene(
        self,
        scene_context: Dict[str, Any],
        project_context: Optional[Dict[str, Any]] = None,
        provider: str = "qwen2.5"
    ) -> List[Dict[str, Any]]:
        """
        🤖 AI Director: Break down a scene into a precise shot list with timing.
        
        Args:
            scene_context: {
                "title": str,
                "description": str,
                "duration": str (e.g. "15s"),
                "characters": str,
                "location": str,
                "emotion": str
            }
            project_context: Full project data (Step 1-4) for style/theme context
            provider: "qwen2.5" or "gpt-4"
            
        Returns:
            List of shot dictionaries with timing and camera details
        """
        print(f"🎬 Director AI: Directing scene '{scene_context.get('title')}'...")
        
        # Parse duration
        duration_str = scene_context.get('duration', '15s')
        try:
            if '-' in duration_str:
                total_duration = (int(duration_str.split('-')[0]) + int(duration_str.split('-')[1].replace('s', ''))) / 2
            else:
                total_duration = int(duration_str.replace('s', '').replace('sec', '').strip())
        except:
            total_duration = 15.0
            
        # Extract Project Context (Step 1-4)
        genre_info = ""
        theme_info = ""
        style_guide = ""
        
        if project_context:
            # Step 1: Genre & Style
            genres = project_context.get('genres', [])
            if genres:
                genre_list = [f"{g.get('type', '')}" for g in genres]
                genre_info = f"Genre: {', '.join(genre_list)}"
                
            # Step 2: Theme
            theme = project_context.get('theme', {})
            if theme:
                theme_info = f"Theme: {theme.get('teaching', '')} {theme.get('lesson', '')}"
                
            # Determine Visual Style based on Genre
            main_genre = genres[0].get('type', '').lower() if genres else 'drama'
            if 'horror' in main_genre:
                style_guide = "Style: High contrast, shadows, unsettling angles, slow creeps."
            elif 'action' in main_genre:
                style_guide = "Style: Dynamic movement, fast cuts, wide to close rapid shifts."
            elif 'romance' in main_genre:
                style_guide = "Style: Soft lighting, close-ups, shallow depth of field, smooth motion."
            elif 'comedy' in main_genre:
                style_guide = "Style: Bright, flat lighting, medium shots, visual gags."
            else:
                style_guide = "Style: Cinematic, balanced, focus on character emotion."

        # Build Prompt
        prompt = f"""You are a professional Film Director and Cinematographer.
Break down this scene into a shot list.

PROJECT INFO:
{genre_info}
{theme_info}
{style_guide}

SCENE INFO:
Title: {scene_context.get('title')}
Description: {scene_context.get('description')}
Location: {scene_context.get('location')}
Characters: {scene_context.get('characters')}
Emotion: {scene_context.get('emotion', 'neutral')}
Total Duration: {total_duration} seconds

TASK:
1. Create a sequence of shots that tell this story visually.
2. Assign specific duration to each shot based on pacing (fast for action, slow for emotion).
3. Ensure total duration sums up to approx {total_duration}s.
4. Vary shot types and angles (Wide, Close-up, Low angle, etc.).
5. Align visual style with the Genre and Theme provided above.

OUTPUT FORMAT (JSON Array only):
[
  {{
    "shot_number": 1,
    "description": "Visual description of action...",
    "duration": 4.0,
    "shot_type": "wide",
    "camera_angle": "high",
    "movement": "static",
    "reasoning": "Establishing the location"
  }},
  ...
]

Valid Shot Types: {', '.join(self.SHOT_TYPES)}
Valid Angles: {', '.join(self.CAMERA_ANGLES)}
Valid Movements: {', '.join(self.MOVEMENT_TYPES)}

Generate JSON:"""

        # Call AI
        try:
            if provider == "qwen2.5":
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "http://127.0.0.1:11434/api/generate",
                        json={
                            "model": "qwen2.5:7b",
                            "prompt": prompt,
                            "stream": False,
                            "options": {"temperature": 0.7, "num_predict": 2000}
                        }
                    )
                    if response.status_code == 200:
                        result = response.json().get("response", "")
                    else:
                        raise Exception(f"Ollama error: {response.text}")
            
            elif provider == "gpt-4":
                # ... (GPT-4 implementation if needed, skipping for brevity as user uses local)
                pass
            
            # Parse JSON
            result_clean = result.strip()
            if result_clean.startswith("```json"): result_clean = result_clean[7:]
            if result_clean.startswith("```"): result_clean = result_clean[3:]
            if result_clean.endswith("```"): result_clean = result_clean[:-3]
            
            shots = json.loads(result_clean.strip())
            
            # Validate and fix shots
            validated_shots = []
            current_time = 0.0
            
            for i, shot in enumerate(shots):
                # Ensure required fields
                duration = float(shot.get("duration", 3.0))
                
                validated_shot = {
                    "shot_number": i + 1,
                    "description": shot.get("description", f"Shot {i+1}"),
                    "duration": duration,
                    "start_time": round(current_time, 1),
                    "end_time": round(current_time + duration, 1),
                    "shot_type": shot.get("shot_type", "medium"),
                    "camera_angle": shot.get("camera_angle", "eye_level"),
                    "movement": shot.get("movement", "static"),
                    "reasoning": shot.get("reasoning", "Director's choice")
                }
                validated_shots.append(validated_shot)
                current_time += duration
            
            print(f"✅ Director AI planned {len(validated_shots)} shots (Total: {current_time}s)")
            return validated_shots
            
        except Exception as e:
            print(f"⚠️ Director AI failed: {e}")
            # Fallback: Simple 3-shot breakdown
            avg_dur = total_duration / 3
            return [
                {
                    "shot_number": 1,
                    "description": "Establishing shot",
                    "duration": avg_dur,
                    "start_time": 0.0,
                    "end_time": avg_dur,
                    "shot_type": "wide",
                    "camera_angle": "eye_level",
                    "movement": "static"
                },
                {
                    "shot_number": 2,
                    "description": "Main action",
                    "duration": avg_dur,
                    "start_time": avg_dur,
                    "end_time": avg_dur * 2,
                    "shot_type": "medium",
                    "camera_angle": "eye_level",
                    "movement": "pan"
                },
                {
                    "shot_number": 3,
                    "description": "Reaction or conclusion",
                    "duration": avg_dur,
                    "start_time": avg_dur * 2,
                    "end_time": avg_dur * 3,
                    "shot_type": "close_up",
                    "camera_angle": "eye_level",
                    "movement": "static"
                }
            ]
