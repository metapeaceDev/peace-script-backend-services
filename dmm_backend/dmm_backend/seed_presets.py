"""
Seed data for Custom Presets System
Sprint 2: Days 9-16
Created: 28 ตุลาคม 2568
"""

import asyncio
from datetime import datetime
from documents_presets import (
    PresetTemplate,
    UserPreset,
    PresetCollection,
    PresetCategory,
    PresetVisibility,
    PresetConfig,
    PresetParameter,
    PresetUsageStats,
    PresetTag
)
from db_init import init_db
from core.logging_config import get_logger

logger = get_logger(__name__)


async def seed_preset_templates():
    """Seed system preset templates"""
    logger.info("Seeding preset templates...")
    
    # Clear existing templates
    await PresetTemplate.delete_all()
    
    templates = [
        # Shot Composition Presets
        PresetTemplate(
            template_id="template_closeup_emotional",
            name="Close-up Emotional",
            description="Close-up shot for capturing emotional moments and facial expressions",
            category=PresetCategory.SHOT_COMPOSITION,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="shot_size",
                        value="close_up",
                        type="select",
                        description="Shot size classification",
                        options=["extreme_close_up", "close_up", "medium_close_up"]
                    ),
                    PresetParameter(
                        name="focus_point",
                        value="eyes",
                        type="select",
                        description="Primary focus point",
                        options=["eyes", "face", "hands"]
                    ),
                    PresetParameter(
                        name="depth_of_field",
                        value=2.8,
                        type="range",
                        description="F-stop for depth of field",
                        min_value=1.4,
                        max_value=8.0
                    )
                ],
                camera_settings={
                    "focal_length": 85,
                    "aperture": "f/2.8",
                    "height": "eye_level"
                },
                shot_settings={
                    "framing": "tight",
                    "headroom": "minimal",
                    "look_room": "standard"
                },
                feedback_triggers={
                    "check_focus": True,
                    "check_lighting": True,
                    "check_emotion": True
                }
            ),
            tags=[
                PresetTag(name="emotional", color="#FF6B6B"),
                PresetTag(name="portrait", color="#4ECDC4"),
                PresetTag(name="dramatic", color="#FFD93D")
            ],
            thumbnail_url="/assets/presets/closeup_emotional.jpg"
        ),
        
        PresetTemplate(
            template_id="template_wide_establishing",
            name="Wide Establishing Shot",
            description="Wide shot for establishing location and context",
            category=PresetCategory.SHOT_COMPOSITION,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="shot_size",
                        value="wide_shot",
                        type="select",
                        description="Shot size classification",
                        options=["extreme_wide", "wide_shot", "full_shot"]
                    ),
                    PresetParameter(
                        name="subject_position",
                        value="rule_of_thirds",
                        type="select",
                        description="Subject positioning guide",
                        options=["centered", "rule_of_thirds", "golden_ratio"]
                    ),
                    PresetParameter(
                        name="depth_of_field",
                        value=8.0,
                        type="range",
                        description="F-stop for depth of field",
                        min_value=5.6,
                        max_value=16.0
                    )
                ],
                camera_settings={
                    "focal_length": 24,
                    "aperture": "f/8",
                    "height": "chest_level"
                },
                shot_settings={
                    "framing": "loose",
                    "headroom": "generous",
                    "environment_visible": True
                }
            ),
            tags=[
                PresetTag(name="establishing", color="#95E1D3"),
                PresetTag(name="landscape", color="#38ada9"),
                PresetTag(name="context", color="#6C5CE7")
            ],
            thumbnail_url="/assets/presets/wide_establishing.jpg"
        ),
        
        # Camera Movement Presets
        PresetTemplate(
            template_id="template_dolly_zoom",
            name="Dolly Zoom (Vertigo Effect)",
            description="Classic dolly zoom for dramatic tension and psychological impact",
            category=PresetCategory.CAMERA_MOVEMENT,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="movement_type",
                        value="dolly_zoom",
                        type="select",
                        description="Type of camera movement",
                        options=["dolly_in", "dolly_out", "dolly_zoom"]
                    ),
                    PresetParameter(
                        name="speed",
                        value=0.5,
                        type="range",
                        description="Movement speed (0=slow, 1=fast)",
                        min_value=0.1,
                        max_value=1.0
                    ),
                    PresetParameter(
                        name="intensity",
                        value=0.7,
                        type="range",
                        description="Effect intensity",
                        min_value=0.3,
                        max_value=1.0
                    )
                ],
                camera_settings={
                    "focal_length_start": 50,
                    "focal_length_end": 85,
                    "maintain_subject_size": True
                },
                shot_settings={
                    "subject_tracking": True,
                    "stabilization": "high"
                }
            ),
            tags=[
                PresetTag(name="dramatic", color="#FFD93D"),
                PresetTag(name="psychological", color="#A29BFE"),
                PresetTag(name="iconic", color="#FD79A8")
            ],
            thumbnail_url="/assets/presets/dolly_zoom.jpg"
        ),
        
        PresetTemplate(
            template_id="template_tracking_shot",
            name="Smooth Tracking Shot",
            description="Fluid tracking shot following subject movement",
            category=PresetCategory.CAMERA_MOVEMENT,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="movement_type",
                        value="tracking",
                        type="select",
                        description="Type of camera movement",
                        options=["tracking", "following", "parallax"]
                    ),
                    PresetParameter(
                        name="smoothness",
                        value=0.9,
                        type="range",
                        description="Movement smoothness",
                        min_value=0.5,
                        max_value=1.0
                    ),
                    PresetParameter(
                        name="distance",
                        value="medium",
                        type="select",
                        description="Camera distance from subject",
                        options=["close", "medium", "far"]
                    )
                ],
                camera_settings={
                    "stabilization": "gimbal",
                    "focus_tracking": True
                },
                shot_settings={
                    "subject_in_frame": "center",
                    "environment_visibility": "medium"
                }
            ),
            tags=[
                PresetTag(name="dynamic", color="#00B894"),
                PresetTag(name="smooth", color="#00CEC9"),
                PresetTag(name="cinematic", color="#0984E3")
            ],
            thumbnail_url="/assets/presets/tracking_shot.jpg"
        ),
        
        # Lighting Presets
        PresetTemplate(
            template_id="template_dramatic_low_key",
            name="Dramatic Low-Key Lighting",
            description="High contrast low-key lighting for dramatic and mysterious mood",
            category=PresetCategory.LIGHTING,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="lighting_style",
                        value="low_key",
                        type="select",
                        description="Overall lighting style",
                        options=["high_key", "low_key", "natural"]
                    ),
                    PresetParameter(
                        name="contrast_ratio",
                        value=8.0,
                        type="range",
                        description="Contrast ratio (key:fill)",
                        min_value=2.0,
                        max_value=16.0
                    ),
                    PresetParameter(
                        name="shadow_density",
                        value=0.8,
                        type="range",
                        description="Shadow darkness level",
                        min_value=0.3,
                        max_value=1.0
                    )
                ],
                camera_settings={
                    "iso": 800,
                    "exposure_compensation": -1.0
                },
                shot_settings={
                    "key_light_angle": 45,
                    "fill_light_intensity": 0.2,
                    "rim_light": True
                }
            ),
            tags=[
                PresetTag(name="dramatic", color="#2D3436"),
                PresetTag(name="moody", color="#636E72"),
                PresetTag(name="noir", color="#000000")
            ],
            thumbnail_url="/assets/presets/low_key_lighting.jpg"
        ),
        
        # Emotion Focus Presets
        PresetTemplate(
            template_id="template_joy_capture",
            name="Joy & Happiness Capture",
            description="Optimized settings for capturing moments of joy and happiness",
            category=PresetCategory.EMOTION_FOCUS,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="target_emotion",
                        value="joy",
                        type="select",
                        description="Primary emotion to capture",
                        options=["joy", "sadness", "anger", "surprise", "fear"]
                    ),
                    PresetParameter(
                        name="brightness",
                        value=0.7,
                        type="range",
                        description="Overall brightness level",
                        min_value=0.3,
                        max_value=1.0
                    ),
                    PresetParameter(
                        name="color_warmth",
                        value=0.8,
                        type="range",
                        description="Color temperature warmth",
                        min_value=0.0,
                        max_value=1.0
                    )
                ],
                camera_settings={
                    "white_balance": "warm",
                    "saturation": 1.2,
                    "exposure": "+0.5"
                },
                shot_settings={
                    "composition": "uplifting",
                    "background": "bright"
                },
                feedback_triggers={
                    "detect_smile": True,
                    "check_brightness": True,
                    "validate_emotion": "joy"
                }
            ),
            tags=[
                PresetTag(name="joyful", color="#FDD835"),
                PresetTag(name="uplifting", color="#FFB300"),
                PresetTag(name="positive", color="#4CAF50")
            ],
            thumbnail_url="/assets/presets/joy_capture.jpg"
        ),
        
        # Genre Style Presets
        PresetTemplate(
            template_id="template_horror_atmosphere",
            name="Horror Atmosphere",
            description="Create suspenseful and eerie atmosphere for horror scenes",
            category=PresetCategory.GENRE_STYLE,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="genre",
                        value="horror",
                        type="select",
                        description="Genre style",
                        options=["horror", "thriller", "drama", "comedy", "action"]
                    ),
                    PresetParameter(
                        name="tension_level",
                        value=0.9,
                        type="range",
                        description="Tension and suspense level",
                        min_value=0.3,
                        max_value=1.0
                    ),
                    PresetParameter(
                        name="color_grading",
                        value="desaturated_cold",
                        type="select",
                        description="Color grading style",
                        options=["desaturated_cold", "high_contrast", "green_tint"]
                    )
                ],
                camera_settings={
                    "angle": "dutch",
                    "movement": "handheld_shaky",
                    "focus": "soft_edges"
                },
                shot_settings={
                    "framing": "uncomfortable",
                    "negative_space": "emphasized",
                    "shadows": "deep"
                }
            ),
            tags=[
                PresetTag(name="horror", color="#5F0A87"),
                PresetTag(name="suspense", color="#1A1A2E"),
                PresetTag(name="eerie", color="#16213E")
            ],
            thumbnail_url="/assets/presets/horror_atmosphere.jpg"
        ),
        
        PresetTemplate(
            template_id="template_romance_soft",
            name="Romantic Soft Focus",
            description="Soft, dreamy aesthetic for romantic scenes",
            category=PresetCategory.GENRE_STYLE,
            visibility=PresetVisibility.SYSTEM,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="genre",
                        value="romance",
                        type="select",
                        description="Genre style",
                        options=["romance", "drama", "comedy"]
                    ),
                    PresetParameter(
                        name="softness",
                        value=0.7,
                        type="range",
                        description="Image softness level",
                        min_value=0.0,
                        max_value=1.0
                    ),
                    PresetParameter(
                        name="bloom_intensity",
                        value=0.5,
                        type="range",
                        description="Bloom/glow effect intensity",
                        min_value=0.0,
                        max_value=1.0
                    )
                ],
                camera_settings={
                    "diffusion_filter": True,
                    "aperture": "f/1.8",
                    "white_balance": "warm_golden"
                },
                shot_settings={
                    "composition": "intimate",
                    "lighting": "soft_natural",
                    "color_palette": "pastels"
                }
            ),
            tags=[
                PresetTag(name="romantic", color="#FF69B4"),
                PresetTag(name="soft", color="#FFB6C1"),
                PresetTag(name="dreamy", color="#DDA0DD")
            ],
            thumbnail_url="/assets/presets/romance_soft.jpg"
        )
    ]
    
    # Insert all templates
    for template in templates:
        await template.insert()
    
    logger.info(f"✅ Seeded {len(templates)} preset templates")
    return templates


