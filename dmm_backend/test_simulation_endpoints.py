#!/usr/bin/env python3
"""
Test script for Interactive Simulation API endpoints
Tests all 5 endpoints and reports results
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

async def test_endpoint(client: httpx.AsyncClient, method: str, url: str, data: Dict = None) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    try:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "error": response.text if response.status_code != 200 else None
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "data": None,
            "error": str(e)
        }

async def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Interactive Simulation API Testing ==={Colors.ENDC}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = {}
        
        # Test 1: Health Check
        print(f"{Colors.BOLD}Test 1: Health Check{Colors.ENDC}")
        print(f"GET {BASE_URL}/api/simulation/health")
        results['health'] = await test_endpoint(client, "GET", f"{BASE_URL}/api/simulation/health")
        
        if results['health']['success']:
            print(f"{Colors.GREEN}✅ PASS{Colors.ENDC}")
            print(json.dumps(results['health']['data'], indent=2, ensure_ascii=False))
        else:
            print(f"{Colors.RED}❌ FAIL - Status: {results['health']['status_code']}{Colors.ENDC}")
            print(f"Error: {results['health']['error']}")
        print()
        
        # Test 2: List Scenarios
        print(f"{Colors.BOLD}Test 2: List Scenarios{Colors.ENDC}")
        print(f"GET {BASE_URL}/api/simulation/scenarios")
        results['list'] = await test_endpoint(client, "GET", f"{BASE_URL}/api/simulation/scenarios")
        
        if results['list']['success']:
            print(f"{Colors.GREEN}✅ PASS{Colors.ENDC}")
            data = results['list']['data']
            print(f"Total scenarios: {data['total']}")
            print(f"Categories: {data['categories']}")
            for scenario in data['scenarios']:
                print(f"  - [{scenario['category']}] {scenario['title']} (ID: {scenario['scenario_id']}, Difficulty: {scenario['difficulty']})")
        else:
            print(f"{Colors.RED}❌ FAIL - Status: {results['list']['status_code']}{Colors.ENDC}")
            print(f"Error: {results['list']['error']}")
        print()
        
        # Test 3: Scenario Detail
        print(f"{Colors.BOLD}Test 3: Scenario Detail{Colors.ENDC}")
        scenario_id = "marketplace_expensive"
        print(f"GET {BASE_URL}/api/simulation/scenarios/{scenario_id}")
        results['detail'] = await test_endpoint(client, "GET", f"{BASE_URL}/api/simulation/scenarios/{scenario_id}")
        
        if results['detail']['success']:
            print(f"{Colors.GREEN}✅ PASS{Colors.ENDC}")
            data = results['detail']['data']
            print(f"Title: {data['title']}")
            print(f"Category: {data['category']}")
            print(f"Difficulty: {data['difficulty']}/10")
            print(f"Sensory Input: {data['sensory_input']['dvara']} -> {data['sensory_input']['vedana']}")
            print(f"Choices: {len(data['choices'])}")
            for i, choice in enumerate(data['choices']):
                print(f"  {i+1}. [{choice['choice_type']}] {choice['title']}")
        else:
            print(f"{Colors.RED}❌ FAIL - Status: {results['detail']['status_code']}{Colors.ENDC}")
            print(f"Error: {results['detail']['error']}")
        print()
        
        # Test 4: Run Simulation (only if detail passed)
        if results['detail']['success']:
            print(f"{Colors.BOLD}Test 4: Run Simulation{Colors.ENDC}")
            simulation_request = {
                "scenario_id": "marketplace_expensive",
                "choice_index": 0,
                "user_id": "test_user_001",
                "reflection": "Testing first kusala choice"
            }
            print(f"POST {BASE_URL}/api/simulation/simulate")
            print(f"Request: {json.dumps(simulation_request, ensure_ascii=False)}")
            results['simulate'] = await test_endpoint(client, "POST", f"{BASE_URL}/api/simulation/simulate", simulation_request)
            
            if results['simulate']['success']:
                print(f"{Colors.GREEN}✅ PASS{Colors.ENDC}")
                data = results['simulate']['data']
                print(f"Simulation ID: {data['simulation_id']}")
                print(f"Chosen Option: {data['chosen_option']['title']} ({data['chosen_option']['type']})")
                print(f"Citta Result: {data['citta_result']['javana_citta']}")
                print(f"Immediate: {data['immediate_consequences']['description']}")
                print(f"Wisdom: {data['learning']['wisdom']}")
            else:
                print(f"{Colors.RED}❌ FAIL - Status: {results['simulate']['status_code']}{Colors.ENDC}")
                print(f"Error: {results['simulate']['error']}")
        else:
            print(f"{Colors.YELLOW}⏩ SKIP - Test 4 (Simulation) - Blocked by failed detail test{Colors.ENDC}")
            results['simulate'] = {"success": False, "skipped": True}
        print()
        
        # Test 5: User Progress
        print(f"{Colors.BOLD}Test 5: User Progress{Colors.ENDC}")
        user_id = "test_user_001"
        print(f"GET {BASE_URL}/api/simulation/progress/{user_id}")
        results['progress'] = await test_endpoint(client, "GET", f"{BASE_URL}/api/simulation/progress/{user_id}")
        
        if results['progress']['success']:
            print(f"{Colors.GREEN}✅ PASS{Colors.ENDC}")
            data = results['progress']['data']
            print(f"User ID: {data['user_id']}")
            print(f"Total Simulations: {data['total_simulations']}")
            print(f"Kusala: {data['kusala_choices']} | Akusala: {data['akusala_choices']} | Neutral: {data['neutral_choices']}")
            print(f"Current Streak: {data['current_streak']} days")
        else:
            print(f"{Colors.RED}❌ FAIL - Status: {results['progress']['status_code']}{Colors.ENDC}")
            print(f"Error: {results['progress']['error']}")
        print()
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.BLUE}=== Test Summary ==={Colors.ENDC}")
        passed = sum(1 for r in results.values() if r['success'])
        total = len(results)
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {failed}{Colors.ENDC}")
        print(f"Success Rate: {(passed/total)*100:.1f}%\n")
        
        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Ready for UI testing.{Colors.ENDC}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ {failed} test(s) failed. Fix issues before UI testing.{Colors.ENDC}")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())
