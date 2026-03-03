#!/usr/bin/env python3
"""
Script to check saved AI-generated images in database
Run after saving images from Generate Tab
"""
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from kamma_appearance_models import GeneratedImageDocument

async def check_saved_images(actor_id=None):
    """Check all saved images, optionally filter by actor_id"""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(
        database=client['dmm_database'],
        document_models=[GeneratedImageDocument]
    )
    
    print("=" * 70)
    print("🖼️  CHECKING SAVED AI IMAGES IN DATABASE")
    print("=" * 70)
    
    # Find all generated images
    if actor_id:
        images = await GeneratedImageDocument.find(
            GeneratedImageDocument.actor_id == actor_id
        ).to_list()
        print(f"\n📊 Filtering by actor_id: {actor_id}")
    else:
        images = await GeneratedImageDocument.find_all().to_list()
    
    print(f"\n📊 Total images found: {len(images)}")
    
    if not images:
        print("\n❌ No images found in database!")
        print("\n💡 Try:")
        print("   1. Generate an image in Character Avatar → Generate tab")
        print("   2. Click 'Save to Gallery' button")
        print("   3. Run this script again")
        return
    
    print("\n" + "=" * 70)
    print("SAVED IMAGES:")
    print("=" * 70)
    
    for i, img in enumerate(images, 1):
        print(f"\n{i}. Image ID: {img.image_id}")
        print(f"   Model ID: {img.model_id}")
        print(f"   Actor ID: {img.actor_id or 'None'}")
        print(f"   Style: {img.metadata.style}")
        print(f"   Size: {img.metadata.width}x{img.metadata.height}")
        print(f"   Image Size: {img.metadata.image_size_kb:.2f} KB")
        
        if img.metadata.thumbnail_medium_base64:
            print(f"   Medium Thumbnail: {img.metadata.thumbnail_medium_size_kb:.2f} KB ✅")
        else:
            print(f"   Medium Thumbnail: Not generated ⚠️")
        
        print(f"   Seed: {img.metadata.seed}")
        print(f"   Favorite: {'⭐ Yes' if img.metadata.is_favorite else 'No'}")
        print(f"   Created: {img.created_at}")
        print(f"   Prompt: {img.metadata.positive_prompt[:80]}...")
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully loaded {len(images)} image(s)")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    
    # Optional: pass actor_id as command line argument
    actor_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    asyncio.run(check_saved_images(actor_id))
