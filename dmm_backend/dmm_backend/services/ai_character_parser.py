"""
AI Character Parser Service

Parses Thai language character descriptions from Peace Script Step 3
into structured InternalCharacter and ExternalCharacter data using Ollama LLM.

This service enables automatic transformation of simple 12-field Characters
into comprehensive 100+ field ActorProfiles with psychological depth.

Features:
    - Parse personality text → InternalCharacter (40+ fields)
    - Parse appearance text → ExternalCharacter (35+ fields)
    - Support for Thai language prompts
    - Fallback to sensible defaults if parsing fails
    - Production-ready with error handling

Installation Requirements:
    1. brew install ollama  (macOS)
    2. ollama serve
    3. ollama pull llama3.2:3b

Usage:
    from services.ai_character_parser import ai_parser
    
    # Parse personality
    internal = await ai_parser.parse_personality_to_internal(
        "เข้มแข็ง มุ่งมั่น แต่มีบาดแผลในใจ"
    )
    
    # Parse appearance
    external = await ai_parser.parse_appearance_to_external(
        "ผู้หญิงสูง ผมยาวดำ ดวงตาคม",
        gender="female",
        age=28
    )

Author: Peace Script Team
Date: 10 November 2568
Version: 1.0.0
"""

from typing import Optional
import json
import asyncio

from core.llm_service import get_ollama_service
from core.logging_config import get_logger
from documents_actors import InternalCharacter, ExternalCharacter

logger = get_logger(__name__)


