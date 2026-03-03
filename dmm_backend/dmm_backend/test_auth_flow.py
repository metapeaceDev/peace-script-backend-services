#!/usr/bin/env python3
"""
Authentication Flow Testing Script
Tests the complete authentication flow: register → login → access protected endpoint
"""

import asyncio
import sys
from httpx import AsyncClient, ASGITransport
from main import app
import json


async def test_complete_auth_flow():
    """Test complete authentication flow"""
    
    print("=" * 70)
    print("🧪 AUTHENTICATION FLOW TEST")
    print("=" * 70)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        
        # ============================================================================
        # STEP 1: Register a new user
        # ============================================================================
        print("\n📝 STEP 1: User Registration")
        print("-" * 70)
        
        register_data = {
            "email": f"flowtest-{asyncio.get_event_loop().time()}@peacescript.com",
            "password": "TestFlow2024!",
            "display_name": "Flow Test User",
            "preferred_language": "th"
        }
        
        print(f"📤 POST /auth/register")
        print(f"   Email: {register_data['email']}")
        
        try:
            response = await client.post("/auth/register", json=register_data)
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                user_data = response.json()
                print(f"✅ Registration SUCCESS")
                print(f"   User ID: {user_data['id']}")
                print(f"   Email: {user_data['email']}")
                print(f"   Display Name: {user_data['display_name']}")
                print(f"   Active: {user_data['is_active']}")
                print(f"   Verified: {user_data['is_verified']}")
            else:
                print(f"❌ Registration FAILED")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration ERROR: {e}")
            return False
        
        # ============================================================================
        # STEP 2: Login to get JWT token
        # ============================================================================
        print("\n🔐 STEP 2: User Login (Get JWT Token)")
        print("-" * 70)
        
        login_data = {
            "username": register_data['email'],
            "password": register_data['password']
        }
        
        print(f"📤 POST /auth/jwt/login")
        print(f"   Username: {login_data['username']}")
        
        try:
            response = await client.post(
                "/auth/jwt/login",
                data=login_data,  # form-urlencoded
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ Login SUCCESS")
                print(f"   Token Type: {token_data.get('token_type', 'N/A')}")
                print(f"   Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
                
                access_token = token_data.get('access_token')
                if not access_token:
                    print(f"❌ No access_token in response!")
                    return False
            else:
                print(f"❌ Login FAILED")
                print(f"   Response: {response.text}")
                print(f"   Headers: {dict(response.headers)}")
                return False
        except Exception as e:
            print(f"❌ Login ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # ============================================================================
        # STEP 3: Access protected endpoint (/users/me)
        # ============================================================================
        print("\n👤 STEP 3: Access Protected Endpoint (/users/me)")
        print("-" * 70)
        
        print(f"📤 GET /users/me")
        print(f"   Authorization: Bearer {access_token[:30]}...")
        
        try:
            response = await client.get(
                "/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                me_data = response.json()
                print(f"✅ Protected Endpoint SUCCESS")
                print(f"   User ID: {me_data['id']}")
                print(f"   Email: {me_data['email']}")
                print(f"   Display Name: {me_data['display_name']}")
                print(f"   Preferred Language: {me_data['preferred_language']}")
            else:
                print(f"❌ Protected Endpoint FAILED")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Protected Endpoint ERROR: {e}")
            return False
        
        # ============================================================================
        # STEP 4: Test without token (should fail)
        # ============================================================================
        print("\n🚫 STEP 4: Access Protected Endpoint WITHOUT Token (Should Fail)")
        print("-" * 70)
        
        try:
            response = await client.get("/users/me")
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 401:
                print(f"✅ Correctly REJECTED (401 Unauthorized)")
            else:
                print(f"❌ Should have returned 401, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        
        # ============================================================================
        # SUMMARY
        # ============================================================================
        print("\n" + "=" * 70)
        print("✅ ALL AUTHENTICATION TESTS PASSED!")
        print("=" * 70)
        print("\n📋 Summary:")
        print("  ✅ User Registration: Working")
        print("  ✅ User Login (JWT): Working")
        print("  ✅ Protected Endpoint Access: Working")
        print("  ✅ Authentication Required: Working")
        print("\n🎉 Phase 2 Authentication System is FULLY FUNCTIONAL!")
        print("=" * 70)
        
        return True


async def diagnose_login_issue():
    """Diagnose why login might be failing"""
    
    print("\n" + "=" * 70)
    print("🔍 LOGIN DIAGNOSTIC TEST")
    print("=" * 70)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        
        # Test 1: Check if /auth/jwt/login endpoint exists
        print("\n1️⃣ Checking if login endpoint exists...")
        try:
            response = await client.post("/auth/jwt/login", data={})
            print(f"   Status: {response.status_code}")
            if response.status_code == 422:  # Validation error (expected)
                print(f"   ✅ Endpoint EXISTS (validation error is normal)")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Test 2: Try to login with existing user
        print("\n2️⃣ Testing login with recently registered user...")
        print("   Email: fixed-test@peacescript.com")
        
        try:
            response = await client.post(
                "/auth/jwt/login",
                data={
                    "username": "fixed-test@peacescript.com",
                    "password": "FixedPass2024!"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ LOGIN SUCCESSFUL!")
                token_data = response.json()
                print(f"   Token: {token_data.get('access_token', 'N/A')[:50]}...")
            elif response.status_code == 400:
                error_data = response.json()
                print(f"   ❌ Login Failed: {error_data}")
                print(f"   Possible causes:")
                print(f"      - Wrong password")
                print(f"      - User not found")
                print(f"      - Email not verified (if verification required)")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Check User model in database
        print("\n3️⃣ Checking User in database...")
        try:
            from auth.models import User
            user = await User.find_one(User.email == "fixed-test@peacescript.com")
            
            if user:
                print(f"   ✅ User FOUND in database")
                print(f"      ID: {user.id}")
                print(f"      Email: {user.email}")
                print(f"      Active: {user.is_active}")
                print(f"      Verified: {user.is_verified}")
                print(f"      Has password: {bool(user.hashed_password)}")
                print(f"      Password hash: {user.hashed_password[:50]}...")
            else:
                print(f"   ❌ User NOT FOUND in database")
        except Exception as e:
            print(f"   ❌ ERROR checking database: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main test function"""
    
    print("\n🚀 Starting Authentication System Tests...")
    print(f"⏰ Time: {asyncio.get_event_loop().time()}")
    
    # First, run diagnostic
    await diagnose_login_issue()
    
    # Then run complete flow test
    print("\n" + "=" * 70)
    input("Press ENTER to continue with full authentication flow test...")
    
    success = await test_complete_auth_flow()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
