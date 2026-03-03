"""
🧪 Unit Tests for Buddhist Logic Validators
Digital Mind Model v1.4

Tests for core_profile_validators.py functions
"""

import pytest
from core_profile_validators import (
    validate_fetter_progression,
    validate_character_status_transition,
    validate_parami_for_attainment,
    validate_age_spiritual_development,
    validate_core_profile_spiritual_data,
    get_validation_summary,
    FETTER_ORDER
)


# ============================================================================
# TEST FETTER PROGRESSION VALIDATION
# ============================================================================

class TestFetterProgression:
    """Tests for validate_fetter_progression"""
    
    def test_empty_fetters_valid(self):
        """Test that empty fetter list is valid"""
        result = validate_fetter_progression([])
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_first_three_together_valid(self):
        """Test breaking first 3 fetters together (Stream Entry)"""
        first_three = FETTER_ORDER[:3]
        result = validate_fetter_progression(first_three)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_break_first_fetter_alone_invalid(self):
        """Test that breaking first fetter alone is invalid"""
        result = validate_fetter_progression([], new_fetter_to_break="sakkaya_ditthi")
        assert not result.is_valid
        assert any("must be broken together" in err for err in result.errors)
    
    def test_break_second_without_first_invalid(self):
        """Test cannot break higher fetter before lower"""
        result = validate_fetter_progression(
            ["sakkaya_ditthi", "vicikiccha"],
            new_fetter_to_break="kama_raga"  # 4th fetter
        )
        assert not result.is_valid
        assert any("sequential order" in err for err in result.errors)
    
    def test_sequential_progression_valid(self):
        """Test valid sequential progression"""
        # Stream Entry (first 3)
        fetters = FETTER_ORDER[:3]
        result = validate_fetter_progression(fetters)
        assert result.is_valid
        
        # Add 4th fetter
        result = validate_fetter_progression(fetters, new_fetter_to_break=FETTER_ORDER[3])
        assert result.is_valid
    
    def test_all_ten_fetters_valid(self):
        """Test all 10 fetters broken (Arahant)"""
        result = validate_fetter_progression(FETTER_ORDER)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_unknown_fetter_invalid(self):
        """Test unknown fetter name"""
        result = validate_fetter_progression([], new_fetter_to_break="unknown_fetter")
        assert not result.is_valid
        assert any("Unknown fetter" in err for err in result.errors)
    
    def test_suggestion_for_fourth_fifth_together(self):
        """Test suggestion to break 4th and 5th fetters together"""
        first_three = FETTER_ORDER[:3]
        result = validate_fetter_progression(first_three, new_fetter_to_break="kama_raga")
        assert result.is_valid
        assert any("vyapada" in sug for sug in result.suggestions)


# ============================================================================
# TEST CHARACTER STATUS TRANSITION
# ============================================================================

class TestCharacterStatusTransition:
    """Tests for validate_character_status_transition"""
    
    def test_puthujjana_no_fetters(self):
        """Test Puthujjana must have no fetters broken"""
        result = validate_character_status_transition(
            "Puthujjana", None, []
        )
        assert result.is_valid
    
    def test_puthujjana_with_fetters_invalid(self):
        """Test Puthujjana cannot have broken fetters"""
        result = validate_character_status_transition(
            "Puthujjana", None, ["sakkaya_ditthi"]
        )
        assert not result.is_valid
        assert any("cannot have broken fetters" in err for err in result.errors)
    
    def test_sotapanna_requires_first_three(self):
        """Test Sotāpanna requires first 3 fetters"""
        # Valid Sotāpanna
        result = validate_character_status_transition(
            "Sekha", "Sotapanna", FETTER_ORDER[:3]
        )
        assert result.is_valid
        
        # Invalid: missing fetters
        result = validate_character_status_transition(
            "Sekha", "Sotapanna", ["sakkaya_ditthi"]
        )
        assert not result.is_valid
        assert any("Missing required fetters" in err for err in result.errors)
    
    def test_anagami_requires_first_five(self):
        """Test Anāgāmī requires first 5 fetters"""
        result = validate_character_status_transition(
            "Sekha", "Anagami", FETTER_ORDER[:5]
        )
        assert result.is_valid
    
    def test_arahant_requires_all_ten(self):
        """Test Arahant requires all 10 fetters"""
        result = validate_character_status_transition(
            "Asekha", "Arahant", FETTER_ORDER
        )
        assert result.is_valid
        
        # Invalid: missing some
        result = validate_character_status_transition(
            "Asekha", "Arahant", FETTER_ORDER[:8]
        )
        assert not result.is_valid
    
    def test_sekha_requires_path_stage(self):
        """Test Sekha must have a path stage"""
        result = validate_character_status_transition(
            "Sekha", None, FETTER_ORDER[:3]
        )
        assert not result.is_valid
        assert any("must have a path_stage" in err for err in result.errors)
    
    def test_arahant_should_be_asekha(self):
        """Test Arahant should have type Asekha"""
        result = validate_character_status_transition(
            "Sekha", "Arahant", FETTER_ORDER
        )
        assert result.is_valid  # Valid but warning
        assert any("should have type 'Asekha'" in warn for warn in result.warnings)


# ============================================================================
# TEST PARAMI VALIDATION
# ============================================================================

