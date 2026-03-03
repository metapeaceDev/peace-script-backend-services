"""
🔒 Buddhist Logic Validators for Core Profile System
Digital Mind Model v1.4

This module provides validation functions for Buddhist spiritual progression rules
to ensure data integrity and realistic character development.

Functions:
- validate_fetter_progression: Ensure fetters broken in correct order
- validate_character_status_transition: Check if character status change is valid
- validate_parami_for_attainment: Verify pāramī levels support spiritual stage
- validate_age_spiritual_development: Warn if age inconsistent with attainment
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel


# ============================================================================
# BUDDHIST REFERENCE DATA
# ============================================================================

# 10 Fetters (Saṃyojana) in order of removal
FETTER_ORDER = [
    "sakkaya_ditthi",      # 1. Identity view (removed at Stream Entry)
    "vicikiccha",          # 2. Doubt (removed at Stream Entry)
    "silabbata_paramasa",  # 3. Attachment to rites & rituals (removed at Stream Entry)
    "kama_raga",           # 4. Sensual desire (weakened at Once-Returner, removed at Non-Returner)
    "vyapada",             # 5. Ill-will (weakened at Once-Returner, removed at Non-Returner)
    "rupa_raga",           # 6. Attachment to form realm (removed at Arahant)
    "arupa_raga",          # 7. Attachment to formless realm (removed at Arahant)
    "mana",                # 8. Conceit (removed at Arahant)
    "uddhacca",            # 9. Restlessness (removed at Arahant)
    "avijja"               # 10. Ignorance (removed at Arahant)
]

# Path stages with required fetters broken
PATH_STAGE_REQUIREMENTS = {
    "Sotapanna": {
        "fetters_broken": ["sakkaya_ditthi", "vicikiccha", "silabbata_paramasa"],
        "min_fetters": 3,
        "description": "Stream Enterer - First 3 fetters removed"
    },
    "Sakadagami": {
        "fetters_broken": ["sakkaya_ditthi", "vicikiccha", "silabbata_paramasa"],
        "fetters_weakened": ["kama_raga", "vyapada"],
        "min_fetters": 3,
        "description": "Once Returner - First 3 removed, 4-5 weakened"
    },
    "Anagami": {
        "fetters_broken": ["sakkaya_ditthi", "vicikiccha", "silabbata_paramasa", "kama_raga", "vyapada"],
        "min_fetters": 5,
        "description": "Non-Returner - First 5 fetters removed"
    },
    "Arahant": {
        "fetters_broken": FETTER_ORDER,  # All 10
        "min_fetters": 10,
        "description": "Fully Enlightened - All 10 fetters removed"
    }
}

# Minimum Pāramī levels for each attainment (rule of thumb)
MIN_PARAMI_FOR_ATTAINMENT = {
    "Sotapanna": {
        "total_avg": 3.0,  # Average level across all 10 pāramī
        "sila": 3,         # Minimum virtue level
        "panna": 2,        # Minimum wisdom level
        "sati": 2          # Minimum mindfulness
    },
    "Sakadagami": {
        "total_avg": 4.5,
        "sila": 4,
        "panna": 3,
        "sati": 3
    },
    "Anagami": {
        "total_avg": 6.0,
        "sila": 5,
        "panna": 4,
        "sati": 4,
        "nekkhamma": 4  # Renunciation becomes important
    },
    "Arahant": {
        "total_avg": 8.0,
        "sila": 7,
        "panna": 7,
        "sati": 6,
        "upekkha": 6  # Equanimity critical
    }
}

# Typical age ranges for attainments (very rough guidelines)
TYPICAL_AGE_RANGES = {
    "Sotapanna": (20, 80),    # Can happen at any adult age
    "Sakadagami": (25, 85),
    "Anagami": (30, 90),
    "Arahant": (35, 95)       # Typically requires more life experience
}


# ============================================================================
# VALIDATION RESULT MODEL
# ============================================================================

class ValidationResult(BaseModel):
    """Result of a validation check"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []


# ============================================================================
# VALIDATOR FUNCTIONS
# ============================================================================