async def seed_sample_user_presets():
    """Seed sample user presets for testing"""
    logger.info("Seeding sample user presets...")
    
    # Clear existing user presets
    await UserPreset.delete_all()
    
    # Sample user ID
    user_id = "user_001"
    
    presets = [
        UserPreset(
            preset_id="preset_custom_interview",
            name="My Interview Setup",
            description="Custom preset for interview shots",
            category=PresetCategory.SHOT_COMPOSITION,
            visibility=PresetVisibility.PRIVATE,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="shot_size",
                        value="medium_shot",
                        type="select",
                        options=["medium_shot", "medium_close_up"]
                    ),
                    PresetParameter(
                        name="background_blur",
                        value=0.6,
                        type="range",
                        min_value=0.0,
                        max_value=1.0
                    )
                ],
                camera_settings={"focal_length": 50, "aperture": "f/2.8"}
            ),
            owner_id=user_id,
            based_on_template_id="template_closeup_emotional",
            is_modified=True,
            is_favorite=True,
            tags=[
                PresetTag(name="interview", color="#3498db"),
                PresetTag(name="professional", color="#2ecc71")
            ]
        ),
        
        UserPreset(
            preset_id="preset_action_chase",
            name="Action Chase Sequence",
            description="High-energy preset for chase scenes",
            category=PresetCategory.CAMERA_MOVEMENT,
            visibility=PresetVisibility.PRIVATE,
            config=PresetConfig(
                parameters=[
                    PresetParameter(
                        name="movement_type",
                        value="fast_tracking",
                        type="select",
                        options=["fast_tracking", "handheld", "drone"]
                    ),
                    PresetParameter(
                        name="shutter_speed",
                        value=0.002,
                        type="range",
                        min_value=0.001,
                        max_value=0.01
                    )
                ]
            ),
            owner_id=user_id,
            is_favorite=True,
            tags=[
                PresetTag(name="action", color="#e74c3c"),
                PresetTag(name="fast-paced", color="#f39c12")
            ]
        )
    ]
    
    for preset in presets:
        await preset.insert()
    
    logger.info(f"✅ Seeded {len(presets)} sample user presets")
    return presets


