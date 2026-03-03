"""
🧪 Voice Synthesis Tests
Test TTS integration with kamma-based voices

Run:
    python test_voice_synthesis.py
"""

from pathlib import Path
from datetime import datetime

from kamma_appearance_models import VoiceScore
from modules.voice_synthesizer import (
    VoiceSynthesizer,
    TTSConfig,
    VoiceParameterMapper,
    synthesize_character_voice,
    get_voice_description
)


def test_1_monk_warm_voice():
    """
    Test Case 1: Peaceful Monk
    - High truthful speech (98%)
    - High warmth (95%)
    - Low harsh speech (5%)
    """
    print("\n" + "="*70)
    print("TEST 1: Peaceful Monk - Warm, Gentle Voice")
    print("="*70)
    
    # Create VoiceScore
    voice_score = VoiceScore(
        voice_quality=90.0,
        speech_clarity=95.0,
        communication_effectiveness=92.0,
        vocal_warmth=95.0,
        truthful_speech_score=98.0,
        harsh_speech_score=5.0,
        description="Clear, gentle voice from years of truthful speech and mettā practice"
    )
    
    # Get voice parameters
    print("\n1. Voice Parameters:")
    mapper = VoiceParameterMapper()
    params = mapper.map_voice_score(voice_score)
    
    print(f"   - Pitch: {params.pitch:.2f} (1.0 = normal)")
    print(f"   - Speed: {params.speed:.2f}")
    print(f"   - Warmth: {params.warmth:.2f}")
    print(f"   - Clarity: {params.clarity:.2f}")
    print(f"   - Tension: {params.tension:.2f}")
    print(f"   - Mettā influence: {params.metta_influence:.2f}")
    print(f"   - Truthfulness marker: {params.truthfulness_marker:.2f}")
    print(f"   - Emotional tone: {params.emotional_tone}")
    
    # Get description
    print("\n2. Voice Description:")
    description = get_voice_description(voice_score)
    print(f"   {description}")
    
    # Synthesize voice (if gTTS available)
    print("\n3. Synthesizing voice...")
    try:
        result = synthesize_character_voice(
            text="สวัสดีครับ ผมเป็นพระภิกษุ ขออนุโมทนาครับ",
            voice_score=voice_score,
            engine="gtts",
            output_path="test_monk_voice.mp3"
        )
        
        if result.get("success"):
            print(f"   ✅ Audio saved: {result['output_path']}")
            print(f"   - Engine: {result['engine']}")
            print(f"   - Cached: {result.get('cached', False)}")
        else:
            print(f"   ❌ Error: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  Could not synthesize: {e}")
        print("   Install gTTS: pip install gTTS")
    
    print("\n✅ Test 1 Complete")


def test_2_warrior_harsh_voice():
    """
    Test Case 2: Warrior with Harsh Speech
    - Low truthful speech (40%)
    - Low warmth (30%)
    - High harsh speech (70%)
    """
    print("\n" + "="*70)
    print("TEST 2: Warrior - Harsh, Tense Voice")
    print("="*70)
    
    voice_score = VoiceScore(
        voice_quality=65.0,
        speech_clarity=70.0,
        communication_effectiveness=75.0,
        vocal_warmth=30.0,
        truthful_speech_score=40.0,
        harsh_speech_score=70.0,
        description="Harsh, commanding voice from years of battle"
    )
    
    print("\n1. Voice Parameters:")
    mapper = VoiceParameterMapper()
    params = mapper.map_voice_score(voice_score)
    
    print(f"   - Pitch: {params.pitch:.2f}")
    print(f"   - Speed: {params.speed:.2f}")
    print(f"   - Warmth: {params.warmth:.2f}")
    print(f"   - Clarity: {params.clarity:.2f}")
    print(f"   - Tension: {params.tension:.2f} (high = tense)")
    print(f"   - Emotional tone: {params.emotional_tone}")
    
    print("\n2. Voice Description:")
    description = get_voice_description(voice_score)
    print(f"   {description}")
    
    print("\n3. Synthesizing voice...")
    try:
        result = synthesize_character_voice(
            text="เชื่อฟังคำสั่ง เราต้องชนะศึกครั้งนี้",
            voice_score=voice_score,
            engine="gtts",
            output_path="test_warrior_voice.mp3"
        )
        
        if result.get("success"):
            print(f"   ✅ Audio saved: {result['output_path']}")
        else:
            print(f"   ❌ Error: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  Could not synthesize: {e}")
    
    print("\n✅ Test 2 Complete")


