"""
🔊 Voice Synthesis Module - TTS Integration
Synthesizes character voice from VoiceScore

Features:
- Convert VoiceScore → TTS parameters
- Multiple TTS engines (Google TTS, ElevenLabs, Coqui TTS)
- Voice quality mapping from kamma
- Audio file generation and caching
- Buddhist-accurate voice characteristics

Dependencies:
- gTTS (Google Text-to-Speech) - Free, simple
- elevenlabs (Premium, high quality) - Optional
- TTS (Coqui TTS) - Local, customizable - Optional
"""

from typing import Optional, Dict, List, Literal, Tuple
from datetime import datetime
from pathlib import Path
import hashlib
import json
from pydantic import BaseModel, Field

from kamma_appearance_models import VoiceScore, KammaAppearanceProfile
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

class TTSConfig(BaseModel):
    """Text-to-Speech Configuration"""
    engine: Literal["gtts", "elevenlabs", "coqui"] = Field("gtts", description="TTS engine to use")
    
    # Google TTS settings
    gtts_lang: str = Field("th", description="Language code (th, en, etc.)")
    gtts_slow: bool = Field(False, description="Slow speech rate")
    
    # ElevenLabs settings (requires API key)
    elevenlabs_api_key: Optional[str] = Field(None, description="ElevenLabs API key")
    elevenlabs_voice_id: Optional[str] = Field(None, description="Voice ID to use")
    elevenlabs_stability: float = Field(0.5, ge=0, le=1, description="Voice stability")
    elevenlabs_similarity: float = Field(0.75, ge=0, le=1, description="Voice similarity")
    
    # Coqui TTS settings (local)
    coqui_model: str = Field("tts_models/multilingual/multi-dataset/your_tts", description="Coqui model")
    coqui_speaker: Optional[str] = Field(None, description="Speaker name")
    
    # General audio settings
    output_format: Literal["mp3", "wav", "ogg"] = Field("mp3", description="Audio format")
    sample_rate: int = Field(22050, description="Audio sample rate")
    cache_audio: bool = Field(True, description="Cache generated audio")
    cache_dir: str = Field("audio_cache", description="Cache directory")


# =============================================================================
# VOICE PARAMETER MAPPING
# =============================================================================

class VoiceParameters(BaseModel):
    """Voice synthesis parameters derived from VoiceScore"""
    
    # Core voice characteristics
    pitch: float = Field(..., ge=0.5, le=2.0, description="Voice pitch (1.0 = normal)")
    speed: float = Field(..., ge=0.5, le=2.0, description="Speech speed (1.0 = normal)")
    volume: float = Field(..., ge=0.0, le=1.0, description="Volume level")
    warmth: float = Field(..., ge=0.0, le=1.0, description="Voice warmth/friendliness")
    
    # Advanced characteristics
    clarity: float = Field(..., ge=0.0, le=1.0, description="Speech clarity")
    resonance: float = Field(..., ge=0.0, le=1.0, description="Voice resonance/depth")
    tension: float = Field(..., ge=0.0, le=1.0, description="Vocal tension")
    breathiness: float = Field(..., ge=0.0, le=1.0, description="Breathy quality")
    
    # Emotional tone
    emotional_tone: str = Field(..., description="Overall emotional quality")
    energy_level: float = Field(..., ge=0.0, le=1.0, description="Vocal energy")
    
    # Buddhist influence markers
    metta_influence: float = Field(..., ge=0.0, le=1.0, description="Loving-kindness in voice")
    truthfulness_marker: float = Field(..., ge=0.0, le=1.0, description="Honesty marker")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pitch": 1.0,
                "speed": 0.95,
                "volume": 0.8,
                "warmth": 0.9,
                "clarity": 0.95,
                "resonance": 0.7,
                "tension": 0.2,
                "breathiness": 0.3,
                "emotional_tone": "warm and gentle",
                "energy_level": 0.7,
                "metta_influence": 0.9,
                "truthfulness_marker": 0.95
            }
        }


