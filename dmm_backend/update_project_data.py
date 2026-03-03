"""
Update existing project data with missing fields
Adds descriptions and other metadata to existing projects
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "peace_script_db")

async def update_projects():
    """Update existing projects with missing data"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    projects_collection = db["narrative_projects"]
    
    print("🔄 Starting project data update...")
    print(f"📊 Database: {DATABASE_NAME}")
    
    # Get all projects
    projects = await projects_collection.find({}).to_list(length=None)
    print(f"\n📁 Found {len(projects)} projects to check")
    
    updates_made = 0
    
    for project in projects:
        update_fields = {}
        needs_update = False
        
        # Add description if missing
        if not project.get("description") or project.get("description") is None:
            script_name = project.get("script_name", "Untitled")
            genre = project.get("genre_display", "ดราม่า")
            update_fields["description"] = f"โปรเจ็กต์ {script_name} - {genre} ที่สร้างด้วยระบบ Peace Script"
            needs_update = True
        
        # Ensure genre_display exists
        if not project.get("genre_display"):
            update_fields["genre_display"] = "ดราม่า"
            needs_update = True
        
        # Ensure progress exists
        if "progress" not in project or project.get("progress") is None:
            update_fields["progress"] = 0
            needs_update = True
        
        # Ensure scenes_count and characters_count exist
        if "scenes_count" not in project or project.get("scenes_count") is None:
            update_fields["scenes_count"] = 0
            needs_update = True
            
        if "characters_count" not in project or project.get("characters_count") is None:
            update_fields["characters_count"] = 0
            needs_update = True
        
        if needs_update:
            update_fields["updated_at"] = datetime.utcnow()
            
            result = await projects_collection.update_one(
                {"_id": project["_id"]},
                {"$set": update_fields}
            )
            
            if result.modified_count > 0:
                updates_made += 1
                print(f"✅ Updated: {project.get('script_name', 'Unknown')}")
                print(f"   Fields updated: {', '.join(update_fields.keys())}")
        else:
            print(f"✓ No update needed: {project.get('script_name', 'Unknown')}")
    
    print(f"\n✨ Update complete!")
    print(f"📊 {updates_made}/{len(projects)} projects updated")
    
    # Show updated data
    print("\n📋 Updated Project Data:")
    updated_projects = await projects_collection.find({}).to_list(length=None)
    for p in updated_projects:
        print(f"\n  • {p.get('title', 'No title')}")
        print(f"    Description: {p.get('description', 'N/A')}")
        print(f"    Genre: {p.get('genre_display', 'N/A')}")
        print(f"    Progress: {p.get('progress', 0)}%")
        print(f"    Scenes: {p.get('scenes_count', 0)} | Characters: {p.get('characters_count', 0)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_projects())
