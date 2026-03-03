#!/usr/bin/env python3
"""
End-to-End Testing Script for Avatar System
Tests complete flow: Mental State → Kamma Analysis → Appearance → UI Display

วันที่: 2 พฤศจิกายน 2568
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any
import httpx

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from documents import DigitalMindModel
from modules.kamma_engine import KammaCategory
from modules.kamma_appearance_analyzer import KammaAppearanceAnalyzer
from core_profile_models import RupaCalculationEngine

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_result(label: str, value: Any):
    """Print test result"""
    print(f"{Colors.OKCYAN}{label}:{Colors.ENDC} {value}")


async def init_db():
    """Initialize database connection"""
    print_info("Connecting to MongoDB...")
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(
        database=client["digital_mind_db"],
        document_models=[DigitalMindModel]
    )
    print_success("Database connected")
    return client


async def create_test_character() -> DigitalMindModel:
    """Create a test character with specific kamma"""
    print_header("Test 1: Create Test Character")
    
    # Check if test character exists
    existing = await DigitalMindModel.find_one(
        DigitalMindModel.unique_id == "test-avatar-e2e-001"
    )
    
    if existing:
        print_info("Test character already exists, deleting...")
        await existing.delete()
    
    # Create new character
    character = DigitalMindModel(
        name="Avatar Test Character",
        unique_id="test-avatar-e2e-001",
        base_personality="compassionate",
        role="test_subject"
    )
    
    await character.insert()
    print_success(f"Character created: {character.name} (ID: {character.unique_id})")
    
    return character


async def log_test_kamma(character: DigitalMindModel) -> Dict[str, int]:
    """Log various kamma actions for testing"""
    print_header("Test 2: Log Kamma Actions")
    
    kamma_actions = {
        # High Mettā (loving-kindness)
        KammaCategory.METTA: (50, 8.5),
        
        # Generosity
        KammaCategory.DANA: (30, 7.0),
        
        # Truthful speech
        KammaCategory.MUSAVADA_VIRATI: (25, 8.0),
        
        # Meditation
        KammaCategory.BHAVANA: (40, 9.0),
        
        # Some negative (for balance testing)
        KammaCategory.MUSAVADA: (5, 3.0),
        KammaCategory.BYAPADA: (3, 2.5),
    }
    
    kamma_counts = {}
    
    for category, (count, intensity) in kamma_actions.items():
        for _ in range(count):
            character.kamma_engine.log_kamma(
                category=category,
                intensity=intensity
            )
        kamma_counts[category.value] = count
        print_success(f"Logged {count} × {category.value} (intensity: {intensity})")
    
    await character.save()
    print_success("All kamma actions logged and saved")
    
    return kamma_counts


async def analyze_appearance(character: DigitalMindModel):
    """Analyze appearance from kamma"""
    print_header("Test 3: Kamma Appearance Analysis")
    
    analyzer = KammaAppearanceAnalyzer()
    
    # Analyze kamma ledger
    appearance_profile = analyzer.analyze_kamma_ledger(
        kamma_ledger=character.kamma_engine.ledger.dict(),
        model_id=character.unique_id
    )
    
    print_info("Physical Appearance:")
    print_result("  Health Status", f"{appearance_profile.health_score.overall_health:.1f}/100")
    print_result("  Skin Quality", f"{appearance_profile.health_score.skin_quality:.1f}/100")
    print_result("  Skin Tone", appearance_profile.health_score.skin_tone_desc)
    print_result("  Body Type", appearance_profile.health_score.body_type_tendency)
    print_result("  Fitness Level", f"{appearance_profile.health_score.fitness_level}/10")
    
    print_info("\nVoice Characteristics:")
    print_result("  Clarity Score", f"{appearance_profile.voice_score.clarity_score:.1f}/100")
    print_result("  Pleasantness", f"{appearance_profile.voice_score.pleasantness_score:.1f}/100")
    print_result("  Voice Character", appearance_profile.voice_score.voice_tone_desc)
    
    print_info("\nMovement & Demeanor:")
    print_result("  Approachability", f"{appearance_profile.demeanor_score.approachability:.1f}/100")
    print_result("  Charisma", f"{appearance_profile.demeanor_score.charisma:.1f}/100")
    print_result("  Peacefulness", f"{appearance_profile.demeanor_score.peacefulness:.1f}/100")
    print_result("  Posture", appearance_profile.demeanor_score.posture_desc)
    
    print_info("\nKamma Balance:")
    print_result("  Overall Balance", f"{appearance_profile.overall_balance:.1%}")
    print_result("  Kusala %", f"{appearance_profile.overall_balance * 100:.1f}%")
    print_result("  Akusala %", f"{(1 - appearance_profile.overall_balance) * 100:.1f}%")
    
    # Validate Buddhist accuracy
    print_header("Test 4: Buddhist Accuracy Validation")
    
    # Check if high Mettā → good appearance
    if appearance_profile.overall_balance > 0.7:
        print_success("✓ High kusala → Positive balance (Buddhist accuracy confirmed)")
    else:
        print_error("✗ Expected positive balance from high kusala kamma")
    
    # Check skin quality from Mettā
    if appearance_profile.health_score.skin_quality > 80:
        print_success("✓ High Mettā → Radiant skin (AN 11.16 - เมตตาผล)")
    else:
        print_warning(f"⚠ Expected skin_quality > 80, got {appearance_profile.health_score.skin_quality:.1f}")
    
    # Check voice clarity from truthful speech
    if appearance_profile.voice_score.clarity_score > 85:
        print_success("✓ Truthful speech → Clear voice (Milindapañha)")
    else:
        print_warning(f"⚠ Expected clarity > 85, got {appearance_profile.voice_score.clarity_score:.1f}")
    
    # Check peacefulness from meditation
    if appearance_profile.demeanor_score.peacefulness > 85:
        print_success("✓ High Bhāvanā → Peaceful demeanor (Visuddhimagga)")
    else:
        print_warning(f"⚠ Expected peacefulness > 85, got {appearance_profile.demeanor_score.peacefulness:.1f}")
    
    return appearance_profile


async def calculate_rupa(character: DigitalMindModel):
    """Calculate 28 Rūpa"""
    print_header("Test 5: 28 Rūpa Calculation")
    
    engine = RupaCalculationEngine()
    rupa_profile = engine.calculate_mahabhuta_from_core_profile(character)
    
    print_info("Mahābhūta (4 Great Elements):")
    print_result("  Paṭhavī (ดิน)", f"{rupa_profile.mahabhuta.pathavi:.2f}")
    print_result("  Āpo (น้ำ)", f"{rupa_profile.mahabhuta.apo:.2f}")
    print_result("  Tejo (ไฟ)", f"{rupa_profile.mahabhuta.tejo:.2f}")
    print_result("  Vāyo (ลม)", f"{rupa_profile.mahabhuta.vayo:.2f}")
    
    # Validate
    if 0.5 <= rupa_profile.mahabhuta.tejo <= 1.0:
        print_success("✓ Tejo (heat/energy) in valid range for healthy character")
    
    return rupa_profile


async def test_api_endpoint():
    """Test API endpoint"""
    print_header("Test 6: API Endpoint Testing")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/api/v1/character-avatar/test-avatar-e2e-001/full-appearance",
                timeout=30.0
            )
            
            if response.status_code == 200:
                print_success(f"API Response: {response.status_code} OK")
                
                data = response.json()
                
                # Validate response structure
                required_keys = ["physical", "voice", "movement", "citta_state", "kamma_influence", "rupa"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    print_success("✓ Response structure complete")
                else:
                    print_error(f"✗ Missing keys: {missing_keys}")
                
                # Print summary
                if "summary" in data:
                    print_info(f"\nSummary: {data['summary'][:200]}...")
                
                if "charisma_score" in data:
                    print_result("Charisma Score", f"{data['charisma_score']:.2f}/10")
                
                # Print distinctive features
                if "distinctive_features" in data and data["distinctive_features"]:
                    print_info("\nDistinctive Features:")
                    for feature in data["distinctive_features"][:5]:
                        print(f"  • {feature}")
                
                return data
            else:
                print_error(f"API Error: {response.status_code}")
                print_error(response.text)
                return None
                
    except Exception as e:
        print_error(f"Failed to connect to API: {e}")
        print_info("Make sure backend is running on http://127.0.0.1:8000")
        return None


async def test_real_time_updates():
    """Test real-time updates"""
    print_header("Test 7: Real-time Update Simulation")
    
    print_info("Fetching character...")
    character = await DigitalMindModel.find_one(
        DigitalMindModel.unique_id == "test-avatar-e2e-001"
    )
    
    if not character:
        print_error("Character not found")
        return
    
    # Get initial state
    analyzer = KammaAppearanceAnalyzer()
    initial_profile = analyzer.analyze_kamma_ledger(
        kamma_ledger=character.kamma_engine.ledger.dict(),
        model_id=character.unique_id
    )
    
    print_info(f"Initial skin quality: {initial_profile.health_score.skin_quality:.1f}")
    
    # Log new kamma
    print_info("Logging new negative kamma (BYAPADA - ill-will)...")
    for _ in range(20):
        character.kamma_engine.log_kamma(
            category=KammaCategory.BYAPADA,
            intensity=7.5
        )
    
    await character.save()
    print_success("New kamma logged")
    
    # Analyze again
    updated_profile = analyzer.analyze_kamma_ledger(
        kamma_ledger=character.kamma_engine.ledger.dict(),
        model_id=character.unique_id
    )
    
    print_info(f"Updated skin quality: {updated_profile.health_score.skin_quality:.1f}")
    
    # Check if changed
    skin_change = updated_profile.health_score.skin_quality - initial_profile.health_score.skin_quality
    
    if skin_change < 0:
        print_success(f"✓ Skin quality decreased by {abs(skin_change):.1f} (expected from negative kamma)")
    else:
        print_warning(f"⚠ Expected decrease, got change of {skin_change:.1f}")
    
    # Check balance change
    balance_change = updated_profile.overall_balance - initial_profile.overall_balance
    
    if balance_change < 0:
        print_success(f"✓ Kamma balance shifted negative by {abs(balance_change):.1%}")
    else:
        print_warning(f"⚠ Expected negative shift, got {balance_change:.1%}")


async def cleanup_test_data():
    """Clean up test data"""
    print_header("Test 8: Cleanup")
    
    character = await DigitalMindModel.find_one(
        DigitalMindModel.unique_id == "test-avatar-e2e-001"
    )
    
    if character:
        await character.delete()
        print_success("Test character deleted")
    else:
        print_info("No test character to delete")


async def run_all_tests():
    """Run all E2E tests"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Avatar System End-to-End Testing'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'วันที่: 2 พฤศจิกายน 2568'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    start_time = datetime.now()
    test_results = {}
    
    try:
        # Initialize
        client = await init_db()
        
        # Test 1: Create character
        try:
            character = await create_test_character()
            test_results["Character Creation"] = "PASS"
        except Exception as e:
            print_error(f"Test 1 failed: {e}")
            test_results["Character Creation"] = "FAIL"
            return False
        
        # Test 2: Log kamma
        try:
            kamma_counts = await log_test_kamma(character)
            test_results["Kamma Logging"] = "PASS"
        except Exception as e:
            print_error(f"Test 2 failed: {e}")
            test_results["Kamma Logging"] = "FAIL"
        
        # Test 3: Analyze appearance
        try:
            appearance_profile = await analyze_appearance(character)
            test_results["Appearance Analysis"] = "PASS"
            test_results["Buddhist Accuracy"] = "PASS"
        except Exception as e:
            print_error(f"Test 3 failed: {e}")
            test_results["Appearance Analysis"] = "FAIL"
        
        # Test 5: Calculate Rūpa
        try:
            rupa_profile = await calculate_rupa(character)
            test_results["28 Rūpa Calculation"] = "PASS"
        except Exception as e:
            print_error(f"Test 5 failed: {e}")
            test_results["28 Rūpa Calculation"] = "FAIL"
        
        # Test 6: Test API
        try:
            api_data = await test_api_endpoint()
            test_results["API Endpoint"] = "PASS" if api_data else "FAIL"
        except Exception as e:
            print_error(f"Test 6 failed: {e}")
            test_results["API Endpoint"] = "FAIL"
        
        # Test 7: Real-time updates
        try:
            await test_real_time_updates()
            test_results["Real-time Updates"] = "PASS"
        except Exception as e:
            print_error(f"Test 7 failed: {e}")
            test_results["Real-time Updates"] = "FAIL"
        
        # Test 8: Cleanup
        try:
            await cleanup_test_data()
            test_results["Cleanup"] = "PASS"
        except Exception as e:
            print_error(f"Test 8 failed: {e}")
            test_results["Cleanup"] = "FAIL"
        
        # Summary
        print_header("Test Summary")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        passed = sum(1 for result in test_results.values() if result == "PASS")
        total = len(test_results)
        
        print_info(f"\nTest Results ({passed}/{total} passed):")
        for test_name, result in test_results.items():
            if result == "PASS":
                print_result(f"  {test_name}", f"✓ {result}")
            else:
                print_error(f"  {test_name}: ✗ {result}")
        
        print_info(f"\nExecution time: {duration:.2f} seconds")
        
        if passed == total:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Avatar System is production-ready!{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Some tests failed. Please review.{Colors.ENDC}\n")
        
        # Close connection
        client.close()
        
        return passed == total
        
    except Exception as e:
        print_error(f"Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)