class TestParamiValidation:
    """Tests for validate_parami_for_attainment"""
    
    def test_puthujjana_no_validation(self):
        """Test no validation for Puthujjana"""
        result = validate_parami_for_attainment(
            None,
            {},
            0,
            0
        )
        assert result.is_valid
        assert len(result.warnings) == 0
    
    def test_sotapanna_sufficient_parami(self):
        """Test sufficient pāramī for Sotāpanna"""
        parami = {
            "dana": 3,
            "sila": 4,
            "panna": 3,
            "metta": 2
        }
        result = validate_parami_for_attainment(
            "Sotapanna",
            parami,
            sati_level=3,
            panna_level=3
        )
        assert result.is_valid
        # May have suggestions but no blocking errors
    
    def test_sotapanna_insufficient_parami_warning(self):
        """Test insufficient pāramī gives warnings"""
        parami = {
            "dana": 1,
            "sila": 1,
            "panna": 1
        }
        result = validate_parami_for_attainment(
            "Sotapanna",
            parami,
            sati_level=1,
            panna_level=1
        )
        assert result.is_valid  # Still valid but warnings
        assert len(result.warnings) > 0
        assert any("typically requires" in warn for warn in result.warnings)
    
    def test_arahant_requires_high_parami(self):
        """Test Arahant requires high pāramī levels"""
        # Low pāramī
        parami = {p: 2 for p in ["dana", "sila", "panna", "upekkha"]}
        result = validate_parami_for_attainment(
            "Arahant",
            parami,
            sati_level=2,
            panna_level=2
        )
        assert result.is_valid
        assert len(result.warnings) > 0  # Many warnings
    
    def test_parami_suggestions_for_stages(self):
        """Test stage-specific suggestions"""
        # Anāgāmī should develop nekkhamma
        parami = {"nekkhamma": 1, "sila": 5, "panna": 4}
        result = validate_parami_for_attainment(
            "Anagami",
            parami,
            sati_level=4,
            panna_level=4
        )
        assert any("Nekkhamma" in sug or "renunciation" in sug.lower() 
                   for sug in result.suggestions)


# ============================================================================
# TEST AGE VALIDATION
# ============================================================================

class TestAgeValidation:
    """Tests for validate_age_spiritual_development"""
    
    def test_typical_age_valid(self):
        """Test typical age for attainment"""
        result = validate_age_spiritual_development(
            age=35,
            path_stage="Sotapanna",
            fetters_broken=FETTER_ORDER[:3]
        )
        assert result.is_valid
        assert len(result.warnings) == 0
    
    def test_very_young_attainment_warning(self):
        """Test warning for unusually young attainment (18+ but still young)"""
        result = validate_age_spiritual_development(
            age=19,  # Above 18 but below typical range (20-80)
            path_stage="Sotapanna",
            fetters_broken=FETTER_ORDER[:3]
        )
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("unusually young" in warn.lower() for warn in result.warnings)
    
    def test_under_eighteen_error(self):
        """Test error for attainment under 18"""
        result = validate_age_spiritual_development(
            age=16,
            path_stage="Sotapanna",
            fetters_broken=FETTER_ORDER[:3]
        )
        assert not result.is_valid
        assert any("before age 18" in err for err in result.errors)
    
    def test_old_age_attainment_valid(self):
        """Test old age attainment is valid"""
        result = validate_age_spiritual_development(
            age=75,
            path_stage="Sotapanna",
            fetters_broken=FETTER_ORDER[:3]
        )
        assert result.is_valid
        # May have suggestions but valid
    
    def test_puthujjana_no_validation(self):
        """Test no validation for Puthujjana"""
        result = validate_age_spiritual_development(
            age=10,
            path_stage=None,
            fetters_broken=[]
        )
        assert result.is_valid


# ============================================================================
# TEST COMPREHENSIVE VALIDATION
# ============================================================================

class TestComprehensiveValidation:
    """Tests for validate_core_profile_spiritual_data"""
    
    def test_valid_puthujjana(self):
        """Test valid Puthujjana profile"""
        results = validate_core_profile_spiritual_data(
            character_type="Puthujjana",
            path_stage=None,
            fetters_broken=[],
            age=28,
            parami_levels={"dana": 2, "sila": 3},
            sati_level=2,
            panna_level=1
        )
        
        summary = get_validation_summary(results)
        assert summary["is_valid"]
        assert summary["error_count"] == 0
    
    def test_valid_sotapanna(self):
        """Test valid Sotāpanna profile"""
        results = validate_core_profile_spiritual_data(
            character_type="Sekha",
            path_stage="Sotapanna",
            fetters_broken=FETTER_ORDER[:3],
            age=35,
            parami_levels={"dana": 4, "sila": 5, "panna": 3},
            sati_level=3,
            panna_level=3
        )
        
        summary = get_validation_summary(results)
        assert summary["is_valid"]
    
    def test_invalid_mixed_profile(self):
        """Test invalid profile with multiple errors"""
        results = validate_core_profile_spiritual_data(
            character_type="Puthujjana",
            path_stage="Sotapanna",  # Contradiction
            fetters_broken=FETTER_ORDER[:3],
            age=16,  # Too young
            parami_levels={"dana": 1},
            sati_level=1,
            panna_level=1
        )
        
        summary = get_validation_summary(results)
        assert not summary["is_valid"]
        assert summary["error_count"] > 0
    
    def test_validation_summary_structure(self):
        """Test validation summary structure"""
        results = validate_core_profile_spiritual_data(
            character_type="Sekha",
            path_stage="Arahant",
            fetters_broken=FETTER_ORDER,
            age=45,
            parami_levels={p: 8 for p in ["dana", "sila", "panna", "upekkha"]},
            sati_level=7,
            panna_level=7
        )
        
        summary = get_validation_summary(results)
        
        assert "is_valid" in summary
        assert "error_count" in summary
        assert "warning_count" in summary
        assert "suggestion_count" in summary
        assert "errors" in summary
        assert "warnings" in summary
        assert "suggestions" in summary
        assert isinstance(summary["errors"], list)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
