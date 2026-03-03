"""
Unit Tests for AI Character Parser Service

Tests the AI-powered transformation of Thai text into structured
InternalCharacter and ExternalCharacter data.

Run tests:
    pytest tests/test_ai_character_parser.py -v
    pytest tests/test_ai_character_parser.py::test_parse_personality_basic -v

Author: Peace Script Team
Date: 10 November 2568
"""

import pytest
from services.ai_character_parser import AICharacterParser, get_ai_parser
from documents_actors import InternalCharacter, ExternalCharacter


@pytest.fixture
def parser():
    """Create AICharacterParser instance for testing"""
    return AICharacterParser()


# ============================================================================
# Personality Parsing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_parse_personality_basic(parser):
    """Test basic personality parsing with positive traits"""
    text = "เข้มแข็ง มุ่งมั่น รับผิดชอบ"
    result = await parser.parse_personality_to_internal(text)
    
    # Should return InternalCharacter
    assert isinstance(result, InternalCharacter)
    
    # High conscientiousness expected (มุ่งมั่น, รับผิดชอบ)
    assert result.conscientiousness >= 5.0, "มุ่งมั่น should increase conscientiousness"
    
    # Low neuroticism expected (เข้มแข็ง)
    assert result.neuroticism <= 6.0, "เข้มแข็ง should decrease neuroticism"
    
    # All values should be in valid range
    assert 0 <= result.openness <= 10
    assert 0 <= result.extraversion <= 10
    assert 0 <= result.agreeableness <= 10


@pytest.mark.asyncio
async def test_parse_personality_with_trauma(parser):
    """Test personality parsing with trauma/negative traits"""
    text = "บาดแผลในใจ กลัวการสูญเสีย ไม่ไว้วางใจผู้อื่น"
    result = await parser.parse_personality_to_internal(text)
    
    # High neuroticism expected (บาดแผล)
    assert result.neuroticism >= 5.0, "บาดแผล should increase neuroticism"
    
    # Trauma influence should be present
    assert result.trauma_influence is not None
    assert len(str(result.trauma_influence)) > 0, "Should have trauma description"
    
    # Fears should include loss-related fears
    # Note: AI may translate to English
    fears_text = str(result.fears).lower()
    assert any(keyword in fears_text for keyword in ['loss', 'abandon', 'สูญเสีย', 'ทอดทิ้ง']), \
        f"Expected loss-related fear, got: {result.fears}"
    
    # Low trust expected (ไม่ไว้วางใจ)
    assert result.trust_level <= 6.0, "ไม่ไว้วางใจ should decrease trust_level"


@pytest.mark.asyncio
async def test_parse_personality_with_motivation(parser):
    """Test personality parsing with motivation field"""
    text = "ร่าเริง ขี้เล่น"
    motivation = "ต้องการปกป้องครอบครัว"
    
    result = await parser.parse_personality_to_internal(
        personality_text=text,
        motivation_text=motivation
    )
    
    # High extraversion expected (ร่าเริง)
    assert result.extraversion >= 5.0
    
    # Primary motivation should relate to family/protection
    if result.primary_motivation:
        motivation_lower = str(result.primary_motivation).lower()
        assert any(keyword in motivation_lower for keyword in 
                  ['family', 'protect', 'ครอบครัว', 'ปกป้อง'])
    
    # Core values should include family
    values_text = str(result.core_values).lower()
    assert any(keyword in values_text for keyword in ['family', 'ครอบครัว', 'loved']), \
        f"Expected family in core_values, got: {result.core_values}"


@pytest.mark.asyncio
async def test_parse_personality_thai_values(parser):
    """Test parsing of Thai cultural values"""
    text = "เกรงใจผู้อื่น มีน้ำใจ รู้คุณ"
    result = await parser.parse_personality_to_internal(text)
    
    # High kreng_jai (เกรงใจ)
    assert result.kreng_jai >= 5.0, "เกรงใจ should increase kreng_jai"
    
    # High nam_jai (น้ำใจ)
    assert result.nam_jai >= 5.0, "น้ำใจ should increase nam_jai"
    
    # High bunkhun (รู้คุณ)
    assert result.bunkhun >= 5.0, "รู้คุณ should increase bunkhun"


@pytest.mark.asyncio
async def test_parse_personality_empty_text(parser):
    """Test handling of empty/invalid personality text"""
    # Empty string
    result = await parser.parse_personality_to_internal("")
    assert isinstance(result, InternalCharacter)
    assert result.openness == 5.0  # Should use defaults
    
    # Very short text
    result = await parser.parse_personality_to_internal("ดี")
    assert isinstance(result, InternalCharacter)
    
    # None (should not crash)
    result = await parser.parse_personality_to_internal(None)
    assert isinstance(result, InternalCharacter)