def validate_fetter_progression(
    fetters_broken: List[str],
    new_fetter_to_break: Optional[str] = None
) -> ValidationResult:
    """
    Validate that fetters are broken in the correct order according to Buddhist teachings.
    
    Rules:
    1. First 3 fetters (sakkaya_ditthi, vicikiccha, silabbata_paramasa) must be broken together
    2. Cannot break higher fetters before lower ones
    3. Fetters 4-5 (kama_raga, vyapada) typically broken together
    4. Fetters 6-10 broken at Arahant stage
    
    Args:
        fetters_broken: List of fetters already broken
        new_fetter_to_break: Optional fetter attempting to break
        
    Returns:
        ValidationResult with is_valid flag and error messages
    """
    result = ValidationResult(is_valid=True)
    
    # If trying to break a new fetter
    if new_fetter_to_break:
        if new_fetter_to_break not in FETTER_ORDER:
            result.is_valid = False
            result.errors.append(f"Unknown fetter: {new_fetter_to_break}")
            return result
            
        if new_fetter_to_break in fetters_broken:
            result.warnings.append(f"Fetter '{new_fetter_to_break}' is already broken")
            return result
        
        fetter_index = FETTER_ORDER.index(new_fetter_to_break)
        
        # Rule 1: First 3 fetters must be broken together
        if fetter_index < 3:
            first_three = FETTER_ORDER[:3]
            missing = [f for f in first_three if f not in fetters_broken and f != new_fetter_to_break]
            if missing:
                result.is_valid = False
                result.errors.append(
                    f"Cannot break '{new_fetter_to_break}' alone. "
                    f"The first three fetters must be broken together at Stream Entry. "
                    f"Missing: {', '.join(missing)}"
                )
                return result
        
        # Rule 2: Cannot break higher fetter before lower ones
        for i in range(fetter_index):
            lower_fetter = FETTER_ORDER[i]
            if lower_fetter not in fetters_broken:
                result.is_valid = False
                result.errors.append(
                    f"Cannot break fetter '{new_fetter_to_break}' (#{fetter_index + 1}) "
                    f"before breaking '{lower_fetter}' (#{i + 1}). "
                    f"Fetters must be broken in sequential order."
                )
                return result
        
        # Suggestion: Fetters 4-5 typically broken together
        if new_fetter_to_break in ["kama_raga", "vyapada"]:
            other = "vyapada" if new_fetter_to_break == "kama_raga" else "kama_raga"
            if other not in fetters_broken:
                result.suggestions.append(
                    f"Consider breaking '{other}' as well. "
                    f"Fetters 4-5 (kama_raga & vyapada) are typically weakened/broken together at Non-Returner stage."
                )
    
    # Validate current fetter set consistency
    for fetter in fetters_broken:
        if fetter not in FETTER_ORDER:
            result.is_valid = False
            result.errors.append(f"Unknown fetter in broken list: {fetter}")
            continue
            
        fetter_index = FETTER_ORDER.index(fetter)
        
        # Check all lower fetters are also broken
        for i in range(fetter_index):
            lower_fetter = FETTER_ORDER[i]
            if lower_fetter not in fetters_broken:
                result.is_valid = False
                result.errors.append(
                    f"Inconsistent state: '{fetter}' is broken but '{lower_fetter}' "
                    f"(which should be broken first) is not."
                )
    
    return result


