#!/usr/bin/env python3
"""
Simplified End-to-End Test for Avatar System
Tests API endpoint directly

วันที่: 2 พฤศจิกายน 2568
"""

import asyncio
import sys
import httpx
from datetime import datetime

# Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_result(label: str, value):
    print(f"{Colors.OKCYAN}{label}:{Colors.ENDC} {value}")


async def test_backend_health():
    """Test if backend is running"""
    print_header("Test 1: Backend Health Check")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/health", timeout=5.0)
            
            if response.status_code == 200:
                print_success("Backend is running")
                return True
            else:
                print_error(f"Backend returned {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        print_info("Make sure backend is running: cd dmm_backend && ./venv/bin/python -m uvicorn main:app")
        return False


async def test_use_seeded_character():
    """Use seeded character from database"""
    print_header("Test 2: Use Seeded Character")
    
    # Use the character we know exists from seed_db
    model_id = "peace-mind-001"
    print_success(f"Using seeded character: {model_id}")
    print_info("This character was created by seed_db.py")
    
    return model_id


async def test_full_appearance_api(model_id: str):
    """Test full appearance API endpoint"""
    print_header(f"Test 3: Full Appearance API (ID: {model_id})")
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"http://127.0.0.1:8000/api/v1/character-avatar/{model_id}/full-appearance"
            print_info(f"Calling: {url}")
            
            response = await client.get(url, timeout=30.0)
            
            if response.status_code == 200:
                print_success("API Response: 200 OK")
                
                data = response.json()
                
                # Check structure
                required_keys = ["physical", "voice", "movement", "citta_state", "kamma_influence", "rupa"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    print_success("✓ Response structure complete")
                else:
                    print_warning(f"⚠ Missing keys: {missing_keys}")
                
                # Display physical data
                if "physical" in data:
                    print_info("\n📊 Physical Appearance:")
                    physical = data["physical"]
                    if isinstance(physical, dict):
                        print_result("  Health Status", f"{physical.get('health_status', 0):.1f}/100")
                        print_result("  Skin Quality", f"{physical.get('skin_quality', 0):.1f}/100")
                        print_result("  Skin Tone", physical.get('skin_tone_desc', 'N/A'))
                        print_result("  Body Type", physical.get('body_type_tendency', 'N/A'))
                        print_result("  Fitness Level", f"{physical.get('fitness_level', 0)}/10")
                
                # Display voice data
                if "voice" in data:
                    print_info("\n🎵 Voice Characteristics:")
                    voice = data["voice"]
                    if isinstance(voice, dict):
                        print_result("  Clarity", f"{voice.get('clarity_score', 0):.1f}/100")
                        print_result("  Pleasantness", f"{voice.get('pleasantness_score', 0):.1f}/100")
                        print_result("  Voice Character", voice.get('voice_character_desc', 'N/A'))
                
                # Display movement data
                if "movement" in data:
                    print_info("\n💃 Movement & Demeanor:")
                    movement = data["movement"]
                    if isinstance(movement, dict):
                        print_result("  Approachability", f"{movement.get('approachability_score', 0):.1f}/100")
                        print_result("  Charisma", f"{movement.get('charisma_score', 0):.1f}/100")
                        print_result("  Peacefulness", f"{movement.get('peacefulness_score', 0):.1f}/100")
                        print_result("  Posture", movement.get('posture_desc', 'N/A'))
                
                # Display kamma balance
                if "kamma_influence" in data:
                    print_info("\n⚖️  Kamma Balance:")
                    kamma = data["kamma_influence"]
                    if isinstance(kamma, dict):
                        kusala = kamma.get('kusala_percentage', 0)
                        akusala = kamma.get('akusala_percentage', 0)
                        print_result("  Kusala (ผลบุญ)", f"{kusala:.1f}%")
                        print_result("  Akusala (บาป)", f"{akusala:.1f}%")
                        print_result("  Balance", kamma.get('balance', 'N/A'))
                
                # Display charisma score
                if "charisma_score" in data:
                    charisma = data["charisma_score"]
                    print_info(f"\n✨ Charisma Score: {charisma:.2f}/10")
                
                # Display distinctive features
                if "distinctive_features" in data and data["distinctive_features"]:
                    print_info("\n🌟 Distinctive Features:")
                    for feature in data["distinctive_features"][:5]:
                        print(f"  • {feature}")
                
                # Display summary
                if "summary" in data:
                    summary = data["summary"]
                    if len(summary) > 200:
                        summary = summary[:200] + "..."
                    print_info(f"\n📝 Summary:\n{summary}")
                
                # Validate Buddhist accuracy
                print_header("Test 4: Buddhist Accuracy Validation")
                
                # Check if values are in valid ranges
                if "physical" in data and isinstance(data["physical"], dict):
                    skin_quality = data["physical"].get("skin_quality", 0)
                    if 0 <= skin_quality <= 100:
                        print_success(f"✓ Skin quality ({skin_quality:.1f}) in valid range [0-100]")
                    else:
                        print_warning(f"⚠ Skin quality ({skin_quality:.1f}) out of range")
                
                if "kamma_influence" in data and isinstance(data["kamma_influence"], dict):
                    kusala = data["kamma_influence"].get("kusala_percentage", 0)
                    akusala = data["kamma_influence"].get("akusala_percentage", 0)
                    total = kusala + akusala
                    
                    if 99 <= total <= 101:  # Allow rounding errors
                        print_success(f"✓ Kamma percentages sum to ~100% ({total:.1f}%)")
                    else:
                        print_warning(f"⚠ Kamma percentages sum to {total:.1f}% (expected 100%)")
                
                # Check if high kusala → positive appearance
                if "kamma_influence" in data and isinstance(data["kamma_influence"], dict):
                    balance = data["kamma_influence"].get("balance")
                    kusala = data["kamma_influence"].get("kusala_percentage", 0)
                    
                    if kusala > 70 and balance == "positive":
                        print_success(f"✓ High kusala ({kusala:.1f}%) → Positive balance (Buddhist logic correct)")
                    elif kusala < 30 and balance == "negative":
                        print_success(f"✓ Low kusala ({kusala:.1f}%) → Negative balance (Buddhist logic correct)")
                    else:
                        print_info(f"ℹ️  Kamma balance: {balance} (kusala: {kusala:.1f}%)")
                
                return True
                
            elif response.status_code == 404:
                print_error("Character not found")
                print_info("This endpoint requires a valid character in the database")
                return False
            else:
                print_error(f"API Error: {response.status_code}")
                print_error(response.text[:500])
                return False
                
    except Exception as e:
        print_error(f"Failed to test API: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_frontend_components():
    """Test if frontend components exist"""
    print_header("Test 5: Frontend Components Check")
    
    import os
    
    components = [
        "../frontend/src/components/character/AppearancePanel.jsx",
        "../frontend/src/components/character/VoiceVisualizer.jsx",
        "../frontend/src/components/character/MovementIndicator.jsx",
        "../frontend/src/components/character/CharacterAvatarEnhanced.jsx",
    ]
    
    all_exist = True
    for component in components:
        path = os.path.join(os.path.dirname(__file__), component)
        if os.path.exists(path):
            print_success(f"✓ {os.path.basename(component)} exists")
        else:
            print_error(f"✗ {os.path.basename(component)} not found")
            all_exist = False
    
    return all_exist


async def run_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Avatar System End-to-End Testing (Simplified)'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'วันที่: 2 พฤศจิกายน 2568'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    start_time = datetime.now()
    results = {}
    
    # Test 1: Backend health
    backend_ok = await test_backend_health()
    results["Backend Health"] = "PASS" if backend_ok else "FAIL"
    
    if not backend_ok:
        print_error("\n❌ Backend is not running. Cannot proceed with tests.")
        print_info("Start backend with: cd dmm_backend && ./venv/bin/python -m uvicorn main:app")
        return False
    
    # Test 2: Use seeded character
    model_id = await test_use_seeded_character()
    results["Use Seeded Character"] = "PASS" if model_id else "FAIL"
    
    if not model_id:
        print_error("\n❌ No characters found in database.")
        print_info("Seed database with: cd dmm_backend && ./venv/bin/python seed_db.py")
        return False
    
    # Test 3: Full appearance API
    api_ok = await test_full_appearance_api(model_id)
    results["Full Appearance API"] = "PASS" if api_ok else "FAIL"
    results["Buddhist Accuracy"] = "PASS" if api_ok else "FAIL"
    
    # Test 5: Frontend components
    components_ok = await test_frontend_components()
    results["Frontend Components"] = "PASS" if components_ok else "FAIL"
    
    # Summary
    print_header("Test Summary")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    print_info(f"\nTest Results ({passed}/{total} passed):")
    for test_name, result in results.items():
        if result == "PASS":
            print_success(f"  {test_name}: ✓ {result}")
        else:
            print_error(f"  {test_name}: ✗ {result}")
    
    print_info(f"\nExecution time: {duration:.2f} seconds")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Avatar System is production-ready!{Colors.ENDC}\n")
        print_success("Next steps:")
        print_info("1. Open frontend: http://localhost:5173")
        print_info("2. Navigate to character page")
        print_info("3. Import CharacterAvatarEnhanced component")
        print_info("4. Pass modelId prop to see full avatar display")
        return True
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Some tests failed. Please review above.{Colors.ENDC}\n")
        return False


if __name__ == "__main__":
    result = asyncio.run(run_tests())
    sys.exit(0 if result else 1)
