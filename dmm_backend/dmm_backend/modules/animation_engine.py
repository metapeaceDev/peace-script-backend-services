"""
3D Animation Engine
===================

Integrates Blender Python API and FFmpeg for generating character animations
based on Buddhist mental states.

Features:
1. Blender scene setup and rendering
2. Animation templates for each citta type
3. Path attainment visual effects
4. Video encoding and compression
5. GIF generation for web use

Buddhist Framework:
- Kusala: Peaceful, flowing animations (green theme)
- Akusala: Agitated, unstable animations (red theme)
- Vipāka: Neutral, passive animations (blue theme)
- Kiriya: Steady, functional animations (purple theme)
- Jhāna: Deep meditation animations
- Magga/Phala: Enlightenment transformation animations

Dependencies:
- bpy (Blender Python API)
- ffmpeg-python
- PIL (Pillow) for image processing
"""

import subprocess
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import uuid

# Animation configuration
BLENDER_EXECUTABLE = os.environ.get("BLENDER_PATH", "/Applications/Blender.app/Contents/MacOS/Blender")
ANIMATION_OUTPUT_DIR = Path("media/animations")
TEMP_RENDER_DIR = Path(tempfile.gettempdir()) / "dmm_animations"

# Ensure directories exist
ANIMATION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_RENDER_DIR.mkdir(parents=True, exist_ok=True)


class AnimationType(str, Enum):
    """Animation types mapped to mental states"""
    PEACEFUL_BREATHING = "peaceful-breathing"  # Kusala
    AGITATED_PULSE = "agitated-pulse"  # Akusala
    NEUTRAL_FLOAT = "neutral-float"  # Vipāka
    STEADY_GLOW = "steady-glow"  # Kiriya
    MEDITATION = "meditation"  # Jhāna
    ENLIGHTENMENT = "enlightenment"  # Magga/Phala


class CittaState(str, Enum):
    """Buddhist consciousness categories"""
    KUSALA = "kusala"
    AKUSALA = "akusala"
    VIPAKA = "vipaka"
    KIRIYA = "kiriya"


# ============================================================================
# COLOR SCHEMES
# ============================================================================

COLOR_SCHEMES = {
    CittaState.KUSALA: {
        "primary": (0.063, 0.725, 0.506),  # RGB normalized: #10b981
        "secondary": (0.133, 0.804, 0.576),
        "glow": (0.2, 1.0, 0.7),
        "emission_strength": 1.5
    },
    CittaState.AKUSALA: {
        "primary": (0.937, 0.267, 0.267),  # RGB normalized: #ef4444
        "secondary": (0.988, 0.329, 0.329),
        "glow": (1.0, 0.3, 0.3),
        "emission_strength": 2.0
    },
    CittaState.VIPAKA: {
        "primary": (0.231, 0.510, 0.965),  # RGB normalized: #3b82f6
        "secondary": (0.329, 0.580, 0.988),
        "glow": (0.4, 0.6, 1.0),
        "emission_strength": 1.2
    },
    CittaState.KIRIYA: {
        "primary": (0.659, 0.333, 0.969),  # RGB normalized: #a855f7
        "secondary": (0.753, 0.443, 0.988),
        "glow": (0.8, 0.4, 1.0),
        "emission_strength": 1.3
    }
}


# ============================================================================
# BLENDER SCENE GENERATOR
# ============================================================================