def validate_character_status_transition(
    current_type: str,
    current_path_stage: Optional[str],
    fetters_broken: List[str],
    new_type: Optional[str] = None,
    new_path_stage: Optional[str] = None
) -> ValidationResult:
    """
    Validate character status transitions based on fetters broken.
    
    Args:
        current_type: Current character type (Puthujjana/Sekha/Asekha)
        current_path_stage: Current path stage (Sotapanna/Sakadagami/Anagami/Arahant)
        fetters_broken: List of fetters broken
        new_type: New character type (if transitioning)
        new_path_stage: New path stage (if transitioning)
        
    Returns:
        ValidationResult
    """
    result = ValidationResult(is_valid=True)
    
    target_type = new_type or current_type
    target_path = new_path_stage or current_path_stage
    
    # Puthujjana (worldling) should have no fetters broken and no path stage
    if target_type == "Puthujjana":
        if fetters_broken:
            result.is_valid = False
            result.errors.append(
                f"Puthujjana (worldling) cannot have broken fetters. "
                f"Found {len(fetters_broken)} broken: {', '.join(fetters_broken)}"
            )
        if target_path:
            result.is_valid = False
            result.errors.append(
                f"Puthujjana cannot have a path stage. Remove path_stage or change type to Sekha/Asekha."
            )
        return result
    
    # Sekha (learner) or Asekha (beyond training) must have a path stage
    if target_type in ["Sekha", "Asekha"] and not target_path:
        result.is_valid = False
        result.errors.append(
            f"Character type '{target_type}' must have a path_stage "
            f"(Sotapanna, Sakadagami, Anagami, or Arahant)"
        )
        return result
    
    # Validate path stage requirements
    if target_path:
        if target_path not in PATH_STAGE_REQUIREMENTS:
            result.is_valid = False
            result.errors.append(f"Unknown path stage: {target_path}")
            return result
        
        requirements = PATH_STAGE_REQUIREMENTS[target_path]
        required_fetters = requirements["fetters_broken"]
        min_count = requirements["min_fetters"]
        
        # Check all required fetters are broken
        missing_fetters = [f for f in required_fetters if f not in fetters_broken]
        if missing_fetters:
            result.is_valid = False
            result.errors.append(
                f"Cannot attain {target_path} stage. "
                f"Missing required fetters: {', '.join(missing_fetters)}. "
                f"Description: {requirements['description']}"
            )
        
        # Check minimum count
        if len(fetters_broken) < min_count:
            result.is_valid = False
            result.errors.append(
                f"{target_path} requires at least {min_count} fetters broken, "
                f"but only {len(fetters_broken)} are broken."
            )
        
        # Type consistency
        if target_path == "Arahant" and target_type != "Asekha":
            result.warnings.append(
                f"Arahant attainment should have type 'Asekha' (beyond training), not '{target_type}'"
            )
        elif target_path in ["Sotapanna", "Sakadagami", "Anagami"] and target_type == "Asekha":
            result.warnings.append(
                f"Path stage '{target_path}' should have type 'Sekha' (learner), not 'Asekha'"
            )
    
    return result


def validate_parami_for_attainment(
    path_stage: Optional[str],
    parami_levels: Dict[str, int],
    sati_level: int,
    panna_level: int
) -> ValidationResult:
    """
    Validate that Pāramī (perfections) levels are sufficient for claimed attainment.
    
    Args:
        path_stage: Claimed path stage (Sotapanna/Sakadagami/Anagami/Arahant)
        parami_levels: Dict of 10 pāramī with their levels (0-10)
        sati_level: Mindfulness mastery level
        panna_level: Wisdom mastery level
        
    Returns:
        ValidationResult
    """
    result = ValidationResult(is_valid=True)
    
    if not path_stage or path_stage not in MIN_PARAMI_FOR_ATTAINMENT:
        return result  # No validation needed for Puthujjana
    
    requirements = MIN_PARAMI_FOR_ATTAINMENT[path_stage]
    
    # Calculate average pāramī level
    if parami_levels:
        avg_parami = sum(parami_levels.values()) / len(parami_levels)
    else:
        avg_parami = 0
    
    # Check average level
    if avg_parami < requirements["total_avg"]:
        result.warnings.append(
            f"{path_stage} typically requires average Pāramī level of {requirements['total_avg']}, "
            f"but current average is {avg_parami:.1f}. "
            f"While attainment is possible, more cultivation is recommended."
        )
    
    # Check specific pāramī requirements
    for parami_name, min_level in requirements.items():
        if parami_name == "total_avg":
            continue
        
        if parami_name == "sati":
            current = sati_level
            label = "Sati (mindfulness)"
        elif parami_name == "panna":
            current = panna_level
            label = "Panna (wisdom)"
        else:
            current = parami_levels.get(parami_name, 0)
            label = f"Pāramī '{parami_name}'"
        
        if current < min_level:
            result.warnings.append(
                f"{label} level is {current}, but {path_stage} typically requires {min_level}+. "
                f"Further development recommended."
            )
    
    # Suggestions based on path stage
    if path_stage == "Sotapanna":
        result.suggestions.append(
            "Focus on developing Sīla (virtue) and Paññā (wisdom) for stable Stream Entry."
        )
    elif path_stage == "Anagami":
        if parami_levels.get("nekkhamma", 0) < 4:
            result.suggestions.append(
                "Develop Nekkhamma (renunciation) further for Non-Returner stage."
            )
    elif path_stage == "Arahant":
        if parami_levels.get("upekkha", 0) < 6:
            result.suggestions.append(
                "Upekkha (equanimity) is essential for Arahant. Consider more cultivation."
            )
    
    return result


