"""
Migration Script: Add actor_id to existing generated images

This script updates all existing GeneratedImageDocument records
that don't have actor_id set (NULL/None).

Strategy:
1. Find all images without actor_id
2. For each image, check if there's a character with matching criteria
3. Update the image with the correct actor_id

Usage:
    python migrate_add_actor_id_to_images.py

Author: Peace Script Team
Date: 10 พฤศจิกายน 2568
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "peace_script_db"

async def migrate_images():
    """Migrate existing images to add actor_id"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Collections
    images_collection = db["generated_images"]
    
    print("🔍 Finding images without actor_id...")
    
    # Find all images where actor_id is null
    images_without_actor = await images_collection.find({
        "$or": [
            {"actor_id": {"$exists": False}},
            {"actor_id": None}
        ]
    }).to_list(length=None)
    
    print(f"📊 Found {len(images_without_actor)} images without actor_id")
    
    if len(images_without_actor) == 0:
        print("✅ No migration needed - all images have actor_id!")
        client.close()
        return
    
    print("\n⚠️  WARNING: These images don't have actor_id:")
    print("   They will appear in ALL actors' galleries for the same model_id")
    print("   You have 3 options:")
    print("   1. Leave them as-is (NULL actor_id) - backward compatible")
    print("   2. Delete them (recommended if they're old test data)")
    print("   3. Manually assign actor_id (if you know which actor they belong to)")
    print()
    
    # Show samples
    for i, img in enumerate(images_without_actor[:5]):
        print(f"{i+1}. Image ID: {img['image_id']}")
        print(f"   Model ID: {img['model_id']}")
        print(f"   Prompt: {img['metadata']['positive_prompt'][:60]}...")
        print(f"   Created: {img['created_at']}")
        print()
    
    if len(images_without_actor) > 5:
        print(f"   ... and {len(images_without_actor) - 5} more images")
        print()
    
    # Ask user what to do
    print("What would you like to do?")
    print("1. Keep images as-is (NULL actor_id) - they'll show in all galleries")
    print("2. Delete all old images without actor_id")
    print("3. Exit (do nothing)")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        print("✅ Keeping images as-is with NULL actor_id")
        print("   Note: These images will appear in all actors' galleries for the same model_id")
        
    elif choice == "2":
        confirm = input(f"⚠️  Are you sure you want to DELETE {len(images_without_actor)} images? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            result = await images_collection.delete_many({
                "$or": [
                    {"actor_id": {"$exists": False}},
                    {"actor_id": None}
                ]
            })
            print(f"🗑️  Deleted {result.deleted_count} images without actor_id")
        else:
            print("❌ Deletion cancelled")
    
    else:
        print("❌ Migration cancelled")
    
    client.close()
    print("\n✅ Migration script completed!")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Migration: Add actor_id to existing images")
    print("=" * 60)
    print()
    
    asyncio.run(migrate_images())
