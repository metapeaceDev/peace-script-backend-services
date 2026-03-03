"""
Sample Data Generator for Product Placement System
Peace Script v1.4

This script creates sample brands, products, and placements
for testing and demonstration purposes.
"""

import asyncio
from datetime import datetime
from documents_placement import Brand, Product, ProductPlacement, ProductCategory, PlacementMode, Visibility, DhammaFit, Position, TargetAudience
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

async def create_sample_data():
    """Create sample data for Product Placement system"""
    
    # Initialize database
    client = AsyncIOMotorClient(settings.MONGO_URI)
    database = client.get_database(settings.MONGO_DB_NAME)
    
    await init_beanie(
        database=database,
        document_models=[Brand, Product, ProductPlacement]
    )
    
    print("🎬 Creating sample Product Placement data...\n")
    
    # ========================================================================
    # CREATE BRANDS
    # ========================================================================
    
    print("📊 Creating brands...")
    
    brands_data = [
        {
            "brand_name": "Coca-Cola",
            "industry": "Food & Beverage",
            "description": "World's leading beverage company, known for happiness and refreshment",
            "values": ["happiness", "refreshment", "sharing", "tradition"],
            "website": "https://www.coca-cola.com"
        },
        {
            "brand_name": "Apple",
            "industry": "Technology",
            "description": "Innovation leader in consumer electronics and software",
            "values": ["innovation", "design", "simplicity", "creativity"],
            "website": "https://www.apple.com"
        },
        {
            "brand_name": "Nike",
            "industry": "Sports & Fashion",
            "description": "Global leader in athletic footwear and apparel",
            "values": ["excellence", "inspiration", "innovation", "sustainability"],
            "website": "https://www.nike.com"
        },
        {
            "brand_name": "Toyota",
            "industry": "Automotive",
            "description": "World's largest automobile manufacturer",
            "values": ["quality", "reliability", "innovation", "respect"],
            "website": "https://www.toyota.com"
        },
        {
            "brand_name": "Starbucks",
            "industry": "Food & Beverage",
            "description": "Premium coffee company and coffeehouse chain",
            "values": ["community", "quality", "responsibility", "warmth"],
            "website": "https://www.starbucks.com"
        }
    ]
    
    brands = []
    for brand_data in brands_data:
        brand = Brand(**brand_data)
        await brand.insert()
        brands.append(brand)
        print(f"  ✅ Created brand: {brand.brand_name} (ID: {brand.brand_id})")
    
    print(f"\n✨ Created {len(brands)} brands\n")
    
    # ========================================================================
    # CREATE PRODUCTS
    # ========================================================================
    
    print("📦 Creating products...")
    
    products_data = [
        # Coca-Cola products
        {
            "product_name": "Coca-Cola Classic",
            "brand_id": brands[0].brand_id,
            "category": ProductCategory.FOOD_BEVERAGE,
            "description": "Original Coca-Cola soft drink",
            "target_audience": [TargetAudience.GENERAL],
            "age_restriction": 0,
            "tags": ["soft drink", "cola", "refreshment"]
        },
        {
            "product_name": "Coca-Cola Zero",
            "brand_id": brands[0].brand_id,
            "category": ProductCategory.FOOD_BEVERAGE,
            "description": "Zero sugar version of Coca-Cola",
            "target_audience": [TargetAudience.ADULT, TargetAudience.YOUNG_ADULT],
            "age_restriction": 0,
            "tags": ["soft drink", "zero sugar", "health"]
        },
        # Apple products
        {
            "product_name": "iPhone 15 Pro",
            "brand_id": brands[1].brand_id,
            "category": ProductCategory.ELECTRONICS,
            "description": "Latest flagship smartphone from Apple",
            "target_audience": [TargetAudience.YOUNG_ADULT, TargetAudience.ADULT],
            "age_restriction": 13,
            "tags": ["smartphone", "5G", "premium", "camera"]
        },
        {
            "product_name": "MacBook Pro",
            "brand_id": brands[1].brand_id,
            "category": ProductCategory.ELECTRONICS,
            "description": "Professional laptop for creators",
            "target_audience": [TargetAudience.ADULT, TargetAudience.YOUNG_ADULT],
            "age_restriction": 13,
            "tags": ["laptop", "professional", "creative"]
        },
        {
            "product_name": "AirPods Pro",
            "brand_id": brands[1].brand_id,
            "category": ProductCategory.ELECTRONICS,
            "description": "Premium wireless earbuds with noise cancellation",
            "target_audience": [TargetAudience.YOUNG_ADULT, TargetAudience.ADULT],
            "age_restriction": 13,
            "tags": ["audio", "wireless", "premium"]
        },
        # Nike products
        {
            "product_name": "Air Jordan 1",
            "brand_id": brands[2].brand_id,
            "category": ProductCategory.FASHION,
            "description": "Iconic basketball sneakers",
            "target_audience": [TargetAudience.TEEN, TargetAudience.YOUNG_ADULT],
            "age_restriction": 0,
            "tags": ["sneakers", "basketball", "fashion", "iconic"]
        },
        {
            "product_name": "Nike Pro Dri-FIT",
            "brand_id": brands[2].brand_id,
            "category": ProductCategory.SPORTS_FITNESS,
            "description": "Performance athletic wear",
            "target_audience": [TargetAudience.YOUNG_ADULT, TargetAudience.ADULT],
            "age_restriction": 0,
            "tags": ["athletic wear", "performance", "sports"]
        },
        # Toyota products
        {
            "product_name": "Toyota Camry",
            "brand_id": brands[3].brand_id,
            "category": ProductCategory.AUTOMOTIVE,
            "description": "Best-selling family sedan",
            "target_audience": [TargetAudience.ADULT],
            "age_restriction": 18,
            "tags": ["sedan", "family car", "reliable"]
        },
        {
            "product_name": "Toyota RAV4",
            "brand_id": brands[3].brand_id,
            "category": ProductCategory.AUTOMOTIVE,
            "description": "Compact SUV for adventure",
            "target_audience": [TargetAudience.ADULT],
            "age_restriction": 18,
            "tags": ["SUV", "adventure", "versatile"]
        },
        # Starbucks products
        {
            "product_name": "Starbucks Caramel Macchiato",
            "brand_id": brands[4].brand_id,
            "category": ProductCategory.FOOD_BEVERAGE,
            "description": "Premium coffee drink with caramel",
            "target_audience": [TargetAudience.YOUNG_ADULT, TargetAudience.ADULT],
            "age_restriction": 0,
            "tags": ["coffee", "premium", "caramel"]
        }
    ]
    
    products = []
    for product_data in products_data:
        product = Product(**product_data)
        await product.insert()
        products.append(product)
        print(f"  ✅ Created product: {product.product_name} (ID: {product.product_id})")
    
    print(f"\n✨ Created {len(products)} products\n")
    
    # ========================================================================
    # CREATE SAMPLE PLACEMENTS
    # ========================================================================
    
    print("🎬 Creating sample placements...")
    print("  Note: These placements use placeholder scene/shot IDs")
    print("  You'll need to update them with actual IDs from your scenes\n")
    
    placements_data = [
        {
            "product_id": products[0].product_id,  # Coca-Cola Classic
            "scene_id": "scene_001",  # Placeholder
            "shot_id": "shot_001",
            "placement_mode": PlacementMode.ORGANIC,
            "visibility": Visibility.MODERATE,
            "position": Position.BACKGROUND,
            "screen_time_seconds": 5,
            "ethical_score": 85,
            "dhamma_fit": DhammaFit.FIT,
            "age_appropriate": True,
            "character_interaction": True,
            "context_description": "Character drinks Coca-Cola during lunch scene",
            "placement_reason": "Natural product integration in dining context",
            "notes": "Product visible on table, character interacts naturally"
        },
        {
            "product_id": products[2].product_id,  # iPhone 15 Pro
            "scene_id": "scene_002",
            "shot_id": "shot_002",
            "placement_mode": PlacementMode.INTERACTIVE,
            "visibility": Visibility.PROMINENT,
            "position": Position.FOREGROUND,
            "screen_time_seconds": 15,
            "ethical_score": 75,
            "dhamma_fit": DhammaFit.NEUTRAL,
            "age_appropriate": True,
            "character_interaction": True,
            "context_description": "Character uses iPhone to make important call",
            "placement_reason": "Tech product usage drives plot forward",
            "notes": "Close-up shots of device, Apple logo visible"
        },
        {
            "product_id": products[5].product_id,  # Air Jordan 1
            "scene_id": "scene_003",
            "shot_id": "shot_003",
            "placement_mode": PlacementMode.EXPLICIT,
            "visibility": Visibility.PROMINENT,
            "position": Position.MIDGROUND,
            "screen_time_seconds": 8,
            "ethical_score": 70,
            "dhamma_fit": DhammaFit.NEUTRAL,
            "age_appropriate": True,
            "character_interaction": False,
            "context_description": "Nike sneakers prominently displayed in sports store scene",
            "placement_reason": "Establishes setting and character's interest in fashion",
            "notes": "Product shot, logo clearly visible"
        },
        {
            "product_id": products[9].product_id,  # Starbucks Caramel Macchiato
            "scene_id": "scene_004",
            "shot_id": "shot_004",
            "placement_mode": PlacementMode.BACKGROUND,
            "visibility": Visibility.SUBTLE,
            "position": Position.BACKGROUND,
            "screen_time_seconds": 3,
            "ethical_score": 90,
            "dhamma_fit": DhammaFit.FIT,
            "age_appropriate": True,
            "character_interaction": False,
            "context_description": "Starbucks cup visible on office desk",
            "placement_reason": "Authentic workplace environment detail",
            "notes": "Logo partially visible, natural placement"
        },
        {
            "product_id": products[7].product_id,  # Toyota Camry
            "scene_id": "scene_005",
            "shot_id": "shot_005",
            "placement_mode": PlacementMode.ORGANIC,
            "visibility": Visibility.MODERATE,
            "position": Position.FOREGROUND,
            "screen_time_seconds": 12,
            "ethical_score": 80,
            "dhamma_fit": DhammaFit.FIT,
            "age_appropriate": True,
            "character_interaction": True,
            "context_description": "Character drives Toyota Camry to work",
            "placement_reason": "Establishes character's lifestyle and reliability",
            "notes": "Car exterior and interior shots, Toyota badge visible"
        }
    ]
    
    placements = []
    for placement_data in placements_data:
        placement = ProductPlacement(**placement_data, approved_by=None, approved_at=None)
        await placement.insert()
        placements.append(placement)
        product = next(p for p in products if p.product_id == placement.product_id)
        print(f"  ✅ Created placement: {product.product_name} in {placement.scene_id} ({placement.placement_mode})")
    
    print(f"\n✨ Created {len(placements)} sample placements\n")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("=" * 70)
    print("✅ SAMPLE DATA CREATION COMPLETE!")
    print("=" * 70)
    print(f"📊 Brands created: {len(brands)}")
    print(f"📦 Products created: {len(products)}")
    print(f"🎬 Placements created: {len(placements)}")
    print()
    print("📝 Note: Placeholder scene/shot IDs were used (scene_001, shot_001, etc.)")
    print("   Update placements with real scene IDs from your Peace Script project")
    print()
    print("🎯 Next steps:")
    print("   1. Start backend: cd dmm_backend && ./venv/bin/uvicorn main:app")
    print("   2. Start frontend: cd frontend && npm run dev")
    print("   3. Navigate to Step 5 - Scene Design")
    print("   4. Test Product Placement panel")
    print()
    print("🔗 API Endpoints available at http://127.0.0.1:8000/docs")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(create_sample_data())