def validate_age_spiritual_development(
    age: int,
    path_stage: Optional[str],
    fetters_broken: List[str]
) -> ValidationResult:
    """
    Check if age is consistent with spiritual development level.
    Provides warnings for unusual patterns (not strict errors).
    
    Args:
        age: Current age in years
        path_stage: Path stage attainment
        fetters_broken: List of fetters broken
        
    Returns:
        ValidationResult (usually warnings, rarely errors)
    """
    result = ValidationResult(is_valid=True)
    
    if not path_stage:
        return result  # No validation for Puthujjana
    
    if path_stage not in TYPICAL_AGE_RANGES:
        return result
    
    min_age, max_age = TYPICAL_AGE_RANGES[path_stage]
    
    # Too young warning
    if age < min_age:
        result.warnings.append(
            f"Age {age} is unusually young for {path_stage} attainment. "
            f"Typical range is {min_age}-{max_age} years. "
            f"While not impossible, this is very rare and suggests exceptional past-life development."
        )
    
    # Very young error (under 18 for any noble attainment)
    if age < 18 and len(fetters_broken) >= 3:
        result.is_valid = False
        result.errors.append(
            f"Noble attainment before age 18 is extremely rare in Buddhist literature. "
            f"Please verify age ({age}) and spiritual development data."
        )
    
    # Too old is less of an issue, but note it
    if age > max_age:
        result.suggestions.append(
            f"Age {age} is at the upper end of typical range for {path_stage} ({min_age}-{max_age}). "
            f"This is perfectly valid - some practitioners attain enlightenment in old age."
        )
    
    # Age progression suggestions
    if path_stage == "Sotapanna" and age > 70:
        result.suggestions.append(
            "With Stream Entry attained at this age, focus on deepening practice for further progress."
        )
    
    return result


# ============================================================================
# COMPREHENSIVE VALIDATOR
# ============================================================================

def validate_core_profile_spiritual_data(
    character_type: str,
    path_stage: Optional[str],
    fetters_broken: List[str],
    age: int,
    parami_levels: Dict[str, int],
    sati_level: int,
    panna_level: int
) -> Dict[str, ValidationResult]:
    """
    Run all Buddhist logic validations on Core Profile spiritual data.
    
    Returns:
        Dict with results for each validation type
    """
    results = {
        "fetter_progression": validate_fetter_progression(fetters_broken),
        "character_status": validate_character_status_transition(
            character_type, path_stage, fetters_broken
        ),
        "parami_sufficiency": validate_parami_for_attainment(
            path_stage, parami_levels, sati_level, panna_level
        ),
        "age_consistency": validate_age_spiritual_development(
            age, path_stage, fetters_broken
        )
    }
    
    return results


def get_validation_summary(results: Dict[str, ValidationResult]) -> Dict:
    """
    Summarize validation results into actionable summary.
    
    Returns:
        Dict with overall validity, error count, warning count, all messages
    """
    all_errors = []
    all_warnings = []
    all_suggestions = []
    
    for validator_name, result in results.items():
        all_errors.extend([f"[{validator_name}] {e}" for e in result.errors])
        all_warnings.extend([f"[{validator_name}] {w}" for w in result.warnings])
        all_suggestions.extend([f"[{validator_name}] {s}" for s in result.suggestions])
    
    is_valid = all(r.is_valid for r in results.values())
    
    return {
        "is_valid": is_valid,
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
        "suggestion_count": len(all_suggestions),
        "errors": all_errors,
        "warnings": all_warnings,
        "suggestions": all_suggestions
    }