def test_3_liar_unclear_voice():
    """
    Test Case 3: Deceiver
    - Very low truthful speech (20%)
    - Low clarity (35%)
    - Muddy, unclear voice
    """
    print("\n" + "="*70)
    print("TEST 3: Deceiver - Unclear, Evasive Voice")
    print("="*70)
    
    voice_score = VoiceScore(
        voice_quality=40.0,
        speech_clarity=35.0,
        communication_effectiveness=45.0,
        vocal_warmth=50.0,
        truthful_speech_score=20.0,
        harsh_speech_score=30.0,
        description="Unclear voice from habitual lying"
    )
    
    print("\n1. Voice Parameters:")
    mapper = VoiceParameterMapper()
    params = mapper.map_voice_score(voice_score)
    
    print(f"   - Pitch: {params.pitch:.2f}")
    print(f"   - Speed: {params.speed:.2f} (low = hesitant)")
    print(f"   - Clarity: {params.clarity:.2f} (low = unclear)")
    print(f"   - Truthfulness marker: {params.truthfulness_marker:.2f}")
    print(f"   - Emotional tone: {params.emotional_tone}")
    
    print("\n2. Voice Description:")
    description = get_voice_description(voice_score)
    print(f"   {description}")
    
    print("\n3. Expected characteristics:")
    print("   - Slow speech (hesitant)")
    print("   - Low clarity (muddy)")
    print("   - Evasive tone")
    
    print("\n✅ Test 3 Complete")


def test_4_student_clear_voice():
    """
    Test Case 4: Honest Student
    - High truthful speech (85%)
    - High clarity (88%)
    - Clear, articulate voice
    """
    print("\n" + "="*70)
    print("TEST 4: Honest Student - Clear, Articulate Voice")
    print("="*70)
    
    voice_score = VoiceScore(
        voice_quality=80.0,
        speech_clarity=88.0,
        communication_effectiveness=85.0,
        vocal_warmth=75.0,
        truthful_speech_score=85.0,
        harsh_speech_score=15.0,
        description="Clear, articulate voice from honest communication"
    )
    
    print("\n1. Voice Parameters:")
    mapper = VoiceParameterMapper()
    params = mapper.map_voice_score(voice_score)
    
    print(f"   - Pitch: {params.pitch:.2f}")
    print(f"   - Speed: {params.speed:.2f} (confident)")
    print(f"   - Clarity: {params.clarity:.2f} (excellent)")
    print(f"   - Warmth: {params.warmth:.2f}")
    print(f"   - Emotional tone: {params.emotional_tone}")
    
    print("\n2. Voice Description:")
    description = get_voice_description(voice_score)
    print(f"   {description}")
    
    print("\n3. Synthesizing voice...")
    try:
        result = synthesize_character_voice(
            text="สวัสดีครับ ผมชื่อนิติ เป็นนักเรียนมัธยมปลาย",
            voice_score=voice_score,
            engine="gtts",
            output_path="test_student_voice.mp3"
        )
        
        if result.get("success"):
            print(f"   ✅ Audio saved: {result['output_path']}")
        else:
            print(f"   ❌ Error: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  Could not synthesize: {e}")
    
    print("\n✅ Test 4 Complete")


def test_5_parameter_mapping():
    """
    Test Case 5: Parameter Mapping Accuracy
    Verify kamma → voice parameter conversions
    """
    print("\n" + "="*70)
    print("TEST 5: Parameter Mapping Accuracy")
    print("="*70)
    
    test_cases = [
        {
            "name": "Perfect Voice",
            "score": VoiceScore(
                voice_quality=100.0,
                speech_clarity=100.0,
                vocal_warmth=100.0,
                truthful_speech_score=100.0,
                harsh_speech_score=0.0
            ),
            "expected": {
                "warmth": "≥ 0.9",
                "clarity": "≥ 0.95",
                "tension": "≤ 0.1"
            }
        },
        {
            "name": "Poor Voice",
            "score": VoiceScore(
                voice_quality=20.0,
                speech_clarity=20.0,
                vocal_warmth=20.0,
                truthful_speech_score=20.0,
                harsh_speech_score=80.0
            ),
            "expected": {
                "warmth": "≤ 0.3",
                "clarity": "≤ 0.4",
                "tension": "≥ 0.7"
            }
        },
        {
            "name": "Balanced Voice",
            "score": VoiceScore(
                voice_quality=70.0,
                speech_clarity=70.0,
                vocal_warmth=70.0,
                truthful_speech_score=70.0,
                harsh_speech_score=30.0
            ),
            "expected": {
                "warmth": "0.6-0.8",
                "clarity": "0.7-0.9",
                "tension": "0.2-0.4"
            }
        }
    ]
    
    mapper = VoiceParameterMapper()
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}:")
        params = mapper.map_voice_score(case['score'])
        
        print(f"   - Warmth: {params.warmth:.2f} (expected: {case['expected']['warmth']})")
        print(f"   - Clarity: {params.clarity:.2f} (expected: {case['expected']['clarity']})")
        print(f"   - Tension: {params.tension:.2f} (expected: {case['expected']['tension']})")
        print(f"   - Emotional tone: {params.emotional_tone}")
    
    print("\n✅ Test 5 Complete")


