#!/usr/bin/env python3
"""
Test script for authentication rate limiting
Tests login and register rate limits
"""

import requests
import time
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(attempt, response):
    """Print test result"""
    status = response.status_code
    headers = dict(response.headers)
    
    # Extract rate limit headers
    limit = headers.get('x-ratelimit-limit', 'N/A')
    remaining = headers.get('x-ratelimit-remaining', 'N/A')
    reset = headers.get('x-ratelimit-reset', 'N/A')
    retry_after = headers.get('retry-after', 'N/A')
    
    print(f"\n📊 Attempt #{attempt}:")
    print(f"   Status: {status}")
    print(f"   Rate Limit: {remaining}/{limit}")
    print(f"   Reset: {reset}")
    
    if status == 429:
        print(f"   🚫 RATE LIMITED - Retry After: {retry_after}s")
        try:
            data = response.json()
            print(f"   Message: {data.get('detail', {}).get('message', 'N/A')}")
        except:
            pass
    elif status < 400:
        print(f"   ✅ SUCCESS")
    else:
        print(f"   ❌ ERROR")
        try:
            print(f"   Detail: {response.json()}")
        except:
            pass

def test_login_rate_limit():
    """Test login rate limit: 5 attempts per minute"""
    print_header("TEST 1: Login Rate Limit (5 per minute)")
    
    login_data = {
        "username": "ratelimit-test@peace.com",
        "password": "WrongPassword123"
    }
    
    print(f"\nTesting with: {login_data['username']}")
    print("Rate Limit Config: 5 attempts per 60 seconds")
    
    for i in range(7):  # Try 7 times, should block after 5
        time.sleep(0.5)  # Small delay between requests
        
        response = requests.post(
            f"{API_BASE}/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print_result(i + 1, response)
        
        if response.status_code == 429:
            print("\n✅ Rate limiting working correctly!")
            return True
    
    print("\n❌ Rate limiting not triggered after 7 attempts!")
    return False

def test_register_rate_limit():
    """Test register rate limit: 3 attempts per hour"""
    print_header("TEST 2: Register Rate Limit (3 per hour)")
    
    print("\nTesting register endpoint")
    print("Rate Limit Config: 3 attempts per 3600 seconds")
    
    for i in range(5):  # Try 5 times, should block after 3
        time.sleep(0.5)
        
        # Use unique email each time
        register_data = {
            "email": f"ratelimit-{int(time.time())}-{i}@peace.com",
            "password": "TestPassword123",
            "display_name": f"Rate Test {i}"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_data
        )
        
        print_result(i + 1, response)
        
        if response.status_code == 429:
            print("\n✅ Rate limiting working correctly!")
            return True
    
    print("\n❌ Rate limiting not triggered after 5 attempts!")
    return False

def test_rate_limit_headers():
    """Test that rate limit headers are present"""
    print_header("TEST 3: Rate Limit Headers")
    
    response = requests.post(
        f"{API_BASE}/auth/jwt/login",
        data={"username": "test@peace.com", "password": "test"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    headers = dict(response.headers)
    required_headers = [
        'x-ratelimit-limit',
        'x-ratelimit-remaining',
        'x-ratelimit-reset'
    ]
    
    print("\nChecking for rate limit headers:")
    all_present = True
    for header in required_headers:
        value = headers.get(header, None)
        if value:
            print(f"   ✅ {header}: {value}")
        else:
            print(f"   ❌ {header}: MISSING")
            all_present = False
    
    return all_present

def main():
    print("\n" + "🔒" * 30)
    print("  AUTHENTICATION RATE LIMIT TEST SUITE")
    print("🔒" * 30)
    print(f"\nAPI Base: {API_BASE}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        print(f"✅ Backend is running (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        print("\n⚠️  Please start the backend server first:")
        print("   cd dmm_backend && ./venv/bin/uvicorn main:app")
        return
    
    results = {
        "Login Rate Limit": test_login_rate_limit(),
        "Register Rate Limit": test_register_rate_limit(),
        "Rate Limit Headers": test_rate_limit_headers()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\n📊 Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Rate limiting is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