async def seed_sample_collections():
    """Seed sample preset collections"""
    logger.info("Seeding sample collections...")
    
    # Clear existing collections
    await PresetCollection.delete_all()
    
    user_id = "user_001"
    
    collections = [
        PresetCollection(
            collection_id="collection_favorites",
            name="⭐ My Favorites",
            description="Collection of my most-used presets",
            owner_id=user_id,
            preset_ids=["preset_custom_interview", "preset_action_chase"],
            icon="star",
            color="#FFD700",
            sort_order=0
        ),
        
        PresetCollection(
            collection_id="collection_interviews",
            name="🎤 Interview Setups",
            description="All my interview-related presets",
            owner_id=user_id,
            preset_ids=["preset_custom_interview"],
            icon="microphone",
            color="#3498db",
            sort_order=1
        ),
        
        PresetCollection(
            collection_id="collection_action",
            name="💥 Action Scenes",
            description="High-energy action and chase presets",
            owner_id=user_id,
            preset_ids=["preset_action_chase"],
            icon="bolt",
            color="#e74c3c",
            sort_order=2
        )
    ]
    
    for collection in collections:
        await collection.insert()
    
    logger.info(f"✅ Seeded {len(collections)} collections")
    return collections


async def main():
    """Main seeding function"""
    logger.info("🌱 Starting Custom Presets seed process...")
    
    # Initialize database
    await init_db()
    
    # Seed data
    templates = await seed_preset_templates()
    user_presets = await seed_sample_user_presets()
    collections = await seed_sample_collections()
    
    logger.info("=" * 60)
    logger.info("✅ Custom Presets Seeding Complete!")
    logger.info("=" * 60)
    logger.info(f"📋 Preset Templates: {len(templates)}")
    logger.info(f"👤 User Presets: {len(user_presets)}")
    logger.info(f"📁 Collections: {len(collections)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
