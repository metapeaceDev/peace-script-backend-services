"""
🔸 AI Image Generation Module - Stable Diffusion Integration
Generates character images from appearance descriptions

Features:
- Convert ExternalCharacter → SD Prompt
- Integrate with Stable Diffusion API
- Generate portrait images
- Cache generated images
- Support multiple SD models (Realistic Vision, Deliberate, etc.)

Dependencies:
- requests (HTTP client)
- PIL/Pillow (image processing)
- Optional: diffusers library for local generation
"""

from typing import Optional, Dict, List, Literal
from datetime import datetime
from pathlib import Path
import json
import hashlib
from pydantic import BaseModel, Field

from documents_actors import ExternalCharacter
from kamma_appearance_models import KammaAppearanceProfile
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

class SDConfig(BaseModel):
    """Stable Diffusion API Configuration"""
    api_url: str = Field("http://localhost:7860", description="SD WebUI API URL")
    model: str = Field("realisticVisionV51_v51VAE", description="SD model checkpoint")
    sampler: str = Field("DPM++ 2M Karras", description="Sampling method")
    steps: int = Field(30, ge=10, le=150, description="Sampling steps")
    cfg_scale: float = Field(7.0, ge=1, le=30, description="CFG scale")
    width: int = Field(512, description="Image width")
    height: int = Field(768, description="Image height (portrait)")
    seed: int = Field(-1, description="Random seed (-1 for random)")
    negative_prompt: str = Field(
        "ugly, deformed, noisy, blurry, distorted, out of focus, bad anatomy, extra limbs, poorly drawn face, poorly drawn hands, missing fingers",
        description="What to avoid"
    )


# =============================================================================
# PROMPT GENERATION
# =============================================================================

