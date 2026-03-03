#!/usr/bin/env python3
"""
🎨 Update Actor Avatars - Add placeholder avatars to all actors without avatars

This script updates all ActorProfile documents that don't have avatar_thumbnail_url
with a placeholder avatar from UI Avatars API.

Usage:
    python update_actor_avatars.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus


async def update_actor_avatars():
    """Update all actors without avatars with placeholder avatars"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['digital_mind_model']
    actors_collection = db['actor_profiles']
    
    print("🎨 Updating Actor Avatars...")
    print("=" * 60)
    
    # Find actors without avatars
    query = {
        '$or': [
            {'avatar_thumbnail_url': None},
            {'avatar_thumbnail_url': ''},
            {'avatar_thumbnail_url': {'$exists': False}}
        ]
    }
    
    actors_without_avatar = await actors_collection.count_documents(query)
    print(f"\n📊 Found {actors_without_avatar} actors without avatars")
    
    if actors_without_avatar == 0:
        print("✅ All actors already have avatars!")
        return
    
    # Update each actor
    updated_count = 0
    skipped_count = 0
    
    cursor = actors_collection.find(query)
    
    async for actor in cursor:
        actor_id = actor.get('actor_id', 'Unknown')
        actor_name = actor.get('actor_name', 'Actor')
        
        # Generate placeholder avatar URL
        name_encoded = quote_plus(actor_name)
        placeholder_url = f"https://ui-avatars.com/api/?name={name_encoded}&size=512&background=random&color=fff&bold=true"
        
        try:
            # Update the actor
            result = await actors_collection.update_one(
                {'_id': actor['_id']},
                {
                    '$set': {
                        'avatar_thumbnail_url': placeholder_url,
                        'updated_at': None  # Will be set by application
                    }
                }
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"✅ Updated: {actor_name} ({actor_id})")
                print(f"   Avatar: {placeholder_url}")
            else:
                skipped_count += 1
                print(f"⚠️  Skipped: {actor_name} ({actor_id})")
                
        except Exception as e:
            print(f"❌ Error updating {actor_name}: {e}")
            skipped_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Update Complete!")
    print(f"   ✅ Updated: {updated_count} actors")
    print(f"   ⚠️  Skipped: {skipped_count} actors")
    print(f"   📊 Total: {actors_without_avatar} actors processed")
    print("=" * 60)
    
    # Verify the update
    remaining = await actors_collection.count_documents(query)
    print(f"\n✨ Verification:")
    print(f"   Actors still without avatars: {remaining}")
    
    if remaining == 0:
        print("   🎊 All actors now have avatars!")
    else:
        print(f"   ⚠️  {remaining} actors still need avatars")


if __name__ == "__main__":
    print("\n🚀 Starting Actor Avatar Update...")
    asyncio.run(update_actor_avatars())
    print("\n✅ Done!\n")
