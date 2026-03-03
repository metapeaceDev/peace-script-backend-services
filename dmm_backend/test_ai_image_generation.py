"""
🧪 AI Image Generation Tests
Test Stable Diffusion integration with kamma-based appearances

Run:
    python test_ai_image_generation.py
"""

import asyncio
from pathlib import Path
from datetime import datetime

from kamma_appearance_models import (
    KammaAppearanceProfile,
    HealthScore,
    VoiceScore,
    DemeanorScore
)
from modules.appearance_synthesizer import synthesize_from_model
from modules.ai_image_generator import (
    generate_character_image,
    get_prompt_for_character,
    StableDiffusionClient,
    SDConfig
)


def test_1_monk_with_high_metta():
    """
    Test Case 1: Peaceful Monk
    - High mettā (98%)
    - Excellent health
    - Clear, gentle voice
    - Radiant appearance
    """
    print("\n" + "="*70)
    print("TEST 1: Peaceful Monk with High Mettā")
    print("="*70)
    
    # Create profile
    profile = KammaAppearanceProfile(
        model_id="monk-001",
        health_score=HealthScore(
            body_strength=85.0,
            skin_quality=90.0,
            vitality=88.0,
            energy_level=80.0,
            overall_health=88.0,
            protection_kamma_score=95.0,
            harmful_actions_score=5.0,
            description="Excellent health from protection practice and mettā"
        ),
        voice_score=VoiceScore(
            voice_quality=92.0,
            speech_clarity=95.0,
            communication_effectiveness=93.0,
            vocal_warmth=96.0,
            truthful_speech_score=98.0,
            harsh_speech_score=2.0,
            description="Clear, gentle voice from years of truthful speech"
        ),
        demeanor_score=DemeanorScore(
            overall_demeanor=95.0,
            expression_openness=90.0,
            peacefulness=95.0,
            confidence_level=85.0,
            loving_kindness_score=98.0,
            ill_will_score=2.0,
            tension_level=10.0,
            description="Radiant with mettā practice, peaceful and open"
        ),
        overall_kamma_balance=88.0,
        kusala_percentage=95.0,
        akusala_percentage=5.0,
        total_kamma_analyzed=100,
        kamma_influence_summary="High mettā practice creates warm, radiant appearance with peaceful demeanor.",
        distinctive_features=[
            "Radiant smile from loving-kindness",
            "Peaceful aura from meditation",
            "Clear, honest eyes from truthful speech"
        ],
        analysis_timestamp=datetime.utcnow()
    )
    
    # Generate ExternalCharacter
    print("\n1. Generating ExternalCharacter...")
    external = synthesize_from_model(profile, base_template={
        "age": 45,
        "gender": "male",
        "ethnicity": "Thai",
        "height": 170
    })
    
    print(f"   - Age: {external.age}")
    print(f"   - Gender: {external.gender}")
    print(f"   - Skin tone: {external.skin_tone}")
    print(f"   - First impression: {external.first_impression}")
    
    # Get prompt
    print("\n2. Generating SD prompt...")
    prompts = get_prompt_for_character(external, profile, style="portrait")
    
    print(f"\n   Positive Prompt ({len(prompts['positive'])} chars):")
    print(f"   {prompts['positive'][:200]}...")
    
    print(f"\n   Negative Prompt:")
    print(f"   {prompts['negative'][:150]}...")
    
    # Generate image (if SD is running)
    print("\n3. Generating image with Stable Diffusion...")
    print("   (This will only work if SD WebUI API is running)")
    
    try:
        result = generate_character_image(
            external=external,
            kamma_profile=profile,
            output_path="output/test_monk_001.png",
            style="portrait"
        )
        
        if result.get("success"):
            print(f"   ✅ SUCCESS!")
            print(f"   - Saved to: {result['saved_to']}")
            print(f"   - Seed: {result['seed']}")
            print(f"   - Size: {result['width']}x{result['height']}")
        else:
            print(f"   ❌ FAILED: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  Could not generate image: {e}")
        print("   Make sure SD WebUI is running: ./webui.sh --api")
    
    print("\n✅ Test 1 Complete")