class VoiceParameterMapper:
    """
    Maps VoiceScore to synthesizer parameters
    
    Buddhist Mappings:
    - Truthful Speech (Musāvāda veramaṇī) → Clear, stable voice
    - Harsh Speech (Pharusā vācā veramaṇī) → Soft, gentle voice
    - Mettā practice → Warm, compassionate tone
    - Lying → Unclear, unstable voice
    """
    
    def map_voice_score(self, voice_score: VoiceScore) -> VoiceParameters:
        """
        Convert VoiceScore → VoiceParameters
        
        Algorithm:
        1. Base parameters from voice_quality
        2. Adjust clarity from speech_clarity
        3. Add warmth from vocal_warmth
        4. Apply kamma modifiers (truthful/harsh speech)
        5. Add emotional tone
        """
        logger.info("Mapping VoiceScore to synthesis parameters")
        
        # 1. Base pitch (from voice quality)
        # Higher quality → more resonant (slightly lower pitch)
        pitch = self._calculate_pitch(voice_score)
        
        # 2. Speech speed (from clarity and effectiveness)
        speed = self._calculate_speed(voice_score)
        
        # 3. Volume (from overall quality)
        volume = self._calculate_volume(voice_score)
        
        # 4. Warmth (critical for mettā)
        warmth = voice_score.vocal_warmth / 100.0
        
        # 5. Clarity (from speech_clarity and truthfulness)
        clarity = self._calculate_clarity(voice_score)
        
        # 6. Resonance (depth and richness)
        resonance = self._calculate_resonance(voice_score)
        
        # 7. Tension (inverse of calmness)
        tension = self._calculate_tension(voice_score)
        
        # 8. Breathiness (relates to energy and health)
        breathiness = self._calculate_breathiness(voice_score)
        
        # 9. Emotional tone (descriptive)
        emotional_tone = self._determine_emotional_tone(voice_score)
        
        # 10. Energy level
        energy_level = voice_score.communication_effectiveness / 100.0
        
        # 11. Mettā influence
        metta_influence = min(1.0, voice_score.vocal_warmth / 100.0)
        
        # 12. Truthfulness marker
        truthfulness_marker = voice_score.truthful_speech_score / 100.0
        
        params = VoiceParameters(
            pitch=pitch,
            speed=speed,
            volume=volume,
            warmth=warmth,
            clarity=clarity,
            resonance=resonance,
            tension=tension,
            breathiness=breathiness,
            emotional_tone=emotional_tone,
            energy_level=energy_level,
            metta_influence=metta_influence,
            truthfulness_marker=truthfulness_marker
        )
        
        logger.info(f"Mapped parameters: pitch={pitch:.2f}, speed={speed:.2f}, warmth={warmth:.2f}")
        
        return params
    
    def _calculate_pitch(self, voice_score: VoiceScore) -> float:
        """
        Calculate voice pitch
        
        Higher quality → more natural pitch (1.0)
        Tension → higher pitch
        Warmth → slightly lower pitch
        """
        base_pitch = 1.0
        
        # Quality adjustment (70-100 → 0.9-1.1)
        quality_factor = (voice_score.voice_quality - 50) / 500.0
        
        # Warmth lowers pitch slightly
        warmth_factor = -0.05 * (voice_score.vocal_warmth / 100.0)
        
        pitch = base_pitch + quality_factor + warmth_factor
        
        return max(0.5, min(2.0, pitch))
    
    def _calculate_speed(self, voice_score: VoiceScore) -> float:
        """
        Calculate speech speed
        
        High clarity → moderate speed (0.9-1.0)
        Low clarity → slower or erratic
        High effectiveness → confident speed
        """
        # Base speed from clarity
        if voice_score.speech_clarity >= 80:
            base_speed = 0.95  # Clear, confident
        elif voice_score.speech_clarity >= 60:
            base_speed = 0.9   # Moderate
        else:
            base_speed = 0.85  # Slower, less confident
        
        # Adjust for communication effectiveness
        effectiveness_factor = (voice_score.communication_effectiveness - 50) / 500.0
        
        speed = base_speed + effectiveness_factor
        
        return max(0.5, min(2.0, speed))
    
    def _calculate_volume(self, voice_score: VoiceScore) -> float:
        """
        Calculate volume level
        
        Higher quality → good volume control (0.7-0.9)
        """
        # Map 0-100 to 0.5-1.0
        volume = 0.5 + (voice_score.voice_quality / 200.0)
        
        return max(0.0, min(1.0, volume))
    
    def _calculate_clarity(self, voice_score: VoiceScore) -> float:
        """
        Calculate speech clarity
        
        High truthful_speech_score → crystal clear
        Low truthful_speech_score → muddy, unclear
        """
        # Base clarity
        base_clarity = voice_score.speech_clarity / 100.0
        
        # Truthfulness boost
        truth_bonus = (voice_score.truthful_speech_score - 50) / 200.0
        
        clarity = base_clarity + truth_bonus
        
        return max(0.0, min(1.0, clarity))
    
    def _calculate_resonance(self, voice_score: VoiceScore) -> float:
        """
        Calculate voice resonance (depth)
        
        High quality + warmth → good resonance
        """
        quality_component = voice_score.voice_quality / 100.0
        warmth_component = voice_score.vocal_warmth / 100.0
        
        resonance = (quality_component + warmth_component) / 2.0
        
        return max(0.0, min(1.0, resonance))
    
    def _calculate_tension(self, voice_score: VoiceScore) -> float:
        """
        Calculate vocal tension
        
        Harsh speech → high tension
        Gentle speech → low tension
        """
        # Harsh speech creates tension
        tension = voice_score.harsh_speech_score / 100.0
        
        return max(0.0, min(1.0, tension))
    
    def _calculate_breathiness(self, voice_score: VoiceScore) -> float:
        """
        Calculate breathy quality
        
        Lower energy/quality → more breathiness
        """
        # Inverse of quality
        breathiness = 1.0 - (voice_score.voice_quality / 100.0)
        
        # Clamp to reasonable range
        breathiness = max(0.1, min(0.5, breathiness))
        
        return breathiness
    
    def _determine_emotional_tone(self, voice_score: VoiceScore) -> str:
        """
        Determine overall emotional tone
        """
        warmth = voice_score.vocal_warmth
        clarity = voice_score.speech_clarity
        harsh = voice_score.harsh_speech_score
        truth = voice_score.truthful_speech_score
        
        # High warmth, high truth, low harsh
        if warmth >= 80 and truth >= 80 and harsh <= 20:
            return "warm, gentle, and trustworthy"
        
        # High clarity, moderate warmth
        elif clarity >= 80 and warmth >= 60:
            return "clear, confident, and friendly"
        
        # High harsh, low warmth
        elif harsh >= 60 and warmth <= 40:
            return "harsh, tense, and sharp"
        
        # Low truth, low clarity
        elif truth <= 40 and clarity <= 40:
            return "unclear, hesitant, and evasive"
        
        # Moderate everything
        elif 50 <= warmth <= 70 and 50 <= clarity <= 70:
            return "neutral and balanced"
        
        # High energy, high clarity
        elif clarity >= 80:
            return "clear and articulate"
        
        # Default
        else:
            return "moderate tone"


