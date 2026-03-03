"""
🎨 Video Quality Presets

Defines quality levels for video generation with optimal parameters
for different use cases: speed vs quality tradeoff.

Quality Levels:
- PREVIEW: Ultra-fast for testing (256x144, 3 steps, ~3s generation)
- LOW: Fast generation for drafts (512x288, 10 steps, ~10s generation)
- MEDIUM: Balanced quality/speed (1024x576, 20 steps, ~30s generation)
- HIGH: High quality (1920x1080, 40 steps, ~60s generation)
- ULTRA: Maximum quality (1920x1080, 80 steps, ~120s generation)

Author: Peace Script Team
Date: 20 November 2025
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class QualityPreset:
    """Quality preset configuration"""
    name: str
    description: str
    
    # ComfyUI settings
    width: int
    height: int
    steps: int
    cfg_scale: float
    
    # FFmpeg settings
    fps: int
    crf: int  # Constant Rate Factor (lower = better quality, 18-28 typical)
    preset: str  # FFmpeg encoding preset (ultrafast, fast, medium, slow)
    
    # Generation settings
    num_images: int
    duration_per_image: float
    
    # Metadata
    estimated_time: int  # seconds
    typical_file_size: str  # MB per second of video


# =============================================================================
# QUALITY PRESETS
# =============================================================================

QUALITY_PRESETS: Dict[str, QualityPreset] = {
    "preview": QualityPreset(
        name="Preview",
        description="Ultra-fast preview for testing (256p, 3 steps)",
        width=256,
        height=144,
        steps=3,
        cfg_scale=5.0,
        fps=12,
        crf=28,
        preset="ultrafast",
        num_images=1,
        duration_per_image=2.0,
        estimated_time=3,
        typical_file_size="0.5 MB/s"
    ),
    
    "low": QualityPreset(
        name="Low Quality",
        description="Fast generation for drafts (480p, 10 steps)",
        width=512,
        height=288,
        steps=10,
        cfg_scale=6.0,
        fps=24,
        crf=26,
        preset="fast",
        num_images=2,
        duration_per_image=2.5,
        estimated_time=10,
        typical_file_size="1 MB/s"
    ),
    
    "medium": QualityPreset(
        name="Medium Quality",
        description="Balanced quality and speed (720p, 20 steps)",
        width=1024,
        height=576,
        steps=20,
        cfg_scale=7.0,
        fps=24,
        crf=23,
        preset="medium",
        num_images=3,
        duration_per_image=3.0,
        estimated_time=30,
        typical_file_size="2 MB/s"
    ),
    
    "high": QualityPreset(
        name="High Quality",
        description="High quality production (1080p, 40 steps)",
        width=1920,
        height=1080,
        steps=40,
        cfg_scale=7.5,
        fps=24,
        crf=20,
        preset="slow",
        num_images=4,
        duration_per_image=3.0,
        estimated_time=60,
        typical_file_size="4 MB/s"
    ),
    
    "ultra": QualityPreset(
        name="Ultra Quality",
        description="Maximum quality for final renders (1080p, 80 steps)",
        width=1920,
        height=1080,
        steps=80,
        cfg_scale=8.0,
        fps=30,
        crf=18,
        preset="slow",
        num_images=5,
        duration_per_image=3.0,
        estimated_time=120,
        typical_file_size="6 MB/s"
    )
}


def get_preset(quality: str) -> QualityPreset:
    """
    Get quality preset by name
    
    Args:
        quality: Quality level (preview, low, medium, high, ultra)
        
    Returns:
        QualityPreset configuration
        
    Raises:
        ValueError: If quality level not found
    """
    quality_lower = quality.lower()
    
    if quality_lower not in QUALITY_PRESETS:
        raise ValueError(
            f"Unknown quality '{quality}'. "
            f"Valid options: {', '.join(QUALITY_PRESETS.keys())}"
        )
    
    return QUALITY_PRESETS[quality_lower]


def get_all_presets() -> Dict[str, QualityPreset]:
    """Get all available quality presets"""
    return QUALITY_PRESETS.copy()


def estimate_generation_time(quality: str, duration: float) -> int:
    """
    Estimate total generation time
    
    Args:
        quality: Quality preset name
        duration: Video duration in seconds
        
    Returns:
        Estimated time in seconds
    """
    preset = get_preset(quality)
    
    # Base time from preset
    base_time = preset.estimated_time
    
    # Scale with duration (linear approximation)
    # Each additional second adds ~20% of base time
    extra_duration = max(0, duration - (preset.num_images * preset.duration_per_image))
    extra_time = extra_duration * (base_time * 0.2)
    
    return int(base_time + extra_time)


def estimate_file_size(quality: str, duration: float) -> float:
    """
    Estimate output file size in MB
    
    Args:
        quality: Quality preset name
        duration: Video duration in seconds
        
    Returns:
        Estimated file size in MB
    """
    preset = get_preset(quality)
    
    # Parse typical file size (format: "X MB/s")
    mb_per_second = float(preset.typical_file_size.split()[0])
    
    return mb_per_second * duration


def get_preset_summary() -> Dict[str, Dict[str, Any]]:
    """
    Get summary of all presets for UI display
    
    Returns:
        Dict with preset info for each quality level
    """
    summary = {}
    
    for key, preset in QUALITY_PRESETS.items():
        summary[key] = {
            "name": preset.name,
            "description": preset.description,
            "resolution": f"{preset.width}x{preset.height}",
            "estimated_time": f"~{preset.estimated_time}s",
            "file_size": preset.typical_file_size,
            "recommended_for": _get_use_case(key)
        }
    
    return summary


def _get_use_case(quality: str) -> str:
    """Get recommended use case for quality level"""
    use_cases = {
        "preview": "Quick tests and iterations",
        "low": "Draft reviews and storyboards",
        "medium": "General content and social media",
        "high": "Professional videos and presentations",
        "ultra": "Final renders and archival quality"
    }
    return use_cases.get(quality, "General use")


# =============================================================================
# VALIDATION
# =============================================================================

def validate_quality_settings(
    quality: str,
    custom_width: Optional[int] = None,
    custom_height: Optional[int] = None,
    custom_steps: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validate and merge custom settings with preset
    
    Args:
        quality: Quality preset name
        custom_width: Override width (optional)
        custom_height: Override height (optional)
        custom_steps: Override steps (optional)
        
    Returns:
        Validated settings dict
    """
    preset = get_preset(quality)
    
    settings = {
        "width": custom_width or preset.width,
        "height": custom_height or preset.height,
        "steps": custom_steps or preset.steps,
        "cfg_scale": preset.cfg_scale,
        "fps": preset.fps,
        "crf": preset.crf,
        "preset": preset.preset,
        "num_images": preset.num_images,
        "duration_per_image": preset.duration_per_image
    }
    
    # Validation
    if settings["width"] < 256 or settings["width"] > 3840:
        raise ValueError("Width must be between 256 and 3840")
    
    if settings["height"] < 144 or settings["height"] > 2160:
        raise ValueError("Height must be between 144 and 2160")
    
    if settings["steps"] < 1 or settings["steps"] > 150:
        raise ValueError("Steps must be between 1 and 150")
    
    return settings
