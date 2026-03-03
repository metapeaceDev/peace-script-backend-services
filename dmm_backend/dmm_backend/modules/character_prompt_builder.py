"""
🎭 Character Prompt Builder Module

Converts ActorProfile data into enhanced prompts for video generation.
Integrates character appearance, personality, and mood into AI prompts.

Features:
- Build character-enhanced prompts from ActorProfile
- Merge character data with user prompts
- Support appearance, personality, and emotional state
- Generate Stable Diffusion-compatible prompts

Author: Peace Script Team
Date: 25 November 2025
Version: 1.0.0
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field

from documents_actors import ActorProfile, InternalCharacter, ExternalCharacter
from modules.ai_image_generator import AppearancePromptGenerator
from kamma_appearance_models import KammaAppearanceProfile
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# MODELS
# =============================================================================

class CharacterPromptOptions(BaseModel):
    """Options for character prompt building"""
    use_appearance: bool = Field(default=True, description="Include appearance traits")
    use_personality: bool = Field(default=False, description="Include personality traits")
    use_mood: bool = Field(default=False, description="Include emotional state")
    emotion: Optional[str] = Field(default=None, description="Current emotion (e.g., 'happy', 'sad', 'angry')")
    style: str = Field(default="realistic", description="Visual style (realistic/anime/portrait/cinematic)")
    include_clothing: bool = Field(default=True, description="Include clothing description")
    include_expression: bool = Field(default=True, description="Include facial expression")


class CharacterPromptResult(BaseModel):
    """Result of character prompt building"""
    character_prompt: str = Field(..., description="Generated character prompt")
    positive_prompt: str = Field(..., description="Full positive prompt (character + user)")
    negative_prompt: str = Field(..., description="Negative prompt (what to avoid)")
    character_name: str = Field(..., description="Character name")
    actor_id: str = Field(..., description="Actor ID")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")


# =============================================================================
# CHARACTER PROMPT BUILDER
# =============================================================================

class CharacterPromptBuilder:
    """
    Build enhanced prompts from ActorProfile data
    
    Usage:
        builder = CharacterPromptBuilder()
        result = await builder.build_prompt(
            actor=actor_profile,
            user_prompt="standing in forest",
            options=CharacterPromptOptions(use_appearance=True)
        )
        print(result.positive_prompt)
    """
    
    def __init__(self):
        """Initialize builder"""
        self.appearance_generator = AppearancePromptGenerator()
        logger.info("CharacterPromptBuilder initialized")
    
    async def build_prompt(
        self,
        actor: ActorProfile,
        user_prompt: Optional[str] = None,
        options: Optional[CharacterPromptOptions] = None
    ) -> CharacterPromptResult:
        """
        Build enhanced prompt from actor profile
        
        Args:
            actor: ActorProfile with character data
            user_prompt: User's custom prompt (scene description)
            options: Options for prompt building
            
        Returns:
            CharacterPromptResult with all prompt components
            
        Example:
            >>> actor = await ActorProfile.find_one({"actor_id": "ACT-001"})
            >>> result = await builder.build_prompt(
            ...     actor=actor,
            ...     user_prompt="walking through ancient temple",
            ...     options=CharacterPromptOptions(use_appearance=True, use_mood=True, emotion="peaceful")
            ... )
            >>> print(result.positive_prompt)
        """
        logger.info(f"Building prompt for actor: {actor.actor_name} ({actor.actor_id})")
        
        # Default options
        if options is None:
            options = CharacterPromptOptions()
        
        # Build character prompt components
        components = []
        metadata = {}
        
        # 1. APPEARANCE (from ExternalCharacter)
        if options.use_appearance and actor.external_character:
            appearance_prompt = self._build_appearance_prompt(
                actor.external_character,
                options
            )
            if appearance_prompt:
                components.append(appearance_prompt)
                metadata["has_appearance"] = True
                logger.debug(f"Added appearance: {appearance_prompt[:100]}...")
        
        # 2. PERSONALITY (from InternalCharacter)
        if options.use_personality and actor.internal_character:
            personality_prompt = self._build_personality_prompt(
                actor.internal_character,
                options
            )
            if personality_prompt:
                components.append(personality_prompt)
                metadata["has_personality"] = True
                logger.debug(f"Added personality: {personality_prompt[:100]}...")
        
        # 3. EMOTIONAL STATE (from options or InternalCharacter)
        if options.use_mood:
            mood_prompt = self._build_mood_prompt(
                actor.internal_character,
                options.emotion
            )
            if mood_prompt:
                components.append(mood_prompt)
                metadata["has_mood"] = True
                logger.debug(f"Added mood: {mood_prompt}")
        
        # 4. USER PROMPT (scene context)
        if user_prompt and user_prompt.strip():
            components.append(user_prompt.strip())
            metadata["has_user_prompt"] = True
        
        # Combine character prompt
        character_prompt = ", ".join(components[:3])  # Appearance + Personality + Mood
        
        # Combine full positive prompt
        positive_prompt = ", ".join(components)
        
        # Generate negative prompt
        negative_prompt = self._build_negative_prompt(actor.external_character)
        
        # Build result
        result = CharacterPromptResult(
            character_prompt=character_prompt,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            character_name=actor.actor_name,
            actor_id=actor.actor_id,
            metadata=metadata
        )
        
        logger.info(f"✅ Built prompt for {actor.actor_name} ({len(positive_prompt)} chars)")
        return result
    
    def _build_appearance_prompt(
        self,
        external: ExternalCharacter,
        options: CharacterPromptOptions
    ) -> str:
        """Build appearance prompt from ExternalCharacter"""
        try:
            # Use existing AppearancePromptGenerator
            prompts = self.appearance_generator.generate_prompt(
                external=external,
                kamma_profile=None,
                style=options.style,
                include_buddhist_context=False
            )
            
            # Extract appearance parts (without quality prefix)
            appearance_parts = prompts["positive"].replace(
                self.appearance_generator.QUALITY_PREFIX,
                ""
            ).strip()
            
            # Remove unnecessary parts for video
            appearance_parts = appearance_parts.replace("professional photography, studio lighting, 8k uhd, dslr, ", "")
            appearance_parts = appearance_parts.replace("centered composition, upper body portrait, ", "")
            
            return appearance_parts.strip(", ")
            
        except Exception as e:
            logger.error(f"Failed to build appearance prompt: {e}")
            return ""
    
    def _build_personality_prompt(
        self,
        internal: Optional[InternalCharacter],
        options: CharacterPromptOptions
    ) -> str:
        """Build personality prompt from InternalCharacter"""
        if not internal:
            return ""
        
        parts = []
        
        # Map personality traits to visual cues
        # High openness → curious expression, alert posture
        if internal.openness >= 7:
            parts.append("curious expression, alert posture")
        elif internal.openness <= 3:
            parts.append("reserved demeanor, guarded posture")
        
        # High conscientiousness → composed, organized appearance
        if internal.conscientiousness >= 7:
            parts.append("composed demeanor, neat appearance")
        
        # High extraversion → warm, engaging expression
        if internal.extraversion >= 7:
            parts.append("warm expression, engaging presence")
        elif internal.extraversion <= 3:
            parts.append("reserved expression, introverted demeanor")
        
        # High agreeableness → friendly, approachable look
        if internal.agreeableness >= 7:
            parts.append("friendly demeanor, approachable")
        
        # High neuroticism → tense, anxious expression
        if internal.neuroticism >= 7:
            parts.append("tense expression, worried look")
        elif internal.neuroticism <= 3:
            parts.append("calm expression, relaxed")
        
        return ", ".join(parts) if parts else ""
    
    def _build_mood_prompt(
        self,
        internal: Optional[InternalCharacter],
        emotion: Optional[str]
    ) -> str:
        """Build mood/emotion prompt"""
        # Use explicit emotion if provided
        if emotion:
            emotion_map = {
                "happy": "happy expression, smiling, joyful demeanor",
                "sad": "sad expression, downcast eyes, somber mood",
                "angry": "angry expression, furrowed brows, tense jaw",
                "fearful": "fearful expression, wide eyes, anxious",
                "surprised": "surprised expression, raised eyebrows, open mouth",
                "disgusted": "disgusted expression, wrinkled nose",
                "neutral": "neutral expression, calm demeanor",
                "peaceful": "peaceful expression, serene face, relaxed",
                "excited": "excited expression, bright eyes, energetic",
                "worried": "worried expression, concerned look",
                "confident": "confident expression, assured demeanor",
                "shy": "shy expression, averted gaze, timid"
            }
            return emotion_map.get(emotion.lower(), f"{emotion} expression")
        
        # Infer from personality (if no explicit emotion)
        if internal:
            if internal.kusala_percentage >= 80:
                return "peaceful expression, serene demeanor"
            elif internal.akusala_percentage >= 60:
                return "tense expression, troubled look"
        
        return ""
    
    def _build_negative_prompt(
        self,
        external: Optional[ExternalCharacter]
    ) -> str:
        """Build negative prompt (what to avoid)"""
        # Use existing generator if available
        if external:
            try:
                return self.appearance_generator._generate_negative_prompt(external)
            except:
                pass
        
        # Default negative prompt for video
        return (
            "blurry, low quality, distorted face, extra limbs, "
            "bad anatomy, disfigured, mutation, watermark, text, "
            "multiple people, duplicate, ugly, poorly drawn"
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def build_character_prompt(
    actor_id: str,
    user_prompt: Optional[str] = None,
    use_appearance: bool = True,
    use_personality: bool = False,
    use_mood: bool = False,
    emotion: Optional[str] = None,
    style: str = "realistic"
) -> CharacterPromptResult:
    """
    Convenience function to build character prompt
    
    Args:
        actor_id: Actor ID (e.g., "ACT-001")
        user_prompt: User's scene description
        use_appearance: Include appearance traits
        use_personality: Include personality traits
        use_mood: Include emotional state
        emotion: Current emotion (if use_mood=True)
        style: Visual style
        
    Returns:
        CharacterPromptResult
        
    Example:
        >>> result = await build_character_prompt(
        ...     actor_id="ACT-001",
        ...     user_prompt="walking through temple",
        ...     use_appearance=True,
        ...     use_mood=True,
        ...     emotion="peaceful"
        ... )
        >>> print(result.positive_prompt)
    """
    # Find actor
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise ValueError(f"Actor {actor_id} not found")
    
    # Build options
    options = CharacterPromptOptions(
        use_appearance=use_appearance,
        use_personality=use_personality,
        use_mood=use_mood,
        emotion=emotion,
        style=style
    )
    
    # Build prompt
    builder = CharacterPromptBuilder()
    return await builder.build_prompt(
        actor=actor,
        user_prompt=user_prompt,
        options=options
    )


async def get_character_prompt_only(
    actor_id: str,
    style: str = "realistic"
) -> str:
    """
    Get character appearance prompt only (no user prompt)
    
    Example:
        >>> prompt = await get_character_prompt_only("ACT-001")
        >>> print(prompt)
        "Thai woman, 28 years old, oval face, dark brown eyes, ..."
    """
    result = await build_character_prompt(
        actor_id=actor_id,
        user_prompt=None,
        use_appearance=True,
        use_personality=False,
        use_mood=False,
        style=style
    )
    return result.character_prompt