class AppearancePromptGenerator:
    """
    Generate Stable Diffusion prompts from ExternalCharacter
    """
    
    # Quality/Style prefixes
    QUALITY_PREFIX = "(masterpiece:1.2), (best quality:1.2), (ultra-detailed:1.2), (photorealistic:1.4)"
    
    # Buddhist/Thai context (optional)
    THAI_CONTEXT = "Thai person, Southeast Asian features"
    
    def generate_prompt(
        self,
        external: ExternalCharacter,
        kamma_profile: Optional[KammaAppearanceProfile] = None,
        style: Literal["realistic", "anime", "portrait", "cinematic"] = "realistic",
        include_buddhist_context: bool = True
    ) -> Dict[str, str]:
        """
        Generate SD prompt from ExternalCharacter
        
        Returns:
            Dict with 'positive' and 'negative' prompts
        """
        logger.info("Generating SD prompt from ExternalCharacter")
        
        # Build components
        components = []
        
        # Quality/Style prefix
        if style == "realistic":
            components.append(self.QUALITY_PREFIX)
            components.append("professional headshot portrait, studio lighting, white background, front view, looking at camera, passport photo style, professional photography, 8k uhd, dslr")
        elif style == "anime":
            components.append("anime style, highly detailed, cel shading")
        elif style == "portrait":
            components.append("professional headshot portrait, studio lighting, white background, front view, looking at camera, passport photo style, portrait photography, 85mm lens")
        elif style == "cinematic":
            components.append("cinematic lighting, dramatic, film grain, anamorphic lens")
        
        # Buddhist/Cultural context
        if include_buddhist_context and external.ethnicity == "Thai":
            components.append(self.THAI_CONTEXT)
        
        # Physical characteristics
        physical = self._generate_physical_prompt(external)
        components.append(physical)
        
        # Facial features
        facial = self._generate_facial_prompt(external)
        components.append(facial)
        
        # Expression & demeanor
        expression = self._generate_expression_prompt(external)
        components.append(expression)
        
        # Clothing & style
        clothing = self._generate_clothing_prompt(external)
        if clothing:
            components.append(clothing)
        
        # Kamma-specific traits (if available)
        if kamma_profile:
            kamma_traits = self._generate_kamma_traits(kamma_profile)
            if kamma_traits:
                components.append(kamma_traits)
        
        # Camera/Setting - แบบโปรไฟล์แนวตั้ง
        components.append("centered composition, head and shoulders portrait, vertical composition, single person only")
        
        # Join all components
        positive_prompt = ", ".join(components)
        
        # Negative prompt (what to avoid)
        negative_prompt = self._generate_negative_prompt(external)
        
        logger.info(f"Generated prompt length: {len(positive_prompt)} chars")
        
        return {
            "positive": positive_prompt,
            "negative": negative_prompt
        }
    
    def _generate_physical_prompt(self, external: ExternalCharacter) -> str:
        """Generate physical appearance part of prompt"""
        parts = []
        
        # Gender & Age
        if external.gender:
            parts.append(f"{external.age if external.age else 'adult'} year old {external.gender}")
        
        # Body type
        if external.body_type:
            # Map body_type to SD-friendly terms
            body_map = {
                "slim": "slim, slender",
                "athletic": "athletic, fit, toned",
                "muscular": "muscular, well-built",
                "average": "average build",
                "heavyset": "heavyset, stocky",
                "frail": "thin, delicate frame",
                "robust": "robust, strong build"
            }
            body_desc = body_map.get(external.body_type.split(",")[0].strip(), external.body_type)
            parts.append(body_desc)
        
        # Height (relative)
        if external.height:
            if external.height >= 180:
                parts.append("tall")
            elif external.height <= 160:
                parts.append("petite")
        
        # Fitness level
        if external.fitness_level >= 8:
            parts.append("very fit, defined muscles")
        elif external.fitness_level <= 3:
            parts.append("low fitness, soft body")
        
        return ", ".join(parts)
    
    def _generate_facial_prompt(self, external: ExternalCharacter) -> str:
        """Generate facial features part of prompt"""
        parts = []
        
        # Face shape
        if external.face_shape:
            parts.append(f"{external.face_shape} face")
        
        # Skin tone (CRITICAL for kamma influence)
        if external.skin_tone:
            # Map to SD-friendly terms
            skin_map = {
                "radiant": "radiant skin, healthy glow, luminous",
                "healthy": "healthy skin tone, clear complexion",
                "pale": "pale skin, fair complexion",
                "sickly": "pale, slightly sallow skin",
                "fair": "fair skin",
                "tan": "tan skin, sun-kissed",
                "dark": "dark skin tone"
            }
            # Check for multiple descriptors
            for key, value in skin_map.items():
                if key in external.skin_tone.lower():
                    parts.append(value)
                    break
            else:
                parts.append(external.skin_tone)
        
        # Eyes
        if external.eye_color:
            parts.append(f"{external.eye_color} eyes")
        
        # Hair
        if external.hair_color and external.hair_style:
            parts.append(f"{external.hair_style} {external.hair_color} hair")
        elif external.hair_color:
            parts.append(f"{external.hair_color} hair")
        
        # Distinctive features
        if external.distinctive_features:
            for feature in external.distinctive_features[:2]:  # Max 2 to avoid clutter
                # Filter out abstract kamma descriptions
                if not any(word in feature.lower() for word in ["from", "practice", "kamma", "karma"]):
                    parts.append(feature)
        
        return ", ".join(parts)
    
    def _generate_expression_prompt(self, external: ExternalCharacter) -> str:
        """Generate expression & demeanor part of prompt"""
        parts = []
        
        # First impression (overall vibe)
        if external.first_impression:
            # Map to visual terms
            impression_map = {
                "warm": "warm expression, friendly demeanor",
                "trustworthy": "trustworthy face, honest look",
                "peaceful": "peaceful expression, serene face",
                "tense": "tense expression, worried look",
                "hostile": "stern expression, intense gaze",
                "cold": "cold expression, distant look"
            }
            for key, value in impression_map.items():
                if key in external.first_impression.lower():
                    parts.append(value)
                    break
        
        # Posture (for body language in portrait)
        if external.posture:
            posture_map = {
                "upright": "confident posture, shoulders back",
                "slouched": "slouched posture",
                "tense": "tense shoulders, rigid posture",
                "relaxed": "relaxed posture, at ease"
            }
            for key, value in posture_map.items():
                if key in external.posture.lower():
                    parts.append(value)
                    break
        
        # Charisma (subtle influence)
        if external.charisma_level >= 8:
            parts.append("charismatic presence, captivating")
        
        return ", ".join(parts) if parts else "neutral expression"
    
    def _generate_clothing_prompt(self, external: ExternalCharacter) -> str:
        """Generate clothing & style part of prompt"""
        parts = []
        
        if external.fashion_style:
            # Map to visual terms
            style_map = {
                "casual": "casual clothing, everyday wear",
                "formal": "formal attire, professional clothing",
                "simple": "simple clothing, minimalist style",
                "well-maintained": "well-dressed, neat appearance",
                "comfortable": "comfortable clothing, relaxed fit"
            }
            for key, value in style_map.items():
                if key in external.fashion_style.lower():
                    parts.append(value)
                    break
        
        # Color palette
        if external.color_palette:
            colors = ", ".join(external.color_palette[:2])
            parts.append(f"wearing {colors}")
        
        return ", ".join(parts)
    
    def _generate_kamma_traits(self, profile: KammaAppearanceProfile) -> str:
        """Generate kamma-specific visual traits"""
        parts = []
        
        # High kusala indicators
        if profile.kusala_percentage >= 70:
            parts.append("peaceful aura, inner light")
        
        # Mettā influence
        if profile.demeanor_score.loving_kindness_score >= 80:
            parts.append("compassionate eyes, gentle smile")
        
        # Health from protection
        if profile.health_score.protection_kamma_score >= 80:
            parts.append("vibrant, energetic presence")
        
        # Meditation influence
        if profile.demeanor_score.peacefulness >= 80:
            parts.append("serene expression, mindful presence")
        
        return ", ".join(parts)
    
    def _generate_negative_prompt(self, external: ExternalCharacter) -> str:
        """Generate negative prompt (what to avoid)"""
        base_negative = [
            # ❌ หลีกเลี่ยงคุณภาพต่ำ
            "ugly, deformed, noisy, blurry, distorted",
            "out of focus, bad anatomy, extra limbs",
            "poorly drawn face, poorly drawn hands",
            "missing fingers, extra fingers, mutated hands",
            "bad proportions, gross proportions",
            "duplicate, watermark, signature, text, logo",
            "lowres, low quality, worst quality",
            
            # ❌ หลีกเลี่ยงคนหลายคน (สำหรับรูปโปรไฟล์)
            "multiple people, group photo, crowd, two people, three people",
            "multiple persons, many people, people in background",
            
            # ❌ หลีกเลี่ยงมุมกล้องแปลก
            "side view, back view, profile view, looking away",
            "tilted head, extreme angle, bird's eye view, worm's eye view",
            
            # ❌ หลีกเลี่ยงแสงไม่สม่ำเสมอ
            "dark lighting, harsh shadows, uneven lighting",
            "overexposed, underexposed, dramatic shadows",
            
            # ❌ หลีกเลี่ยงพื้นหลังรกรุงรัง
            "busy background, cluttered background, colorful background",
            "outdoor, nature, city, buildings, objects in background"
        ]
        
        # Add context-specific negatives
        if external.health_status and "excellent" in external.health_status.lower():
            base_negative.append("sickly, pale, unhealthy")
        
        return ", ".join(base_negative)