def test_2_warrior_mixed_kamma():
    """
    Test Case 2: Conflicted Warrior
    - Mixed kamma (50/50)
    - Strong body, tense mind
    - Confident but harsh
    """
    print("\n" + "="*70)
    print("TEST 2: Conflicted Warrior with Mixed Kamma")
    print("="*70)
    
    profile = KammaAppearanceProfile(
        model_id="warrior-001",
        health_score=HealthScore(
            body_strength=95.0,
            vitality=85.0,
            energy_level=90.0,
            overall_health=75.0,
            protection_kamma_score=60.0,
            harmful_actions_score=40.0,
            description="Strong body but conflicted mind affects health"
        ),
        voice_score=VoiceScore(
            voice_quality=70.0,
            speech_clarity=75.0,
            vocal_warmth=50.0,
            truthful_speech_score=60.0,
            harsh_speech_score=40.0,
            description="Strong voice but sometimes harsh"
        ),
        demeanor_score=DemeanorScore(
            overall_demeanor=65.0,
            confidence_level=85.0,
            peacefulness=40.0,
            tension_level=70.0,
            loving_kindness_score=45.0,
            ill_will_score=55.0,
            description="Confident warrior but inner tension visible"
        ),
        overall_kamma_balance=0.0,  # Balanced
        kusala_percentage=50.0,
        akusala_percentage=50.0,
        total_kamma_analyzed=80,
        kamma_influence_summary="Mixed kamma creates strong but tense appearance.",
        distinctive_features=[
            "Strong, muscular build",
            "Intense gaze",
            "Tension in jaw and shoulders"
        ],
        analysis_timestamp=datetime.utcnow()
    )
    
    print("\n1. Generating ExternalCharacter...")
    external = synthesize_from_model(profile, base_template={
        "age": 32,
        "gender": "male",
        "ethnicity": "Thai",
        "height": 180
    })
    
    print(f"   - Body type: {external.body_type}")
    print(f"   - Fitness level: {external.fitness_level}/10")
    print(f"   - First impression: {external.first_impression}")
    
    print("\n2. Generating SD prompt...")
    prompts = get_prompt_for_character(external, profile, style="cinematic")
    
    print(f"   Positive Prompt: {prompts['positive'][:200]}...")
    
    print("\n3. Attempting image generation...")
    try:
        result = generate_character_image(
            external=external,
            kamma_profile=profile,
            output_path="output/test_warrior_001.png",
            style="cinematic"
        )
        
        if result.get("success"):
            print(f"   ✅ Image saved to: {result['saved_to']}")
        else:
            print(f"   ❌ {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    print("\n✅ Test 2 Complete")


def test_3_student_bright():
    """
    Test Case 3: Bright Student
    - High kusala (75%)
    - Intellectual appearance
    - Youthful, energetic
    """
    print("\n" + "="*70)
    print("TEST 3: Bright Student")
    print("="*70)
    
    profile = KammaAppearanceProfile(
        model_id="student-001",
        health_score=HealthScore(
            body_strength=70.0,
            energy_level=90.0,
            vitality=85.0,
            overall_health=82.0,
            description="Youthful energy and health"
        ),
        voice_score=VoiceScore(
            voice_quality=85.0,
            speech_clarity=88.0,
            communication_effectiveness=87.0,
            description="Clear, articulate speech"
        ),
        demeanor_score=DemeanorScore(
            overall_demeanor=80.0,
            expression_openness=85.0,
            confidence_level=75.0,
            peacefulness=70.0,
            intellectual_appearance=92.0,
            charisma_modifier=5.0,
            description="Bright, intellectual presence"
        ),
        overall_kamma_balance=50.0,
        kusala_percentage=75.0,
        akusala_percentage=25.0,
        total_kamma_analyzed=60,
        kamma_influence_summary="Positive kamma creates bright, intellectual appearance.",
        distinctive_features=[
            "Bright, curious eyes",
            "Energetic posture",
            "Friendly smile"
        ],
        analysis_timestamp=datetime.utcnow()
    )
    
    print("\n1. Generating ExternalCharacter...")
    external = synthesize_from_model(profile, base_template={
        "age": 22,
        "gender": "female",
        "ethnicity": "Thai",
        "height": 165
    })
    
    print(f"   - Age: {external.age}")
    print(f"   - Charisma: {external.charisma_level}/10")
    print(f"   - First impression: {external.first_impression}")
    
    print("\n2. Generating SD prompt...")
    prompts = get_prompt_for_character(external, profile, style="realistic")
    
    print(f"   Positive Prompt: {prompts['positive'][:200]}...")
    
    print("\n3. Attempting image generation...")
    try:
        result = generate_character_image(
            external=external,
            kamma_profile=profile,
            output_path="output/test_student_001.png",
            style="realistic"
        )
        
        if result.get("success"):
            print(f"   ✅ Image saved to: {result['saved_to']}")
        else:
            print(f"   ❌ {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    print("\n✅ Test 3 Complete")


def test_4_prompt_variations():
    """
    Test Case 4: Style Variations
    Test different prompt styles for same character
    """
    print("\n" + "="*70)
    print("TEST 4: Style Variations")
    print("="*70)
    
    # Simple profile
    profile = KammaAppearanceProfile(
        model_id="test-variations",
        health_score=HealthScore(overall_health=75.0),
        voice_score=VoiceScore(voice_quality=75.0),
        demeanor_score=DemeanorScore(overall_demeanor=75.0),
        overall_kamma_balance=25.0,
        kusala_percentage=70.0,
        akusala_percentage=30.0,
        total_kamma_analyzed=50,
        kamma_influence_summary="Balanced appearance",
        distinctive_features=[],
        analysis_timestamp=datetime.utcnow()
    )
    
    external = synthesize_from_model(profile, base_template={
        "age": 30,
        "gender": "male",
        "ethnicity": "Thai"
    })
    
    styles = ["realistic", "anime", "portrait", "cinematic"]
    
    for style in styles:
        print(f"\n{style.upper()} Style:")
        prompts = get_prompt_for_character(external, profile, style=style)
        print(f"   {prompts['positive'][:150]}...")
    
    print("\n✅ Test 4 Complete")


def test_5_api_connectivity():
    """
    Test Case 5: SD API Connection
    Check if Stable Diffusion API is accessible
    """
    print("\n" + "="*70)
    print("TEST 5: Stable Diffusion API Connectivity")
    print("="*70)
    
    try:
        import requests
        
        api_url = "http://localhost:7860"
        
        print(f"\n1. Testing connection to: {api_url}")
        response = requests.get(f"{api_url}/sdapi/v1/sd-models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Connected successfully!")
            print(f"   - Available models: {len(models)}")
            if models:
                print(f"   - First model: {models[0].get('title', 'Unknown')}")
        else:
            print(f"   ❌ Connection failed: {response.status_code}")
    
    except ImportError:
        print("   ⚠️  'requests' library not installed")
        print("   Install with: pip install requests")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to SD API at {api_url}")
        print("   Make sure SD WebUI is running:")
        print("   cd stable-diffusion-webui && ./webui.sh --api")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Test 5 Complete")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("🧪 AI IMAGE GENERATION TESTS")
    print("="*70)
    print("\nThese tests demonstrate the AI Image Generation system.")
    print("Some tests require Stable Diffusion WebUI to be running.")
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Run tests
    test_5_api_connectivity()  # Check SD first
    test_4_prompt_variations()  # Prompt generation (no SD needed)
    test_1_monk_with_high_metta()
    test_2_warrior_mixed_kamma()
    test_3_student_bright()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    print("\nGenerated images (if SD was running):")
    print("   - output/test_monk_001.png")
    print("   - output/test_warrior_001.png")
    print("   - output/test_student_001.png")
    print("\nTo enable image generation:")
    print("   1. Install SD WebUI: git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git")
    print("   2. Run with API: ./webui.sh --api")
    print("   3. Re-run tests: python test_ai_image_generation.py")


if __name__ == "__main__":
    run_all_tests()
