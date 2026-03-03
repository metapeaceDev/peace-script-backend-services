#!/usr/bin/env python3
"""
Populate Character Data Script
===============================
สคริปต์สำหรับเพิ่มข้อมูลตัวละครลงในฐานข้อมูล

Usage:
    python populate_character_data.py

This will update the existing actor with complete character data including:
- first_name, last_name, nickname
- buddhist_type, spiritual_level
- weight (for external_character)
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings

# Load settings
settings = Settings()
MONGODB_URL = settings.MONGO_URI or settings.MONGODB_URI or "mongodb://localhost:27017"
DATABASE_NAME = settings.MONGO_DB_NAME or settings.MONGODB_DB or "digital_mind_model"


async def populate_character_data():
    """Populate character data for existing actor"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    actors_collection = db['actors']
    
    # Actor ID to update
    actor_id = "ACT-20251110-23340B"
    
    print(f"🔍 Looking for actor: {actor_id}")
    
    # Find the actor
    actor = await actors_collection.find_one({"actor_id": actor_id})
    
    if not actor:
        print(f"❌ Actor {actor_id} not found!")
        client.close()
        return
    
    print(f"✅ Found actor: {actor.get('actor_name', 'Unknown')}")
    print(f"   Model ID: {actor.get('model_id')}")
    
    # Prepare update data
    update_data = {}
    
    # 1. Update internal_character with name and Buddhist data
    internal_character = actor.get('internal_character', {})
    
    # Character name data
    internal_character['first_name'] = 'สันติ'  # ชื่อจริง
    internal_character['last_name'] = 'ธรรมสาร'  # นามสกุล
    internal_character['nickname'] = 'พีซ'  # ชื่อเล่น
    
    # Buddhist spiritual data
    internal_character['buddhist_type'] = 'puthujjana'  # ปุถุชน
    internal_character['spiritual_level'] = 3  # ระดับจิตวิญญาณ (1-10)
    
    # Additional spiritual data (optional)
    internal_character['meditation_experience'] = 'beginner'  # ผู้เริ่มต้น
    internal_character['dhamma_knowledge'] = 'intermediate'  # ความรู้ธรรมะระดับกลาง
    
    update_data['internal_character'] = internal_character
    
    # 2. Update external_character with weight
    external_character = actor.get('external_character', {})
    
    if external_character.get('height'):
        # Calculate appropriate weight based on height (if needed)
        height = external_character.get('height', 175)
        # Using BMI ~22 as healthy baseline
        estimated_weight = (height / 100) ** 2 * 22
        external_character['weight'] = round(estimated_weight, 1)
    else:
        external_character['weight'] = 65.0  # Default weight
    
    update_data['external_character'] = external_character
    
    # 3. Perform update
    print("\n📝 Updating actor with new data:")
    print(f"   First Name: {internal_character['first_name']}")
    print(f"   Last Name: {internal_character['last_name']}")
    print(f"   Nickname: {internal_character['nickname']}")
    print(f"   Buddhist Type: {internal_character['buddhist_type']}")
    print(f"   Spiritual Level: {internal_character['spiritual_level']}")
    print(f"   Weight: {external_character['weight']} kg")
    
    result = await actors_collection.update_one(
        {"actor_id": actor_id},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        print(f"\n✅ Successfully updated {result.modified_count} document(s)")
        
        # Verify the update
        updated_actor = await actors_collection.find_one({"actor_id": actor_id})
        
        print("\n🔍 Verification:")
        ic = updated_actor.get('internal_character', {})
        ec = updated_actor.get('external_character', {})
        
        print(f"   ✓ First Name: {ic.get('first_name')}")
        print(f"   ✓ Last Name: {ic.get('last_name')}")
        print(f"   ✓ Nickname: {ic.get('nickname')}")
        print(f"   ✓ Buddhist Type: {ic.get('buddhist_type')}")
        print(f"   ✓ Spiritual Level: {ic.get('spiritual_level')}")
        print(f"   ✓ Weight: {ec.get('weight')} kg")
        print(f"   ✓ Height: {ec.get('height')} cm")
        print(f"   ✓ Age: {ec.get('age')} years")
        print(f"   ✓ Gender: {ec.get('gender')}")
    else:
        print("\n⚠️  No documents were modified (data might be the same)")
    
    client.close()
    print("\n✅ Done!")


async def populate_custom_data(
    actor_id: str,
    first_name: str = None,
    last_name: str = None,
    nickname: str = None,
    buddhist_type: str = None,
    spiritual_level: int = None,
    weight: float = None
):
    """Populate custom character data
    
    Args:
        actor_id: Actor ID to update
        first_name: ชื่อจริง
        last_name: นามสกุล
        nickname: ชื่อเล่น
        buddhist_type: puthujjana, sekha, asekha
        spiritual_level: 1-10
        weight: น้ำหนัก (kg)
    """
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    actors_collection = db['actors']
    
    actor = await actors_collection.find_one({"actor_id": actor_id})
    
    if not actor:
        print(f"❌ Actor {actor_id} not found!")
        client.close()
        return
    
    update_data = {}
    
    # Update internal_character
    if any([first_name, last_name, nickname, buddhist_type, spiritual_level]):
        internal_character = actor.get('internal_character', {})
        
        if first_name:
            internal_character['first_name'] = first_name
        if last_name:
            internal_character['last_name'] = last_name
        if nickname:
            internal_character['nickname'] = nickname
        if buddhist_type:
            internal_character['buddhist_type'] = buddhist_type
        if spiritual_level:
            internal_character['spiritual_level'] = spiritual_level
        
        update_data['internal_character'] = internal_character
    
    # Update external_character
    if weight:
        external_character = actor.get('external_character', {})
        external_character['weight'] = weight
        update_data['external_character'] = external_character
    
    if update_data:
        result = await actors_collection.update_one(
            {"actor_id": actor_id},
            {"$set": update_data}
        )
        
        print(f"✅ Updated {result.modified_count} document(s)")
    
    client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate character data')
    parser.add_argument('--actor-id', default='ACT-20251110-23340B', help='Actor ID to update')
    parser.add_argument('--first-name', help='First name (ชื่อจริง)')
    parser.add_argument('--last-name', help='Last name (นามสกุล)')
    parser.add_argument('--nickname', help='Nickname (ชื่อเล่น)')
    parser.add_argument('--buddhist-type', choices=['puthujjana', 'sekha', 'asekha'], 
                       help='Buddhist type')
    parser.add_argument('--spiritual-level', type=int, choices=range(1, 11), 
                       help='Spiritual level (1-10)')
    parser.add_argument('--weight', type=float, help='Weight in kg')
    
    args = parser.parse_args()
    
    # If custom arguments provided, use populate_custom_data
    if any([args.first_name, args.last_name, args.nickname, 
            args.buddhist_type, args.spiritual_level, args.weight]):
        asyncio.run(populate_custom_data(
            actor_id=args.actor_id,
            first_name=args.first_name,
            last_name=args.last_name,
            nickname=args.nickname,
            buddhist_type=args.buddhist_type,
            spiritual_level=args.spiritual_level,
            weight=args.weight
        ))
    else:
        # Otherwise use default data
        asyncio.run(populate_character_data())