# =============================================================================
# TTS ENGINES
# =============================================================================

class GoogleTTSEngine:
    """
    Google Text-to-Speech (gTTS)
    
    Pros:
    - Free, unlimited
    - Easy to use
    - Supports 100+ languages
    
    Cons:
    - Limited voice control
    - Cannot adjust pitch/speed directly
    - Robotic quality
    """
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.mapper = VoiceParameterMapper()
    
    def synthesize(
        self,
        text: str,
        voice_score: VoiceScore,
        output_path: Path
    ) -> Dict:
        """
        Synthesize speech using Google TTS
        """
        try:
            from gtts import gTTS
        except ImportError:
            logger.error("gTTS not installed. Install with: pip install gTTS")
            return {"error": "gTTS not installed"}
        
        logger.info(f"Synthesizing with Google TTS: {len(text)} chars")
        
        # Map voice parameters
        params = self.mapper.map_voice_score(voice_score)
        
        # Google TTS has limited controls
        # We can only set language and speed
        try:
            tts = gTTS(
                text=text,
                lang=self.config.gtts_lang,
                slow=params.speed < 0.8  # Use slow mode if speed is low
            )
            
            # Save audio
            output_path.parent.mkdir(parents=True, exist_ok=True)
            tts.save(str(output_path))
            
            logger.info(f"Saved audio to: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "engine": "gtts",
                "parameters": params.dict(),
                "text_length": len(text),
                "language": self.config.gtts_lang
            }
            
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}", exc_info=True)
            return {"error": str(e)}


