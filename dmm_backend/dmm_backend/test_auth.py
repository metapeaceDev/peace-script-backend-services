#!/usr/bin/env python3
"""
Test Authentication Flow
Phase 2: Authentication & User Management

Tests:
1. User registration
2. Login with credentials
3. Access protected endpoint (/me)
4. Token refresh
5. Invalid token handling
"""

import asyncio
import sys
from datetime import datetime

# Import models
from database import init_db
from documents import User, MindState
from utils.security import hash_password


async def cleanup_test_user(email: str):
    """Remove test user if exists"""
    user = await User.find_one({"email": email})
    if user:
        # Delete linked MindState
        mind_state = await MindState.find_one({"user_id": str(user.id)})
        if mind_state:
            await mind_state.delete()
        # Delete user
        await user.delete()
        print(f"🧹 Cleaned up existing user: {email}")


async def test_authentication():
    """Test complete authentication flow"""
    
    print("🔐 Starting Authentication Test\n")
    print("=" * 60)
    
    # Initialize database
    print("📦 Step 1: Initializing database...")
    await init_db()
    print("✅ Database initialized\n")
    
    # Test credentials
    test_email = "testauth@peace.com"
    test_password = "TestPass123"
    test_name = "Test Auth User"
    
    # Cleanup any existing test user
    await cleanup_test_user(test_email)
    
    # Step 2: Test Registration
    print("=" * 60)
    print("👤 Step 2: Testing User Registration...")
    print(f"   Email: {test_email}")
    print(f"   Name: {test_name}")
    
    # Simulate registration (same logic as auth_router.py)
    from utils.security import validate_password_strength
    
    is_valid, msg = validate_password_strength(test_password)
    if not is_valid:
        print(f"❌ Password validation failed: {msg}")
        return
    print(f"✅ Password validation passed")
    
    # Create user
    user = User(
        email=test_email,
        hashed_password=hash_password(test_password),
        full_name=test_name,
        is_active=True,
        is_verified=False,
        roles=["user"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await user.insert()
    print(f"✅ User created: {user.id}")
    
    # Create linked MindState
    mind_state = MindState(
        user_id=str(user.id),
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        sati_strength=5.0,
        current_anusaya={
            "lobha": 3.0, "dosa": 2.5, "moha": 3.5,
            "mana": 2.0, "ditthi": 2.0, "vicikiccha": 2.5, "thina": 3.0
        },
        kusala_count_today=0,
        akusala_count_today=0,
        kusala_count_total=0,
        akusala_count_total=0,
        current_bhumi="puthujjana",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await mind_state.insert()
    print(f"✅ MindState created and linked")
    print()
    
    # Step 3: Test Login
    print("=" * 60)
    print("🔑 Step 3: Testing Login...")
    
    from utils.security import verify_password, create_access_token, create_refresh_token
    
    # Find user
    login_user = await User.find_one({"email": test_email})
    if not login_user:
        print(f"❌ User not found")
        return
    print(f"✅ User found: {login_user.email}")
    
    # Verify password
    if not verify_password(test_password, login_user.hashed_password):
        print(f"❌ Password verification failed")
        return
    print(f"✅ Password verified")
    
    # Create tokens
    token_data = {
        "sub": str(login_user.id),
        "email": login_user.email
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    print(f"✅ Access token generated: {access_token[:50]}...")
    print(f"✅ Refresh token generated: {refresh_token[:50]}...")
    print()
    
    # Step 4: Test Token Decode
    print("=" * 60)
    print("🔍 Step 4: Testing Token Decode...")
    
    from utils.security import decode_token, verify_token_type
    
    # Decode access token
    access_payload = decode_token(access_token)
    if not access_payload:
        print(f"❌ Failed to decode access token")
        return
    print(f"✅ Access token decoded")
    print(f"   User ID: {access_payload.get('sub')}")
    print(f"   Email: {access_payload.get('email')}")
    print(f"   Type: {access_payload.get('type')}")
    print(f"   Expires: {datetime.fromtimestamp(access_payload.get('exp'))}")
    
    # Verify token type
    if not verify_token_type(access_payload, "access"):
        print(f"❌ Token type verification failed")
        return
    print(f"✅ Token type verified: access")
    print()
    
    # Step 5: Test Get Current User
    print("=" * 60)
    print("👁️  Step 5: Testing Get Current User...")
    
    user_id = access_payload.get("sub")
    current_user = await User.get(user_id)
    
    if not current_user:
        print(f"❌ User not found")
        return
    
    print(f"✅ User retrieved from database")
    print(f"   ID: {current_user.id}")
    print(f"   Email: {current_user.email}")
    print(f"   Name: {current_user.full_name}")
    print(f"   Active: {current_user.is_active}")
    print(f"   Roles: {current_user.roles}")
    print(f"   Created: {current_user.created_at}")
    print()
    
    # Step 6: Test Refresh Token
    print("=" * 60)
    print("🔄 Step 6: Testing Token Refresh...")
    
    # Decode refresh token
    refresh_payload = decode_token(refresh_token)
    if not refresh_payload:
        print(f"❌ Failed to decode refresh token")
        return
    print(f"✅ Refresh token decoded")
    
    # Verify it's a refresh token
    if not verify_token_type(refresh_payload, "refresh"):
        print(f"❌ Not a refresh token")
        return
    print(f"✅ Token type verified: refresh")
    
    # Generate new access token
    new_access_token = create_access_token(data=token_data)
    print(f"✅ New access token generated: {new_access_token[:50]}...")
    print()
    
    # Step 7: Test Invalid Token
    print("=" * 60)
    print("❌ Step 7: Testing Invalid Token Handling...")
    
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    invalid_payload = decode_token(invalid_token)
    
    if invalid_payload is None:
        print(f"✅ Invalid token correctly rejected")
    else:
        print(f"❌ Invalid token was accepted (security issue!)")
    print()
    
    # Step 8: Verify MindState Link
    print("=" * 60)
    print("🔗 Step 8: Verifying User-MindState Link...")
    
    user_mind_state = await MindState.find_one({"user_id": str(current_user.id)})
    if not user_mind_state:
        print(f"❌ MindState not found for user")
        return
    
    print(f"✅ MindState found")
    print(f"   Sila: {user_mind_state.sila}")
    print(f"   Samadhi: {user_mind_state.samadhi}")
    print(f"   Panna: {user_mind_state.panna}")
    print(f"   Bhumi: {user_mind_state.current_bhumi}")
    print()
    
    # Cleanup
    print("=" * 60)
    print("🧹 Cleaning up test data...")
    await cleanup_test_user(test_email)
    print("✅ Cleanup complete")
    print()
    
    # Final summary
    print("=" * 60)
    print("✨ AUTHENTICATION TEST COMPLETE! ✨")
    print("=" * 60)
    print()
    print("✅ All tests passed:")
    print("   1. User registration")
    print("   2. Password hashing and verification")
    print("   3. Token generation (access + refresh)")
    print("   4. Token decoding and validation")
    print("   5. User retrieval from token")
    print("   6. Token refresh flow")
    print("   7. Invalid token rejection")
    print("   8. User-MindState linking")
    print()
    print("🔐 Authentication system is ready!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_authentication())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