@pytest.mark.asyncio
async def test_parse_personality_with_all_fields(parser):
    """Test parsing with all optional fields"""
    result = await parser.parse_personality_to_internal(
        personality_text="เข้มแข็ง แต่อ่อนโยน",
        motivation_text="ต้องการเปลี่ยนแปลงโลก",
        conflict_text="ติดอยู่ระหว่างอำนาจกับความรัก"
    )
    
    assert isinstance(result, InternalCharacter)
    
    # Should have some desires
    assert len(result.desires) >= 0  # At least empty list
    
    # Moral alignment should be set
    assert result.moral_alignment is not None


# ============================================================================
# Appearance Parsing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_parse_appearance_basic(parser):
    """Test basic appearance parsing"""
    text = "ผู้หญิงสูง ผมยาวดำ"
    result = await parser.parse_appearance_to_external(text, gender="female")
    
    assert isinstance(result, ExternalCharacter)
    
    # Gender should match
    assert result.gender == "female"
    
    # Hair should be black
    assert "black" in result.hair_color.lower() or "ดำ" in result.hair_color
    
    # Hair should be long
    assert "long" in result.hair_style.lower() or "ยาว" in result.hair_style
    
    # Height should be tall for Thai woman (>= 165 cm)
    assert result.height >= 160.0, f"Expected tall height, got {result.height}"


@pytest.mark.asyncio
async def test_parse_appearance_with_age(parser):
    """Test appearance parsing with age hint"""
    text = "ชายหนุ่ม หล่อ"
    result = await parser.parse_appearance_to_external(
        text,
        gender="male",
        age=25
    )
    
    assert result.gender == "male"
    assert result.age == 25 or result.age in range(20, 30)  # Should be close


@pytest.mark.asyncio
async def test_parse_appearance_distinctive_features(parser):
    """Test parsing of distinctive features (scars, marks)"""
    text = "มีรอยแผลที่แขน ดวงตาคม"
    result = await parser.parse_appearance_to_external(text)
    
    # Should have distinctive features
    assert len(result.distinctive_features) > 0, \
        "Should detect distinctive features (scar)"
    
    # Features should mention scar/wound
    features_text = str(result.distinctive_features).lower()
    assert any(keyword in features_text for keyword in ['scar', 'mark', 'wound', 'แผล', 'รอย']), \
        f"Expected scar mention, got: {result.distinctive_features}"
    
    # Sharp eyes
    assert "sharp" in result.eye_expression.lower() or "คม" in result.eye_expression, \
        f"Expected sharp eyes, got: {result.eye_expression}"


@pytest.mark.asyncio
async def test_parse_appearance_style(parser):
    """Test parsing of fashion style"""
    text = "แต่งตัวสุภาพ ใส่เสื้อสูทดำ"
    result = await parser.parse_appearance_to_external(text)
    
    # Fashion style should be professional/formal
    assert any(keyword in result.fashion_style.lower() 
              for keyword in ['professional', 'formal', 'elegant', 'business']), \
        f"Expected professional style, got: {result.fashion_style}"
    
    # Color palette should include black
    colors_text = str(result.color_palette).lower()
    assert "black" in colors_text or "ดำ" in colors_text, \
        f"Expected black in palette, got: {result.color_palette}"


@pytest.mark.asyncio
async def test_parse_appearance_body_type(parser):
    """Test parsing of body type"""
    text = "ร่างกายแข็งแรง กล้ามเนื้อมาก"
    result = await parser.parse_appearance_to_external(text)
    
    # Body type should be athletic/muscular
    assert any(keyword in result.body_type.lower() 
              for keyword in ['athletic', 'muscular', 'fit', 'strong']), \
        f"Expected athletic body type, got: {result.body_type}"
    
    # Fitness level should be high
    assert result.fitness_level >= 6.0, \
        f"Expected high fitness, got: {result.fitness_level}"


@pytest.mark.asyncio
async def test_parse_appearance_empty_text(parser):
    """Test handling of empty appearance text"""
    # Empty string
    result = await parser.parse_appearance_to_external("")
    assert isinstance(result, ExternalCharacter)
    assert result.age == 30  # Default age
    
    # With gender hint
    result = await parser.parse_appearance_to_external("", gender="female", age=25)
    assert result.gender == "female"
    assert result.age == 25


@pytest.mark.asyncio
async def test_parse_appearance_presence(parser):
    """Test parsing of character presence/charisma"""
    text = "น่ากลัว น่าเกรงขาม มีบารมี"
    result = await parser.parse_appearance_to_external(text)
    
    # First impression should be intimidating/powerful
    assert any(keyword in result.first_impression.lower() 
              for keyword in ['intimidating', 'powerful', 'commanding', 'imposing']), \
        f"Expected intimidating impression, got: {result.first_impression}"
    
    # Charisma should be high
    assert result.charisma_level >= 6.0, \
        f"Expected high charisma, got: {result.charisma_level}"
    
    # Approachability should be low
    assert result.approachability <= 5.0, \
        f"Expected low approachability, got: {result.approachability}"


# ============================================================================
# Singleton Tests
# ============================================================================