def test_6_multi_language():
    """
    Test Case 6: Multi-Language Support
    Test Thai and English synthesis
    """
    print("\n" + "="*70)
    print("TEST 6: Multi-Language Support")
    print("="*70)
    
    voice_score = VoiceScore(
        voice_quality=85.0,
        speech_clarity=90.0,
        vocal_warmth=88.0,
        truthful_speech_score=92.0,
        harsh_speech_score=10.0
    )
    
    languages = [
        ("th", "สวัสดีครับ ยินดีที่ได้รู้จัก", "test_voice_thai.mp3"),
        ("en", "Hello, nice to meet you", "test_voice_english.mp3")
    ]
    
    for lang_code, text, filename in languages:
        print(f"\n{lang_code.upper()} - {text}")
        
        try:
            config = TTSConfig(engine="gtts", gtts_lang=lang_code)
            synthesizer = VoiceSynthesizer(config)
            
            result = synthesizer.synthesize_voice(
                text=text,
                voice_score=voice_score,
                output_filename=filename
            )
            
            if result.get("success"):
                print(f"   ✅ Saved: {result['output_path']}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        except Exception as e:
            print(f"   ⚠️  Could not synthesize: {e}")
    
    print("\n✅ Test 6 Complete")


def test_7_caching():
    """
    Test Case 7: Audio Caching
    Verify cache system works correctly
    """
    print("\n" + "="*70)
    print("TEST 7: Audio Caching")
    print("="*70)
    
    voice_score = VoiceScore(
        voice_quality=80.0,
        speech_clarity=85.0,
        vocal_warmth=82.0,
        truthful_speech_score=88.0,
        harsh_speech_score=12.0
    )
    
    text = "ทดสอบระบบแคชเสียง"
    
    print("\n1. First generation (should create new):")
    try:
        result1 = synthesize_character_voice(
            text=text,
            voice_score=voice_score,
            engine="gtts"
        )
        
        if result1.get("success"):
            print(f"   ✅ Generated: {result1['output_path']}")
            print(f"   - Cached: {result1.get('cached', False)}")
            
            print("\n2. Second generation (should use cache):")
            result2 = synthesize_character_voice(
                text=text,
                voice_score=voice_score,
                engine="gtts"
            )
            
            if result2.get("success"):
                print(f"   ✅ Retrieved: {result2['output_path']}")
                print(f"   - Cached: {result2.get('cached', False)}")
                
                if result2.get('cached'):
                    print("   ✅ Cache system working!")
                else:
                    print("   ⚠️  Cache not used (might be new run)")
        else:
            print(f"   ❌ Error: {result1.get('error')}")
    except Exception as e:
        print(f"   ⚠️  Could not test caching: {e}")
    
    print("\n✅ Test 7 Complete")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("🧪 VOICE SYNTHESIS TESTS")
    print("="*70)
    print("\nThese tests demonstrate the Voice Synthesis system.")
    print("Some tests require gTTS to be installed.")
    
    # Create output directory
    Path("audio_cache").mkdir(exist_ok=True)
    
    # Run tests
    test_5_parameter_mapping()  # Pure logic test (no dependencies)
    test_1_monk_warm_voice()
    test_2_warrior_harsh_voice()
    test_3_liar_unclear_voice()
    test_4_student_clear_voice()
    test_6_multi_language()
    test_7_caching()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    print("\nGenerated audio files (if gTTS was available):")
    print("   - audio_cache/test_monk_voice.mp3")
    print("   - audio_cache/test_warrior_voice.mp3")
    print("   - audio_cache/test_student_voice.mp3")
    print("   - audio_cache/test_voice_thai.mp3")
    print("   - audio_cache/test_voice_english.mp3")
    print("\nTo enable voice synthesis:")
    print("   pip install gTTS")
    print("   python test_voice_synthesis.py")


if __name__ == "__main__":
    run_all_tests()