class BlenderSceneGenerator:
    """
    Generate Blender Python scripts for character animations.
    
    This class doesn't directly call Blender API (which requires running inside Blender),
    but generates Python scripts that will be executed by Blender.
    """
    
    @staticmethod
    def generate_base_scene_script(
        citta_state: CittaState,
        animation_type: AnimationType,
        duration_seconds: int,
        brightness: float = 1.0,
        path_stage: Optional[str] = None
    ) -> str:
        """
        Generate Blender Python script for base scene setup.
        
        Args:
            citta_state: Current consciousness state
            animation_type: Type of animation to generate
            duration_seconds: Animation duration
            brightness: Brightness multiplier (0.5-1.5)
            path_stage: Path attainment stage (for halo effects)
        
        Returns:
            Python script string to be executed in Blender
        """
        colors = COLOR_SCHEMES[citta_state]
        
        script = f"""
import bpy
import math
from mathutils import Vector, Euler

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Scene setup
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.frame_end = {duration_seconds * 30}  # 30 fps

# Camera setup
bpy.ops.object.camera_add(location=(0, -8, 0))
camera = bpy.context.object
camera.rotation_euler = Euler((math.radians(90), 0, 0))
scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.object
sun.data.energy = 2.0

# Create character sphere (avatar)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
avatar = bpy.context.object
avatar.name = "Avatar"

# Create material
mat = bpy.data.materials.new(name="AvatarMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Shader nodes
output = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
emission = nodes.new('ShaderNodeEmission')
mix_shader = nodes.new('ShaderNodeMixShader')

# Set colors
principled.inputs['Base Color'].default_value = {colors['primary'] + (1.0,)}
principled.inputs['Metallic'].default_value = 0.3
principled.inputs['Roughness'].default_value = 0.2

emission.inputs['Color'].default_value = {colors['glow'] + (1.0,)}
emission.inputs['Strength'].default_value = {colors['emission_strength'] * brightness}

# Connect nodes
links = mat.node_tree.links
links.new(principled.outputs['BSDF'], mix_shader.inputs[1])
links.new(emission.outputs['Emission'], mix_shader.inputs[2])
links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

# Assign material
avatar.data.materials.append(mat)

# Animation keyframes
{BlenderSceneGenerator._generate_animation_keyframes(animation_type, duration_seconds)}

# Path stage halo (if applicable)
{BlenderSceneGenerator._generate_path_halo(path_stage) if path_stage else "# No path stage"}

print("Scene setup complete!")
"""
        return script
    
    @staticmethod
    def _generate_animation_keyframes(animation_type: AnimationType, duration: int) -> str:
        """Generate animation keyframe code based on type"""
        
        if animation_type == AnimationType.PEACEFUL_BREATHING:
            return f"""
# Peaceful breathing animation (Kusala)
avatar.animation_data_create()
avatar.animation_data.action = bpy.data.actions.new(name="PeacefulBreathing")

# Scale breathing
for frame in range(0, {duration * 30}, 1):
    scale = 1.0 + 0.05 * math.sin(frame * math.pi / 60)  # 2 second cycle
    avatar.scale = (scale, scale, scale)
    avatar.keyframe_insert(data_path="scale", frame=frame)
    
# Rotation
for frame in range(0, {duration * 30}, 10):
    avatar.rotation_euler.z = math.radians(5 * math.sin(frame * math.pi / 90))
    avatar.keyframe_insert(data_path="rotation_euler", frame=frame)
"""
        
        elif animation_type == AnimationType.AGITATED_PULSE:
            return f"""
# Agitated pulse animation (Akusala)
avatar.animation_data_create()
avatar.animation_data.action = bpy.data.actions.new(name="AgitatedPulse")

# Rapid pulsing
for frame in range(0, {duration * 30}, 1):
    scale = 1.0 + 0.15 * math.sin(frame * math.pi / 15)  # 0.5 second rapid cycle
    avatar.scale = (scale, scale, scale)
    avatar.keyframe_insert(data_path="scale", frame=frame)
    
# Erratic rotation
for frame in range(0, {duration * 30}, 5):
    avatar.rotation_euler.z = math.radians(15 * math.sin(frame * math.pi / 20))
    avatar.keyframe_insert(data_path="rotation_euler", frame=frame)
"""
        
        elif animation_type == AnimationType.NEUTRAL_FLOAT:
            return f"""
# Neutral floating animation (Vipāka)
avatar.animation_data_create()
avatar.animation_data.action = bpy.data.actions.new(name="NeutralFloat")

# Gentle floating
for frame in range(0, {duration * 30}, 1):
    avatar.location.z = 0.3 * math.sin(frame * math.pi / 90)  # 3 second cycle
    avatar.keyframe_insert(data_path="location", frame=frame)
    
# Slow rotation
for frame in range(0, {duration * 30}, 10):
    avatar.rotation_euler.z = frame * math.pi / 180
    avatar.keyframe_insert(data_path="rotation_euler", frame=frame)
"""
        
        elif animation_type == AnimationType.STEADY_GLOW:
            return f"""
# Steady glow animation (Kiriya)
avatar.animation_data_create()
avatar.animation_data.action = bpy.data.actions.new(name="SteadyGlow")

# Minimal movement, mainly glow variation
for frame in range(0, {duration * 30}, 1):
    glow_strength = 1.3 + 0.2 * math.sin(frame * math.pi / 120)
    # Animate via material nodes (simplified here)
    avatar.keyframe_insert(data_path="location", frame=frame)
"""
        
        elif animation_type == AnimationType.MEDITATION:
            return f"""
# Deep meditation animation (Jhāna)
avatar.animation_data_create()
avatar.animation_data.action = bpy.data.actions.new(name="Meditation")

# Very slow, minimal breathing
for frame in range(0, {duration * 30}, 1):
    scale = 1.0 + 0.02 * math.sin(frame * math.pi / 180)  # 6 second cycle
    avatar.scale = (scale, scale, scale)
    avatar.keyframe_insert(data_path="scale", frame=frame)
"""
        
        elif animation_type == AnimationType.ENLIGHTENMENT:
            return f"""
# Enlightenment transformation (Magga/Phala)
avatar.animation_data_create()
avatar.animation_data.action = bpy.data.actions.new(name="Enlightenment")

# Expanding enlightenment burst
for frame in range(0, {duration * 30}, 1):
    progress = frame / ({duration * 30})
    scale = 1.0 + progress * 0.5  # Gradual expansion
    avatar.scale = (scale, scale, scale)
    avatar.keyframe_insert(data_path="scale", frame=frame)
    
# Intense glow increase
for frame in range(0, {duration * 30}, 1):
    progress = frame / ({duration * 30})
    # Glow increases dramatically
    avatar.keyframe_insert(data_path="location", frame=frame)
"""
        
        return "# Default animation"
    
    @staticmethod
    def _generate_path_halo(path_stage: str) -> str:
        """Generate halo effect for path attainment"""
        
        particle_counts = {
            "sotapanna": 7,
            "sakadagami": 14,
            "anagami": 21,
            "arahant": 108
        }
        
        count = particle_counts.get(path_stage.lower(), 0)
        
        return f"""
# Path attainment halo
bpy.ops.mesh.primitive_torus_add(
    location=(0, 0, 0),
    major_radius=1.5,
    minor_radius=0.05
)
halo = bpy.context.object
halo.name = "PathHalo"

# Halo material
halo_mat = bpy.data.materials.new(name="HaloMaterial")
halo_mat.use_nodes = True
halo_nodes = halo_mat.node_tree.nodes
halo_nodes.clear()

halo_emission = halo_nodes.new('ShaderNodeEmission')
halo_emission.inputs['Color'].default_value = (1.0, 0.84, 0.0, 1.0)  # Gold
halo_emission.inputs['Strength'].default_value = 3.0

halo_output = halo_nodes.new('ShaderNodeOutputMaterial')
halo_mat.node_tree.links.new(halo_emission.outputs['Emission'], halo_output.inputs['Surface'])

halo.data.materials.append(halo_mat)

# Rotate halo
halo.animation_data_create()
for frame in range(0, scene.frame_end, 1):
    halo.rotation_euler.z = frame * math.pi / 60  # One rotation per 2 seconds
    halo.keyframe_insert(data_path="rotation_euler", frame=frame)

# Add {count} light particles around halo
for i in range({count}):
    angle = (2 * math.pi * i) / {count}
    x = 1.5 * math.cos(angle)
    y = 1.5 * math.sin(angle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x, y, 0))
    particle = bpy.context.object
    particle.name = f"Particle_{{i}}"
    particle.data.materials.append(halo_mat)
"""


