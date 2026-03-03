"""
Rebirth Template Generator
===========================
Generate character template for next incarnation.

This is a HELPER TOOL for cross-lifetime storytelling.
NOT an automatic rebirth system.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RebirthTemplate(BaseModel):
    """
    Template for creating next incarnation of a character
    
    ✅ Auto-filled: Kamma ledger, core traits (inherited)
    ❌ Manual fill: Name, age, appearance, realm (Creator decides)
    ⚠️ Optional: Past life memories, karmic debt
    """
    
    # ========================================
    # METADATA
    # ========================================
    template_id: str = Field(default="", description="Template unique ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    # ========================================
    # CONNECTION TO PREVIOUS LIFE
    # ========================================
    previous_life_id: str = Field(..., description="Previous character ID")
    previous_life_name: str = Field(..., description="Previous character name")
    previous_life_realm: str = Field(..., description="Previous realm")
    
    # ========================================
    # ✅ AUTO-INHERITED (from previous life)
    # ========================================
    inherited_kamma: Dict = Field(default_factory=dict, description="Complete kamma ledger from previous life")
    inherited_kamma_score: float = Field(default=0.0, description="Total kamma score calculated")
    inherited_core_traits: List[str] = Field(default_factory=list, description="Core personality traits that carry over")
    inherited_talents: List[str] = Field(default_factory=list, description="Natural talents from past life")
    inherited_weaknesses: List[str] = Field(default_factory=list, description="Weaknesses from past life")
    
    # Suggested realm based on kamma (Advisory only)
    suggested_realm_id: int = Field(default=6, description="Suggested realm ID based on kamma")
    suggested_realm_name: str = Field(default="มนุษย์", description="Suggested realm name")
    suggestion_confidence: float = Field(default=0.0, description="Confidence level 0-100%")
    
    # ========================================
    # ❌ MANUAL FILL (Creator must provide)
    # ========================================
    new_name: str = Field(default="[ใส่ชื่อตัวละครชาติใหม่]", description="New character name")
    new_age: int = Field(default=0, description="New character age")
    new_gender: str = Field(default="[เลือก Male/Female/Other]", description="New character gender")
    
    # Birth realm (Creator chooses, can override suggestion)
    birth_realm_id: int = Field(default=6, description="Actual birth realm (Creator's choice)")
    birth_realm_name: str = Field(default="มนุษย์", description="Actual birth realm name")
    override_suggestion: bool = Field(default=False, description="True if Creator overrode suggestion")
    
    # Appearance (Creator must design)
    new_appearance: Dict = Field(
        default_factory=lambda: {
            "placeholder": True,
            "note": "Creator must design appearance using Character Creation tools"
        },
        description="New appearance (to be designed)"
    )
    
    # ========================================
    # ⚠️ OPTIONAL FEATURES
    # ========================================
    past_life_memories_enabled: bool = Field(default=False, description="Does character remember past life?")
    memory_fragments: List[Dict] = Field(
        default_factory=list,
        description="Specific memory fragments (if enabled)"
    )
    
    karmic_debt_carried: float = Field(default=0.0, description="Unresolved kamma from past life (0-100)")
    karmic_connections: List[Dict] = Field(
        default_factory=list,
        description="Karmic connections to other characters"
    )
    
    # Story-specific fields
    story_context: str = Field(default="", description="Why this rebirth? (story context)")
    narrative_purpose: str = Field(default="", description="Purpose of this incarnation in story")
    
    # Educational mode (for documentary/teaching)
    educational_mode: bool = Field(default=False, description="Is this for educational purposes?")
    educational_lesson: str = Field(default="", description="What Buddhist lesson does this demonstrate?")


class RebirthTemplateGenerator:
    """
    Generate templates for next incarnation
    
    This is a HELPER - Creator still has full control
    """
    
    def __init__(self):
        from .calculator import RebirthCalculator
        self.calculator = RebirthCalculator()
    
    def create_template(
        self,
        previous_character: Dict,
        options: Optional[Dict] = None
    ) -> RebirthTemplate:
        """
        Create rebirth template from previous character
        
        Args:
            previous_character: Previous character data (from database)
            options: Optional settings {
                "enable_memories": bool,
                "karmic_debt": float,
                "educational_mode": bool
            }
        
        Returns:
            RebirthTemplate with auto-filled and placeholder fields
        """
        options = options or {}
        
        # Extract previous life data
        prev_id = previous_character.get("id", "unknown")
        prev_name = previous_character.get("name", "Unknown")
        prev_realm = previous_character.get("current_bhumi", "Human Realm")
        
        # Extract kamma ledger
        kamma_ledger = previous_character.get("kamma_ledger", {})
        
        # Calculate kamma score and suggestions
        kamma_result = self.calculator.calculate_kamma_score(kamma_ledger)
        realm_suggestions = self.calculator.suggest_rebirth_realms(kamma_ledger, top_n=1)
        
        # Get top suggestion
        if realm_suggestions:
            top_suggestion = realm_suggestions[0]
            suggested_realm_id = top_suggestion["realm_id"]
            suggested_realm_name = top_suggestion["realm_name_th"]
            suggestion_confidence = top_suggestion["probability"]
        else:
            # Default to human realm
            suggested_realm_id = 6
            suggested_realm_name = "มนุษย์"
            suggestion_confidence = 50.0
        
        # Extract core traits
        core_traits = self._extract_core_traits(previous_character)
        talents = self._extract_talents(previous_character)
        weaknesses = self._extract_weaknesses(previous_character)
        
        # Create template
        template = RebirthTemplate(
            template_id=f"rebirth_template_{prev_id}_{datetime.now().timestamp()}",
            
            # Previous life connection
            previous_life_id=prev_id,
            previous_life_name=prev_name,
            previous_life_realm=prev_realm,
            
            # Auto-inherited
            inherited_kamma=kamma_ledger,
            inherited_kamma_score=kamma_result["total_score"],
            inherited_core_traits=core_traits,
            inherited_talents=talents,
            inherited_weaknesses=weaknesses,
            
            # Suggested realm
            suggested_realm_id=suggested_realm_id,
            suggested_realm_name=suggested_realm_name,
            suggestion_confidence=suggestion_confidence,
            
            # Optional features
            past_life_memories_enabled=options.get("enable_memories", False),
            karmic_debt_carried=options.get("karmic_debt", 0.0),
            educational_mode=options.get("educational_mode", False),
        )
        
        return template
    
    def apply_template_to_new_character(
        self,
        template: RebirthTemplate,
        new_character_data: Dict
    ) -> Dict:
        """
        Apply template to new character creation
        
        This merges inherited traits with new character data
        """
        # Start with new character data
        merged = new_character_data.copy()
        
        # Add inherited kamma
        merged["kamma_ledger"] = template.inherited_kamma
        merged["kamma_score"] = template.inherited_kamma_score
        
        # Add metadata
        merged["rebirth_metadata"] = {
            "is_reincarnation": True,
            "previous_life_id": template.previous_life_id,
            "previous_life_name": template.previous_life_name,
            "inherited_traits": template.inherited_core_traits,
            "karmic_debt": template.karmic_debt_carried,
        }
        
        # Add past life memories if enabled
        if template.past_life_memories_enabled:
            merged["past_life_memories"] = template.memory_fragments
        
        # Add realm
        merged["birth_bhumi"] = template.birth_realm_name
        merged["current_bhumi"] = template.birth_realm_name
        
        return merged
    
    def create_karmic_connection(
        self,
        character_a_id: str,
        character_b_id: str,
        connection_type: str,
        description: str
    ) -> Dict:
        """
        Create karmic connection between two characters
        
        Useful for:
        - Reincarnated lovers
        - Past life enemies
        - Family karma
        """
        return {
            "character_a_id": character_a_id,
            "character_b_id": character_b_id,
            "connection_type": connection_type,  # "love", "hatred", "debt", "family"
            "description": description,
            "strength": 1.0,  # 0-1 scale
            "created_at": datetime.now().isoformat()
        }
    
    def create_memory_fragment(
        self,
        memory_description: str,
        trigger_condition: str,
        emotional_intensity: float = 0.5
    ) -> Dict:
        """
        Create past life memory fragment
        
        For flashback scenes in movies
        """
        return {
            "description": memory_description,
            "trigger": trigger_condition,
            "intensity": emotional_intensity,
            "type": "past_life_memory",
            "created_at": datetime.now().isoformat()
        }
    
    # ========================================
    # PRIVATE HELPER METHODS
    # ========================================
    
    def _extract_core_traits(self, character: Dict) -> List[str]:
        """
        Extract core personality traits that carry over to next life
        
        Based on Buddhist psychology: Habitual mental patterns (cetasika)
        """
        traits = []
        
        # From personality field
        personality = character.get("personality", {})
        if isinstance(personality, dict):
            # Extract dominant traits
            for trait, value in personality.items():
                if isinstance(value, (int, float)) and value > 70:
                    traits.append(trait)
        
        # From kamma patterns
        kamma_ledger = character.get("kamma_ledger", {})
        
        # Generosity pattern
        if kamma_ledger.get("dana", {}).get("count", 0) > 10:
            traits.append("generous")
        
        # Compassion pattern
        if kamma_ledger.get("metta", {}).get("count", 0) > 10:
            traits.append("compassionate")
        
        # Greed pattern
        if kamma_ledger.get("lobha_actions", {}).get("count", 0) > 10:
            traits.append("greedy")
        
        # Anger pattern
        if kamma_ledger.get("dosa_actions", {}).get("count", 0) > 10:
            traits.append("quick_tempered")
        
        # Default traits if none found
        if not traits:
            traits = ["neutral", "balanced"]
        
        return traits
    
    def _extract_talents(self, character: Dict) -> List[str]:
        """
        Extract natural talents/skills that carry over
        
        Based on: Previous life training creates "vasana" (mental impressions)
        """
        talents = []
        
        # From skills field
        skills = character.get("skills", [])
        if isinstance(skills, list):
            # Skills with high proficiency carry over
            for skill in skills:
                if isinstance(skill, dict):
                    if skill.get("proficiency", 0) > 80:
                        talents.append(skill.get("name", "unknown"))
        
        # From meditation practice
        kamma_ledger = character.get("kamma_ledger", {})
        meditation_count = kamma_ledger.get("meditation", {}).get("count", 0)
        if meditation_count > 20:
            talents.append("meditation_aptitude")
        
        return talents
    
    def _extract_weaknesses(self, character: Dict) -> List[str]:
        """
        Extract weaknesses/defilements that carry over
        
        Based on: Unresolved kilesa (defilements) continue across lives
        """
        weaknesses = []
        
        kamma_ledger = character.get("kamma_ledger", {})
        
        # Strong greed
        if kamma_ledger.get("lobha_actions", {}).get("count", 0) > 15:
            weaknesses.append("greed")
        
        # Strong hatred
        if kamma_ledger.get("dosa_actions", {}).get("count", 0) > 15:
            weaknesses.append("hatred")
        
        # Strong delusion
        if kamma_ledger.get("moha_actions", {}).get("count", 0) > 15:
            weaknesses.append("delusion")
        
        # Lying tendency
        if kamma_ledger.get("musavada", {}).get("count", 0) > 10:
            weaknesses.append("dishonesty")
        
        return weaknesses


# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

def quick_create_template(
    previous_character: Dict,
    enable_memories: bool = False
) -> RebirthTemplate:
    """
    Quick template creation for API endpoints
    """
    generator = RebirthTemplateGenerator()
    
    options = {
        "enable_memories": enable_memories,
        "karmic_debt": 0.0,
        "educational_mode": False
    }
    
    return generator.create_template(previous_character, options)


def create_flashback_characters(
    current_character: Dict,
    num_past_lives: int = 1
) -> List[RebirthTemplate]:
    """
    Create multiple past life templates for flashback scenes
    
    Useful for movies with multiple past life flashbacks
    """
    generator = RebirthTemplateGenerator()
    templates = []
    
    for i in range(num_past_lives):
        template = generator.create_template(
            current_character,
            options={
                "enable_memories": True,
                "karmic_debt": 10.0 * (i + 1),
                "educational_mode": False
            }
        )
        templates.append(template)
    
    return templates
