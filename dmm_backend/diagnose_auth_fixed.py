#!/usr/bin/env python3
import asyncio

async def main():
    print("🔍 AUTHENTICATION DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Imports
    print("\n[1] Testing imports...")
    try:
        from auth.models import User
        from auth.manager import get_user_manager
        from auth.config import auth_backend
        print("  ✅ Auth modules OK")
    except Exception as e:
        print(f"  ❌ {e}")
        return
    
    # 2. Database
    print("\n[2] Checking database...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "digital_mind_model")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        users = await db.users.find({}, {"email": 1, "hashed_password": 1}).to_list(10)
        print(f"  ✅ Found {len(users)} users")
        
        for user in users:
            has_pwd = bool(user.get("hashed_password"))
            email = user.get("email", "NO EMAIL")
            print(f"    - {email}: Password={'✅' if has_pwd else '❌'}")
        
        await client.close()
    except Exception as e:
        print(f"  ❌ {e}")
        return
    
    # 3. Password hashing
    print("\n[3] Testing password hashing...")
    try:
        from passlib.context import CryptContext
        
        ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
        test_pw = "SecurePass2024!"
        hashed = ctx.hash(test_pw)
        valid = ctx.verify(test_pw, hashed)
        
        print(f"  ✅ Hashing works: {valid}")
    except Exception as e:
        print(f"  ❌ {e}")
    
    # 4. Test specific user
    print("\n[4] Testing phase2test user...")
    try:
        from beanie import init_beanie
        from motor.motor_asyncio import AsyncIOMotorClient
        from documents import get_document_models
        import os
        
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "digital_mind_model")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        await init_beanie(database=db, document_models=get_document_models())
        
        user = await User.find_one(User.email == "phase2test@peacescript.com")
        
        if user:
            print(f"  ✅ User found: {user.email}")
            print(f"    - ID: {user.id}")
            print(f"    - Active: {user.is_active}")
            
            from passlib.context import CryptContext
            ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            is_valid = ctx.verify("SecurePass2024!", user.hashed_password)
            print(f"    - Password correct: {is_valid}")
            
            if not is_valid:
                print("\n  ⚠️  PASSWORD MISMATCH DETECTED!")
                print("  This means FastAPI-Users didn't hash the password")
                print("  during registration")
        else:
            print("  ❌ User not found")
        
        await client.close()
    except Exception as e:
        print(f"  ❌ {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