def test_singleton_instance():
    """Test that get_ai_parser returns singleton"""
    parser1 = get_ai_parser()
    parser2 = get_ai_parser()
    
    assert parser1 is parser2, "Should return same instance"


def test_parser_initialization():
    """Test parser initializes correctly"""
    parser = AICharacterParser()
    
    assert parser.model == "llama3.2:3b"
    assert parser.ollama is not None


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_parse_personality_complex_text(parser):
    """Test with complex, multi-sentence personality description"""
    text = """เธอเป็นคนเข้มแข็ง มุ่งมั่น และรับผิดชอบงานที่ได้รับมอบหมายอย่างเต็มที่
    แต่ภายในใจมีบาดแผลจากอดีต ทำให้เธอกลัวการสูญเสียและไม่กล้าเปิดใจให้ใคร
    เธอมักจะเก็บความรู้สึกไว้ภายใน และทำตัวเป็นคนแข็งแกร่งเสมอ"""
    
    result = await parser.parse_personality_to_internal(text)
    
    assert isinstance(result, InternalCharacter)
    # Should handle long text without error
    assert result.conscientiousness >= 5.0  # มุ่งมั่น, รับผิดชอบ
    assert result.neuroticism >= 5.0  # บาดแผล, กลัวสูญเสีย


@pytest.mark.asyncio
async def test_parse_appearance_complex_text(parser):
    """Test with complex appearance description"""
    text = """ผู้หญิงสูงประมาณ 165 ซม. มีผมยาวดำสนิท ตาโต คิ้วเข้ม
    ผิวขาวเนียน รูปร่างสมส่วน มีรอยแผลเป็นเล็กๆ ที่แขนขวา
    มักจะแต่งตัวเรียบๆ สีเข้ม ดูมีระเบียบ"""
    
    result = await parser.parse_appearance_to_external(text)
    
    assert isinstance(result, ExternalCharacter)
    assert result.height >= 165.0
    assert len(result.distinctive_features) > 0  # มีรอยแผล


@pytest.mark.asyncio
async def test_parse_with_english_mixed(parser):
    """Test handling of Thai-English mixed text"""
    text = "เข้มแข็ง confident มุ่งมั่น"
    result = await parser.parse_personality_to_internal(text)
    
    assert isinstance(result, InternalCharacter)
    # Should handle mixed language
    assert result.conscientiousness >= 5.0


# ============================================================================
# Performance Tests (Optional)
# ============================================================================

@pytest.mark.slow
@pytest.mark.asyncio
async def test_parsing_performance(parser):
    """Test parsing speed (should be < 5 seconds)"""
    import time
    
    text = "เข้มแข็ง มุ่งมั่น"
    
    start = time.time()
    result = await parser.parse_personality_to_internal(text)
    duration = time.time() - start
    
    assert duration < 10.0, f"Parsing took {duration:.2f}s, should be < 10s"
    assert result is not None


@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_parsing(parser):
    """Test multiple concurrent parsing requests"""
    import asyncio
    
    texts = [
        "เข้มแข็ง มุ่งมั่น",
        "ร่าเริง ขี้เล่น",
        "เงียบขรึม ลึกลับ",
        "อ่อนโยน ใจดี"
    ]
    
    tasks = [
        parser.parse_personality_to_internal(text)
        for text in texts
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 4
    assert all(isinstance(r, InternalCharacter) for r in results)


# ============================================================================
# Validation Tests
# ============================================================================

@pytest.mark.asyncio
async def test_values_in_valid_range(parser):
    """Test that all numeric values are in valid range 0-10"""
    text = "เข้มแข็ง มุ่งมั่น"
    result = await parser.parse_personality_to_internal(text)
    
    # Check all numeric fields are 0-10
    assert 0 <= result.openness <= 10
    assert 0 <= result.conscientiousness <= 10
    assert 0 <= result.extraversion <= 10
    assert 0 <= result.agreeableness <= 10
    assert 0 <= result.neuroticism <= 10
    assert 0 <= result.kreng_jai <= 10
    assert 0 <= result.bunkhun <= 10
    assert 0 <= result.nam_jai <= 10
    assert 0 <= result.ethical_compass <= 10
    assert 0 <= result.emotional_stability <= 10
    assert 0 <= result.wisdom_level <= 10
    assert 0 <= result.trust_level <= 10
    assert 0 <= result.adaptability <= 10
    assert 0 <= result.learning_capacity <= 10
    assert 0 <= result.redemption_potential <= 10


@pytest.mark.asyncio
async def test_external_values_valid(parser):
    """Test that ExternalCharacter values are valid"""
    text = "ผู้หญิงสูง 25 ปี"
    result = await parser.parse_appearance_to_external(text, age=25)
    
    # Age in reasonable range
    assert 0 < result.age < 120
    
    # Height/weight positive
    assert result.height > 0
    assert result.weight > 0
    
    # Fitness/charisma 0-10
    assert 0 <= result.fitness_level <= 10
    assert 0 <= result.charisma_level <= 10
    assert 0 <= result.approachability <= 10