class AICharacterParser:
    """AI-powered parser for Character → Actor transformation
    
    Uses Ollama LLM (llama3.2:3b) to parse Thai text descriptions
    into structured psychological and physical character data.
    
    Attributes:
        ollama: OllamaService instance
        model: LLM model name (default: llama3.2:3b)
        
    Methods:
        parse_personality_to_internal(): Parse personality → InternalCharacter
        parse_appearance_to_external(): Parse appearance → ExternalCharacter
        summarize_internal_character(): InternalCharacter → Thai summary
        summarize_external_character(): ExternalCharacter → Thai summary
    """
    
    def __init__(self):
        """Initialize AI Character Parser"""
        self.ollama = get_ollama_service()
        self.model = "qwen2.5:7b"  # Best for Thai language (upgraded from llama3.2:3b)
        logger.info("AICharacterParser initialized")
    
    async def parse_personality_to_internal(
        self,
        personality_text: str,
        motivation_text: Optional[str] = None,
        conflict_text: Optional[str] = None
    ) -> InternalCharacter:
        """
        Parse Thai personality description into InternalCharacter structure
        
        This method uses AI to transform free-form Thai text into a structured
        psychological profile with 40+ fields including Big Five traits,
        Thai cultural values, motivations, and emotional states.
        
        Args:
            personality_text: Thai text describing personality (required, min 5 chars)
            motivation_text: Optional motivation/goal description
            conflict_text: Optional internal conflict description
            
        Returns:
            InternalCharacter object with AI-parsed data
            Falls back to defaults if parsing fails
            
        Example:
            >>> parser = AICharacterParser()
            >>> result = await parser.parse_personality_to_internal(
            ...     personality_text="เข้มแข็ง มุ่งมั่น รับผิดชอบ แต่มีบาดแผลในใจ กลัวการสูญเสีย",
            ...     motivation_text="ต้องการปกป้องครอบครัว",
            ...     conflict_text="ติดอยู่ระหว่างหน้าที่กับความรัก"
            ... )
            >>> result.conscientiousness
            8.5
            >>> result.neuroticism
            7.0
            >>> result.fears
            ['loss', 'abandonment']
        """
        # Validate input
        if not personality_text or len(personality_text.strip()) < 5:
            logger.warning("Personality text too short, using defaults")
            return self._create_default_internal()
        
        logger.info(f"Parsing personality: '{personality_text[:50]}...'")
        
        # Build AI prompt
        prompt = self._build_personality_prompt(
            personality_text,
            motivation_text,
            conflict_text
        )
        
        # Call Ollama (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.ollama.generate(
                prompt=prompt,
                model=self.model,
                temperature=0.3,  # Low temperature for consistency
                max_tokens=800
            )
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (may have extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Map to InternalCharacter
            internal = InternalCharacter(
                # Big Five
                openness=float(data.get("big_five", {}).get("openness", 5.0)),
                conscientiousness=float(data.get("big_five", {}).get("conscientiousness", 5.0)),
                extraversion=float(data.get("big_five", {}).get("extraversion", 5.0)),
                agreeableness=float(data.get("big_five", {}).get("agreeableness", 5.0)),
                neuroticism=float(data.get("big_five", {}).get("neuroticism", 5.0)),
                
                # Thai Values
                kreng_jai=float(data.get("thai_values", {}).get("kreng_jai", 5.0)),
                bunkhun=float(data.get("thai_values", {}).get("bunkhun", 5.0)),
                nam_jai=float(data.get("thai_values", {}).get("nam_jai", 5.0)),
                
                # Motivations
                primary_motivation=data.get("motivations", {}).get("primary_motivation"),
                core_values=data.get("motivations", {}).get("core_values", []),
                fears=data.get("motivations", {}).get("fears", []),
                desires=data.get("motivations", {}).get("desires", []),
                
                # Moral
                moral_alignment=data.get("moral", {}).get("moral_alignment"),
                ethical_compass=float(data.get("moral", {}).get("ethical_compass", 5.0)),
                
                # Emotional
                default_mood=data.get("emotional", {}).get("default_mood"),
                emotional_stability=float(data.get("emotional", {}).get("emotional_stability", 5.0)),
                stress_response=data.get("emotional", {}).get("stress_response"),
                
                # Intellectual
                intelligence_type=data.get("intellectual", {}).get("intelligence_type"),
                wisdom_level=float(data.get("intellectual", {}).get("wisdom_level", 5.0)),
                decision_making_style=data.get("intellectual", {}).get("decision_making_style"),
                
                # Social
                communication_style=data.get("social", {}).get("communication_style"),
                conflict_resolution=data.get("social", {}).get("conflict_resolution"),
                trust_level=float(data.get("social", {}).get("trust_level", 5.0)),
                
                # Growth
                adaptability=float(data.get("growth", {}).get("adaptability", 5.0)),
                learning_capacity=float(data.get("growth", {}).get("learning_capacity", 5.0)),
                trauma_influence=data.get("growth", {}).get("trauma_influence"),
                redemption_potential=float(data.get("growth", {}).get("redemption_potential", 5.0))
            )
            
            logger.info("Successfully parsed personality into InternalCharacter")
            return internal
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"AI Response: {response[:200]}")
            # Fallback to defaults
            return self._create_default_internal()
    
    async def parse_appearance_to_external(
        self,
        appearance_text: str,
        gender: Optional[str] = None,
        age: Optional[int] = None
    ) -> ExternalCharacter:
        """
        Parse Thai appearance description into ExternalCharacter structure
        
        Transforms free-form Thai text about physical appearance into
        a structured profile with 35+ fields including physical traits,
        facial features, style, and presence.
        
        Args:
            appearance_text: Thai text describing appearance
            gender: Optional gender hint (male/female/non-binary)
            age: Optional age hint (1-120)
            
        Returns:
            ExternalCharacter object with AI-parsed data
            
        Example:
            >>> external = await parser.parse_appearance_to_external(
            ...     appearance_text="ผู้หญิงสูง ผมยาวดำ ดวงตาคม มีรอยแผลที่แขน",
            ...     gender="female",
            ...     age=28
            ... )
            >>> external.gender
            'female'
            >>> external.hair_color
            'black'
            >>> 'scar' in str(external.distinctive_features)
            True
        """
        # Validate input
        if not appearance_text or len(appearance_text.strip()) < 5:
            logger.warning("Appearance text too short, using defaults")
            return self._create_default_external(gender, age)
        
        logger.info(f"Parsing appearance: '{appearance_text[:50]}...'")
        
        # Build AI prompt
        prompt = self._build_appearance_prompt(
            appearance_text,
            gender,
            age
        )
        
        # Call Ollama (async)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.ollama.generate(
                prompt=prompt,
                model=self.model,
                temperature=0.3,
                max_tokens=800
            )
        )
        
        # Parse JSON response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Map to ExternalCharacter
            external = ExternalCharacter(
                # Physical
                age=int(data.get("physical", {}).get("age", age or 30)),
                gender=data.get("physical", {}).get("gender", gender or "unknown"),
                height=float(data.get("physical", {}).get("height", 170.0)),
                weight=float(data.get("physical", {}).get("weight", 65.0)),
                body_type=data.get("physical", {}).get("body_type", "average"),
                
                # Facial
                face_shape=data.get("facial", {}).get("face_shape", "oval"),
                eye_color=data.get("facial", {}).get("eye_color", "brown"),
                hair_color=data.get("facial", {}).get("hair_color", "black"),
                hair_style=data.get("facial", {}).get("hair_style", "short"),
                skin_tone=data.get("facial", {}).get("skin_tone", "medium"),
                distinctive_features=data.get("facial", {}).get("distinctive_features", []),
                eye_expression=data.get("facial", {}).get("eye_expression", "neutral"),
                smile_type=data.get("facial", {}).get("smile_type", "normal"),
                
                # Style
                fashion_style=data.get("style", {}).get("fashion_style", "casual"),
                color_palette=data.get("style", {}).get("color_palette", ["black", "white"]),
                accessories=data.get("style", {}).get("accessories", []),
                default_clothing_style=data.get("style", {}).get("default_clothing_style", "casual"),
                current_outfit_description=data.get("style", {}).get("current_outfit_description", "Standard casual outfit"),
                wardrobe_size=data.get("style", {}).get("wardrobe_size", "moderate"),
                
                # Condition
                fitness_level=float(data.get("condition", {}).get("fitness_level", 5.0)),
                health_status=data.get("condition", {}).get("health_status", "good"),
                
                # Movement
                posture=data.get("movement", {}).get("posture", "upright"),
                gait=data.get("movement", {}).get("gait", "normal"),
                gestures=data.get("movement", {}).get("gestures", []),
                
                # Voice
                voice_tone=data.get("voice", {}).get("voice_tone", "medium"),
                speech_pattern=data.get("voice", {}).get("speech_pattern", "normal"),
                accent=data.get("voice", {}).get("accent", "standard"),
                catchphrase=data.get("voice", {}).get("catchphrase", ""),
                
                # Quirks
                nervous_habits=data.get("quirks", {}).get("nervous_habits", []),
                signature_gesture=data.get("quirks", {}).get("signature_gesture", ""),
                quirks=data.get("quirks", {}).get("quirks", []),
                
                # Presence
                first_impression=data.get("presence", {}).get("first_impression", "ordinary"),
                charisma_level=float(data.get("presence", {}).get("charisma_level", 5.0)),
                approachability=float(data.get("presence", {}).get("approachability", 5.0)),
                
                # Skills (empty by default, can be enhanced later)
                combat_skills=[],
                artistic_skills=[],
                practical_skills=[],
                supernatural_abilities=[],
                
                # Additional details
                voice_characteristics=data.get("voice", {}).get("characteristics", [])
            )
            
            logger.info("Successfully parsed appearance into ExternalCharacter")
            return external
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"AI Response: {response[:200]}")
            return self._create_default_external(gender, age)
    
    def _build_personality_prompt(
        self,
        personality: str,
        motivation: Optional[str],
        conflict: Optional[str]
    ) -> str:
        """Build AI prompt for personality parsing
        
        Creates a structured prompt that instructs the LLM to analyze
        Thai personality text and output JSON matching InternalCharacter schema.
        """
        return f"""คุณเป็น AI ที่เชี่ยวชาญการวิเคราะห์บุคลิกภาพตัวละครในบทภาพยนตร์ วิเคราะห์คำอธิบายต่อไปนี้และแปลงเป็นข้อมูลโครงสร้าง JSON:

บุคลิกภาพ: "{personality}"
{f'แรงจูงใจ: "{motivation}"' if motivation else ''}
{f'ความขัดแย้ง: "{conflict}"' if conflict else ''}

วิเคราะห์และส่งออกเป็น JSON เท่านั้น (ไม่ต้องอธิบายเพิ่มเติม):

{{
    "big_five": {{
        "openness": 0-10,
        "conscientiousness": 0-10,
        "extraversion": 0-10,
        "agreeableness": 0-10,
        "neuroticism": 0-10
    }},
    "thai_values": {{
        "kreng_jai": 0-10,
        "bunkhun": 0-10,
        "nam_jai": 0-10
    }},
    "motivations": {{
        "primary_motivation": "...",
        "core_values": ["...", "..."],
        "fears": ["...", "..."],
        "desires": ["...", "..."]
    }},
    "moral": {{
        "moral_alignment": "lawful good | neutral | chaotic evil",
        "ethical_compass": 0-10
    }},
    "emotional": {{
        "default_mood": "optimistic | melancholic | angry | calm",
        "emotional_stability": 0-10,
        "stress_response": "fight | flight | freeze | fawn"
    }},
    "intellectual": {{
        "intelligence_type": "analytical | creative | practical | emotional",
        "wisdom_level": 0-10,
        "decision_making_style": "impulsive | calculated | intuitive"
    }},
    "social": {{
        "communication_style": "direct | indirect | passive | assertive",
        "conflict_resolution": "avoidance | confrontation | compromise",
        "trust_level": 0-10
    }},
    "growth": {{
        "adaptability": 0-10,
        "learning_capacity": 0-10,
        "trauma_influence": "...",
        "redemption_potential": 0-10
    }}
}}

คำแนะนำ:
- ค่าตัวเลข 0-10 (5=ปานกลาง, >7=สูง, <3=ต่ำ)
- ถ้าบุคลิก "เข้มแข็ง" → conscientiousness สูง, neuroticism ต่ำ
- ถ้า "บาดแผล" → neuroticism สูง, trauma_influence มีค่า
- ถ้า "รักครอบครัว" → bunkhun สูง
- ให้ค่าที่สมเหตุสมผลตามบริบท"""
    
    def _build_appearance_prompt(
        self,
        appearance: str,
        gender: Optional[str],
        age: Optional[int]
    ) -> str:
        """Build AI prompt for appearance parsing"""
        return f"""วิเคราะห์ลักษณะภายนอกของตัวละครจากคำอธิบายภาษาไทย:

ลักษณะภายนอก: "{appearance}"
{f'เพศ: "{gender}"' if gender else ''}
{f'อายุ: {age} ปี' if age else ''}

ส่งออกเป็น JSON เท่านั้น (ไม่ต้องอธิบาย):

{{
    "physical": {{
        "age": {age or '...'},
        "gender": "{gender or '...'}",
        "height": ...,
        "weight": ...,
        "body_type": "slim | athletic | average | muscular | heavy"
    }},
    "facial": {{
        "face_shape": "oval | round | square | heart | long",
        "eye_color": "...",
        "hair_color": "...",
        "hair_style": "...",
        "skin_tone": "fair | medium | tan | dark",
        "distinctive_features": ["...", "..."],
        "eye_expression": "sharp | gentle | cold | warm | neutral",
        "smile_type": "bright | subtle | rare | mischievous | normal"
    }},
    "style": {{
        "fashion_style": "casual | professional | elegant | sporty | bohemian",
        "color_palette": ["...", "..."],
        "accessories": ["...", "..."]
    }},
    "condition": {{
        "fitness_level": 0-10,
        "health_status": "excellent | good | average | poor"
    }},
    "movement": {{
        "posture": "upright | slouched | rigid | relaxed",
        "gait": "confident | cautious | graceful | clumsy | normal",
        "gestures": ["...", "..."]
    }},
    "voice": {{
        "voice_tone": "deep | high | raspy | smooth | medium",
        "speech_pattern": "fast | slow | stuttering | eloquent | normal",
        "accent": "standard | regional | foreign",
        "catchphrase": "...",
        "characteristics": ["...", "..."]
    }},
    "quirks": {{
        "nervous_habits": ["...", "..."],
        "signature_gesture": "...",
        "quirks": ["...", "..."]
    }},
    "presence": {{
        "first_impression": "intimidating | friendly | mysterious | ordinary",
        "charisma_level": 0-10,
        "approachability": 0-10
    }}
}}

คำแนะนำ:
- ถ้าเป็นผู้หญิงสูง → height ≥ 165
- ถ้าเป็นผู้ชายสูง → height ≥ 175
- ถ้า "ดวงตาคม" → eye_expression = "sharp"
- ถ้า "มีรอยแผล" → distinctive_features มีค่า
- ให้รายละเอียดตามที่มีในคำอธิบาย"""
    
    def _create_default_internal(self) -> InternalCharacter:
        """Create default InternalCharacter if parsing fails
        
        Returns neutral/average values for all fields.
        This ensures the system never crashes due to parsing failures.
        """
        logger.info("Creating default InternalCharacter")
        return InternalCharacter(
            # Big Five (all average)
            openness=5.0,
            conscientiousness=5.0,
            extraversion=5.0,
            agreeableness=5.0,
            neuroticism=5.0,
            
            # Thai Values (all average)
            kreng_jai=5.0,
            bunkhun=5.0,
            nam_jai=5.0,
            
            # Motivations
            primary_motivation="Unknown",
            core_values=[],
            fears=[],
            desires=[],
            
            # Moral
            moral_alignment="neutral",
            ethical_compass=5.0,
            
            # Emotional
            default_mood="neutral",
            emotional_stability=5.0,
            stress_response="unknown",
            
            # Intellectual
            intelligence_type="average",
            wisdom_level=5.0,
            decision_making_style="calculated",
            
            # Social
            communication_style="direct",
            conflict_resolution="compromise",
            trust_level=5.0,
            
            # Growth
            adaptability=5.0,
            learning_capacity=5.0,
            trauma_influence="",
            redemption_potential=5.0
        )
    
    def _create_default_external(
        self,
        gender: Optional[str],
        age: Optional[int]
    ) -> ExternalCharacter:
        """Create default ExternalCharacter if parsing fails
        
        Uses provided gender/age hints if available,
        otherwise uses neutral defaults.
        """
        logger.info(f"Creating default ExternalCharacter (gender={gender}, age={age})")
        return ExternalCharacter(
            # Physical
            age=age or 30,
            gender=gender or "unknown",
            height=170.0,
            weight=65.0,
            body_type="average",
            
            # Facial
            face_shape="oval",
            eye_color="brown",
            hair_color="black",
            hair_style="short",
            skin_tone="medium",
            distinctive_features=[],
            eye_expression="neutral",
            smile_type="normal",
            
            # Style
            fashion_style="casual",
            color_palette=["black", "white"],
            accessories=[],
            default_clothing_style="casual",
            current_outfit_description="Standard casual outfit",
            wardrobe_size="moderate",
            
            # Condition
            fitness_level=5.0,
            health_status="good",
            
            # Movement
            posture="upright",
            gait="normal",
            gestures=[],
            
            # Voice
            voice_tone="medium",
            speech_pattern="normal",
            accent="standard",
            catchphrase="",
            voice_characteristics=[],
            
            # Quirks
            nervous_habits=[],
            signature_gesture="",
            quirks=[],
            
            # Presence
            first_impression="ordinary",
            charisma_level=5.0,
            approachability=5.0,
            
            # Skills (empty, can be enhanced later)
            combat_skills=[],
            artistic_skills=[],
            practical_skills=[],
            supernatural_abilities=[]
        )


# ============================================================================
# Singleton Instance
# ============================================================================

_ai_parser: Optional[AICharacterParser] = None

def get_ai_parser() -> AICharacterParser:
    """Get or create AICharacterParser singleton instance
    
    Returns:
        AICharacterParser instance
        
    Example:
        from services.ai_character_parser import get_ai_parser
        
        parser = get_ai_parser()
        internal = await parser.parse_personality_to_internal("...")
    """
    global _ai_parser
    if _ai_parser is None:
        _ai_parser = AICharacterParser()
        logger.info("AICharacterParser singleton created")
    return _ai_parser


# Global instance for convenience
ai_parser = AICharacterParser()