# ============================================================================
# ANIMATION ENGINE
# ============================================================================

class AnimationEngine:
    """
    Main animation generation engine.
    
    Orchestrates:
    1. Blender script generation
    2. Blender execution
    3. Frame rendering
    4. Video encoding with FFmpeg
    5. GIF generation
    """
    
    def __init__(self):
        self.blender_path = BLENDER_EXECUTABLE
        self.output_dir = ANIMATION_OUTPUT_DIR
        self.temp_dir = TEMP_RENDER_DIR
    
    def generate_animation(
        self,
        model_id: str,
        citta_state: str,
        animation_type: str,
        duration_seconds: int = 5,
        resolution: Tuple[int, int] = (1920, 1080),
        brightness: float = 1.0,
        path_stage: Optional[str] = None,
        output_format: str = "mp4"  # mp4 or gif
    ) -> Dict[str, Any]:
        """
        Generate complete animation.
        
        Args:
            model_id: Character model ID
            citta_state: Current citta state (kusala/akusala/vipaka/kiriya)
            animation_type: Animation type
            duration_seconds: Duration in seconds
            resolution: Video resolution (width, height)
            brightness: Brightness multiplier
            path_stage: Path attainment stage
            output_format: Output format (mp4 or gif)
        
        Returns:
            Dict with animation metadata
        """
        try:
            # 1. Generate Blender script
            citta_enum = CittaState(citta_state)
            anim_enum = AnimationType(animation_type)
            
            blender_script = BlenderSceneGenerator.generate_base_scene_script(
                citta_state=citta_enum,
                animation_type=anim_enum,
                duration_seconds=duration_seconds,
                brightness=brightness,
                path_stage=path_stage
            )
            
            # 2. Save script to temp file
            script_path = self.temp_dir / f"animation_{model_id}_{int(datetime.now().timestamp())}.py"
            script_path.write_text(blender_script)
            
            # 3. Render frames with Blender
            frames_dir = self.temp_dir / f"frames_{model_id}"
            frames_dir.mkdir(exist_ok=True)
            
            render_success = self._render_with_blender(
                script_path=script_path,
                output_dir=frames_dir,
                resolution=resolution
            )
            
            if not render_success:
                raise Exception("Blender rendering failed")
            
            # 4. Encode video with FFmpeg
            animation_id = f"anim_{model_id}_{int(datetime.now().timestamp())}"
            output_path = self.output_dir / f"{animation_id}.{output_format}"
            
            encode_success = self._encode_video(
                frames_dir=frames_dir,
                output_path=output_path,
                fps=30,
                output_format=output_format
            )
            
            if not encode_success:
                raise Exception("FFmpeg encoding failed")
            
            # 5. Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            # 6. Cleanup temp files
            self._cleanup_temp_files(script_path, frames_dir)
            
            return {
                "animation_id": animation_id,
                "animation_url": f"/media/animations/{animation_id}.{output_format}",
                "file_path": str(output_path),
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": duration_seconds,
                "resolution": f"{resolution[0]}x{resolution[1]}",
                "format": output_format,
                "rendered_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "animation_id": None,
                "animation_url": None
            }
    
    def _render_with_blender(
        self,
        script_path: Path,
        output_dir: Path,
        resolution: Tuple[int, int]
    ) -> bool:
        """
        Execute Blender to render frames.
        
        Args:
            script_path: Path to Blender Python script
            output_dir: Directory for rendered frames
            resolution: Resolution tuple
        
        Returns:
            True if successful
        """
        try:
            # Blender command: blender --background --python script.py
            cmd = [
                self.blender_path,
                "--background",
                "--python", str(script_path),
                "--render-output", str(output_dir / "frame_####"),
                "--render-anim",
                "-x", "1",  # Use file extension
                "-o", str(output_dir / "frame_"),
                "-F", "PNG",  # Output format
                "-s", "1",  # Start frame
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"Blender rendering error: {e}")
            return False
    
    def _encode_video(
        self,
        frames_dir: Path,
        output_path: Path,
        fps: int = 30,
        output_format: str = "mp4"
    ) -> bool:
        """
        Encode frames to video using FFmpeg.
        
        Args:
            frames_dir: Directory containing PNG frames
            output_path: Output video path
            fps: Frames per second
            output_format: Output format
        
        Returns:
            True if successful
        """
        try:
            if output_format == "mp4":
                # H.264 encoding
                cmd = [
                    "ffmpeg",
                    "-framerate", str(fps),
                    "-pattern_type", "glob",
                    "-i", str(frames_dir / "frame_*.png"),
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-crf", "23",  # Quality (lower = better, 18-28 range)
                    "-y",  # Overwrite output
                    str(output_path)
                ]
            elif output_format == "gif":
                # GIF encoding
                cmd = [
                    "ffmpeg",
                    "-framerate", str(fps),
                    "-pattern_type", "glob",
                    "-i", str(frames_dir / "frame_*.png"),
                    "-vf", "fps=15,scale=640:-1:flags=lanczos",
                    "-y",
                    str(output_path)
                ]
            else:
                raise ValueError(f"Unsupported format: {output_format}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"FFmpeg encoding error: {e}")
            return False
    
    def _cleanup_temp_files(self, script_path: Path, frames_dir: Path):
        """Clean up temporary files"""
        try:
            # Remove script
            if script_path.exists():
                script_path.unlink()
            
            # Remove frames
            if frames_dir.exists():
                for frame_file in frames_dir.glob("*.png"):
                    frame_file.unlink()
                frames_dir.rmdir()
        
        except Exception as e:
            print(f"Cleanup error: {e}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_animation_engine() -> AnimationEngine:
    """Create animation engine instance"""
    return AnimationEngine()


def generate_kusala_animation(
    model_id: str,
    duration: int = 10,
    path_stage: Optional[str] = None
) -> Dict[str, Any]:
    """Quick function to generate Kusala (wholesome) animation"""
    engine = create_animation_engine()
    return engine.generate_animation(
        model_id=model_id,
        citta_state="kusala",
        animation_type="peaceful-breathing",
        duration_seconds=duration,
        brightness=1.3,
        path_stage=path_stage
    )


def generate_akusala_animation(
    model_id: str,
    duration: int = 5
) -> Dict[str, Any]:
    """Quick function to generate Akusala (unwholesome) animation"""
    engine = create_animation_engine()
    return engine.generate_animation(
        model_id=model_id,
        citta_state="akusala",
        animation_type="agitated-pulse",
        duration_seconds=duration,
        brightness=0.8
    )


def generate_meditation_animation(
    model_id: str,
    duration: int = 30,
    path_stage: str = "sotapanna"
) -> Dict[str, Any]:
    """Quick function to generate meditation animation"""
    engine = create_animation_engine()
    return engine.generate_animation(
        model_id=model_id,
        citta_state="kusala",
        animation_type="meditation",
        duration_seconds=duration,
        brightness=1.5,
        path_stage=path_stage
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "AnimationEngine",
    "AnimationType",
    "CittaState",
    "BlenderSceneGenerator",
    "create_animation_engine",
    "generate_kusala_animation",
    "generate_akusala_animation",
    "generate_meditation_animation"
]