# =============================================================================
# STABLE DIFFUSION API CLIENT
# =============================================================================

class StableDiffusionClient:
    """
    Client for Stable Diffusion WebUI API (AUTOMATIC1111)
    """
    
    def __init__(self, config: SDConfig = SDConfig()):
        self.config = config
        self.prompt_generator = AppearancePromptGenerator()
    
    def generate_image(
        self,
        external: ExternalCharacter,
        kamma_profile: Optional[KammaAppearanceProfile] = None,
        style: str = "realistic",
        output_path: Optional[Path] = None
    ) -> Dict:
        """
        Generate image from ExternalCharacter
        
        Args:
            external: ExternalCharacter to visualize
            kamma_profile: Optional kamma profile for additional traits
            style: Image style (realistic/anime/portrait/cinematic)
            output_path: Where to save image
            
        Returns:
            Dict with image data and metadata
        """
        try:
            import requests
            from PIL import Image
            import io
            import base64
        except ImportError:
            logger.error("requests or PIL not installed. Install with: pip install requests Pillow")
            return {"error": "Missing dependencies: requests, Pillow"}
        
        logger.info(f"Generating image for character via SD API")
        
        # Generate prompts
        prompts = self.prompt_generator.generate_prompt(
            external,
            kamma_profile,
            style=style
        )
        
        # Prepare API payload
        payload = {
            "prompt": prompts["positive"],
            "negative_prompt": prompts["negative"],
            "sampler_name": self.config.sampler,
            "steps": self.config.steps,
            "cfg_scale": self.config.cfg_scale,
            "width": self.config.width,
            "height": self.config.height,
            "seed": self.config.seed,
            "batch_size": 1,
            "n_iter": 1,
        }
        
        # Call SD API
        try:
            response = requests.post(
                f"{self.config.api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=120  # 2 minutes max
            )
            
            if response.status_code != 200:
                logger.error(f"SD API error: {response.status_code}")
                return {
                    "error": f"SD API returned {response.status_code}",
                    "prompts": prompts
                }
            
            result = response.json()
            
            # Decode image
            if "images" not in result or not result["images"]:
                logger.error("No images in SD response")
                return {"error": "No images generated", "prompts": prompts}
            
            image_data = result["images"][0]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Save if output path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                logger.info(f"Saved image to: {output_path}")
            
            # Get seed used
            seed_used = result.get("info", {}).get("seed", -1)
            
            return {
                "success": True,
                "image": image,
                "image_base64": image_data,
                "prompts": prompts,
                "seed": seed_used,
                "width": self.config.width,
                "height": self.config.height,
                "model": self.config.model,
                "saved_to": str(output_path) if output_path else None
            }
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to SD API at {self.config.api_url}")
            return {
                "error": "Cannot connect to Stable Diffusion API. Is it running?",
                "api_url": self.config.api_url,
                "prompts": prompts
            }
        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            return {"error": str(e), "prompts": prompts}
    
    def generate_prompt_only(
        self,
        external: ExternalCharacter,
        kamma_profile: Optional[KammaAppearanceProfile] = None,
        style: str = "realistic"
    ) -> Dict[str, str]:
        """
        Generate prompt without calling SD API
        Useful for testing or manual generation
        """
        return self.prompt_generator.generate_prompt(
            external,
            kamma_profile,
            style=style
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_character_image(
    external: ExternalCharacter,
    kamma_profile: Optional[KammaAppearanceProfile] = None,
    output_path: Optional[str] = None,
    sd_api_url: str = "http://localhost:7860",
    style: str = "realistic"
) -> Dict:
    """
    Convenience function to generate character image
    
    Example:
        >>> external = synthesize_from_model(profile)
        >>> result = generate_character_image(
        ...     external,
        ...     output_path="output/character_001.png"
        ... )
        >>> if result.get("success"):
        ...     print(f"Image saved to: {result['saved_to']}")
    """
    config = SDConfig(api_url=sd_api_url)
    client = StableDiffusionClient(config)
    
    path = Path(output_path) if output_path else None
    
    return client.generate_image(
        external,
        kamma_profile,
        style=style,
        output_path=path
    )


def get_prompt_for_character(
    external: ExternalCharacter,
    kamma_profile: Optional[KammaAppearanceProfile] = None,
    style: str = "realistic"
) -> Dict[str, str]:
    """
    Get SD prompt without generating image
    
    Example:
        >>> external = synthesize_from_model(profile)
        >>> prompts = get_prompt_for_character(external)
        >>> print(prompts["positive"])
    """
    generator = AppearancePromptGenerator()
    return generator.generate_prompt(external, kamma_profile, style=style)