class ElevenLabsEngine:
    """
    ElevenLabs TTS (Premium)
    
    Pros:
    - Extremely realistic voices
    - Fine control over voice parameters
    - Emotional expression
    - Multiple voice models
    
    Cons:
    - Requires API key (paid)
    - Rate limits
    - Online only
    """
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.mapper = VoiceParameterMapper()
    
    def synthesize(
        self,
        text: str,
        voice_score: VoiceScore,
        output_path: Path
    ) -> Dict:
        """
        Synthesize speech using ElevenLabs
        """
        if not self.config.elevenlabs_api_key:
            return {"error": "ElevenLabs API key not configured"}
        
        try:
            from elevenlabs import generate, set_api_key, voices
        except ImportError:
            logger.error("elevenlabs not installed. Install with: pip install elevenlabs")
            return {"error": "elevenlabs not installed"}
        
        logger.info(f"Synthesizing with ElevenLabs: {len(text)} chars")
        
        # Set API key
        set_api_key(self.config.elevenlabs_api_key)
        
        # Map voice parameters
        params = self.mapper.map_voice_score(voice_score)
        
        try:
            # Select voice based on parameters
            voice_id = self._select_voice(params)
            
            # Generate audio
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2",
                voice_settings={
                    "stability": self.config.elevenlabs_stability,
                    "similarity_boost": self.config.elevenlabs_similarity
                }
            )
            
            # Save audio
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(audio)
            
            logger.info(f"Saved audio to: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "engine": "elevenlabs",
                "voice_id": voice_id,
                "parameters": params.dict(),
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _select_voice(self, params: VoiceParameters) -> str:
        """
        Select appropriate ElevenLabs voice based on parameters
        """
        if self.config.elevenlabs_voice_id:
            return self.config.elevenlabs_voice_id
        
        # Default voices based on warmth and gender
        # (These are example voice IDs - replace with actual ones)
        if params.warmth >= 0.7:
            return "21m00Tcm4TlvDq8ikWAM"  # Rachel (warm, friendly)
        else:
            return "EXAVITQu4vr4xnSDxMaL"  # Bella (neutral)


class CoquiTTSEngine:
    """
    Coqui TTS (Local, Open Source)
    
    Pros:
    - Free, open source
    - Runs locally (privacy)
    - Highly customizable
    - Multiple models available
    
    Cons:
    - Requires setup
    - GPU recommended
    - Quality varies by model
    """
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.mapper = VoiceParameterMapper()
        self.tts_model = None
    
    def synthesize(
        self,
        text: str,
        voice_score: VoiceScore,
        output_path: Path
    ) -> Dict:
        """
        Synthesize speech using Coqui TTS
        """
        try:
            from TTS.api import TTS
        except ImportError:
            logger.error("TTS not installed. Install with: pip install TTS")
            return {"error": "Coqui TTS not installed"}
        
        logger.info(f"Synthesizing with Coqui TTS: {len(text)} chars")
        
        # Map voice parameters
        params = self.mapper.map_voice_score(voice_score)
        
        try:
            # Initialize model (cache it)
            if self.tts_model is None:
                self.tts_model = TTS(self.config.coqui_model)
            
            # Generate audio
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.tts_model.tts_to_file(
                text=text,
                file_path=str(output_path),
                speaker=self.config.coqui_speaker
            )
            
            logger.info(f"Saved audio to: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "engine": "coqui",
                "model": self.config.coqui_model,
                "parameters": params.dict(),
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}", exc_info=True)
            return {"error": str(e)}


# =============================================================================
# MAIN SYNTHESIZER
# =============================================================================

class VoiceSynthesizer:
    """
    Main voice synthesis coordinator
    Supports multiple TTS engines
    """
    
    def __init__(self, config: TTSConfig = TTSConfig()):
        self.config = config
        self.mapper = VoiceParameterMapper()
        
        # Initialize engine
        if config.engine == "gtts":
            self.engine = GoogleTTSEngine(config)
        elif config.engine == "elevenlabs":
            self.engine = ElevenLabsEngine(config)
        elif config.engine == "coqui":
            self.engine = CoquiTTSEngine(config)
        else:
            raise ValueError(f"Unknown TTS engine: {config.engine}")
    
    def synthesize_voice(
        self,
        text: str,
        voice_score: VoiceScore,
        output_filename: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Synthesize voice from text and VoiceScore
        
        Args:
            text: Text to speak
            voice_score: Voice characteristics from kamma
            output_filename: Optional custom filename
            use_cache: Use cached audio if available
            
        Returns:
            Dict with success status, file path, and metadata
        """
        logger.info(f"Synthesizing voice for text: '{text[:50]}...'")
        
        # Generate output filename
        if output_filename is None:
            # Hash text + voice params for caching
            cache_key = self._generate_cache_key(text, voice_score)
            output_filename = f"voice_{cache_key}.{self.config.output_format}"
        
        output_path = Path(self.config.cache_dir) / output_filename
        
        # Check cache
        if use_cache and self.config.cache_audio and output_path.exists():
            logger.info(f"Using cached audio: {output_path}")
            return {
                "success": True,
                "output_path": str(output_path),
                "cached": True,
                "engine": self.config.engine
            }
        
        # Synthesize
        result = self.engine.synthesize(text, voice_score, output_path)
        
        if result.get("success"):
            result["cached"] = False
        
        return result
    
    def get_voice_parameters(self, voice_score: VoiceScore) -> VoiceParameters:
        """
        Get voice parameters without synthesizing
        Useful for testing and debugging
        """
        return self.mapper.map_voice_score(voice_score)
    
    def _generate_cache_key(self, text: str, voice_score: VoiceScore) -> str:
        """Generate cache key from text and voice characteristics"""
        # Combine text and key voice metrics
        key_data = f"{text}_{voice_score.voice_quality}_{voice_score.vocal_warmth}_{voice_score.speech_clarity}"
        
        # Hash it
        return hashlib.md5(key_data.encode()).hexdigest()[:12]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def synthesize_character_voice(
    text: str,
    voice_score: VoiceScore,
    engine: str = "gtts",
    output_path: Optional[str] = None
) -> Dict:
    """
    Convenience function to synthesize character voice
    
    Example:
        >>> voice_score = VoiceScore(
        ...     voice_quality=85,
        ...     vocal_warmth=90,
        ...     speech_clarity=88
        ... )
        >>> result = synthesize_character_voice(
        ...     "สวัสดีครับ ผมชื่อพีช",
        ...     voice_score,
        ...     engine="gtts"
        ... )
        >>> if result["success"]:
        ...     print(f"Audio saved: {result['output_path']}")
    """
    config = TTSConfig(engine=engine)
    synthesizer = VoiceSynthesizer(config)
    
    return synthesizer.synthesize_voice(
        text=text,
        voice_score=voice_score,
        output_filename=output_path
    )


def get_voice_description(voice_score: VoiceScore) -> str:
    """
    Get human-readable voice description
    
    Example:
        >>> desc = get_voice_description(voice_score)
        >>> print(desc)
        "Warm, gentle voice with excellent clarity. High mettā influence creates compassionate tone."
    """
    mapper = VoiceParameterMapper()
    params = mapper.map_voice_score(voice_score)
    
    parts = []
    
    # Emotional tone
    parts.append(params.emotional_tone.capitalize())
    
    # Clarity
    if params.clarity >= 0.8:
        parts.append("with excellent clarity")
    elif params.clarity >= 0.6:
        parts.append("with good clarity")
    else:
        parts.append("with moderate clarity")
    
    # Mettā influence
    if params.metta_influence >= 0.8:
        parts.append("High mettā influence creates compassionate tone")
    
    # Truthfulness
    if params.truthfulness_marker >= 0.8:
        parts.append("Honest and trustworthy quality")
    
    return ". ".join(parts) + "."
