#!/usr/bin/env python3
"""Phase 2 Authentication Diagnostic Tool"""
import asyncio
import sys

async def main():
    print("=" * 80)
    print("🔍 PHASE 2 AUTHENTICATION DIAGNOSTIC REPORT")
    print("=" * 80)
    
    # 1. Test imports
    print("\n[1] Testing Module Imports...")
    try:
        from auth.models import User
        from auth.manager import get_user_manager
        from auth.config import auth_backend, fastapi_users, current_active_user
        from auth.schemas import UserRead, UserCreate, UserUpdate
        print("  ✅ All auth modules import successfully")
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return
    
    # 2. Test database connection
    print("\n[2] Testing Database Connection...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from core.config import settings
        
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB_NAME]
        
        users_count = await db.users.count_documents({})
        print(f"  ✅ Database connected: {users_count} users in database")
        
        users = await db.users.find({}, {"email": 1, "_id": 1, "hashed_password": 1}).to_list(10)
        print(f"\n  📋 Existing users:")
        for user in users:
            has_password = "hashed_password" in user and user["hashed_password"]
            print(f"    - {user.get('email', 'NO EMAIL')} (ID: {user['_id']}) - Password: {'✅' if has_password else '❌'}")
        
        await client.close()
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return
    
    # 3. Test password hashing
    print("\n[3] Testing Password Hashing...")
    try:
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        test_password = "SecurePass2024!"
        hashed = pwd_context.hash(test_password)
        verified = pwd_context.verify(test_password, hashed)
        
        print(f"  ✅ Password hashing works: {verified}")
        print(f"  📝 Sample hash: {hashed[:60]}...")
    except Exception as e:
        print(f"  ❌ Password hashing error: {e}")
    
    # 4. Test FastAPI-Users configuration
    print("\n[4] Testing FastAPI-Users Configuration...")
    try:
        from auth.config import get_jwt_strategy
        
        strategy = get_jwt_strategy()
        print(f"  ✅ JWT Strategy configured")
        print(f"    - Token lifetime: {strategy.lifetime_seconds}s ({strategy.lifetime_seconds/3600}h)")
        print(f"  ✅ Auth backend: {auth_backend.name}")
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
    
    # 5. Test login simulation
    print("\n[5] Testing Login Flow (Simulation)...")
    try:
        from beanie import init_beanie
        from motor.motor_asyncio import AsyncIOMotorClient
        from core.config import settings
        from documents import get_document_models
        
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB_NAME]
        
        await init_beanie(database=db, document_models=get_document_models())
        
        test_email = "phase2test@peacescript.com"
        user = await User.find_one(User.email == test_email)
        
        if user:
            print(f"  ✅ Found user: {user.email}")
            print(f"    - ID: {user.id}")
            print(f"    - Active: {user.is_active}")
            print(f"    - Has password: {bool(user.hashed_password)}")
            
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            test_password = "SecurePass2024!"
            is_valid = pwd_context.verify(test_password, user.hashed_password)
            print(f"    - Password validates: {is_valid}")
            
            if not is_valid:
                print(f"\n  ⚠️  PASSWORD MISMATCH!")
        else:
            print(f"  ❌ User not found: {test_email}")
        
        await client.close()
        
    except Exception as e:
        print(f"  ❌ Login flow error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("📋 DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
