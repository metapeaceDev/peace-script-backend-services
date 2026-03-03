"""
Product Placement Router - Product Placement Management
========================================================
ตามแผน Peace Script V.14 - Step 2.2.91, Product Placement Module

Router นี้จัดการ:
- CRUD operations สำหรับ Brands, Products, ProductPlacements
- Analytics (placement count, ethics score, screen time)
- Ethics Audit (Dhamma-fit compliance checking)
- Approval workflow (approve/reject placements)

Routes:
    # Brands
    POST   /api/placement/brands/              - สร้าง brand ใหม่
    GET    /api/placement/brands/              - List brands
    GET    /api/placement/brands/{id}          - Get brand by ID
    PUT    /api/placement/brands/{id}          - Update brand
    DELETE /api/placement/brands/{id}          - Delete brand
    
    # Products
    POST   /api/placement/products/            - สร้าง product ใหม่
    GET    /api/placement/products/            - List products
    GET    /api/placement/products/{id}        - Get product by ID
    PUT    /api/placement/products/{id}        - Update product
    DELETE /api/placement/products/{id}        - Delete product
    GET    /api/placement/products/by-brand/{brand_id} - Get products by brand
    
    # Product Placements
    POST   /api/placement/placements/          - สร้าง placement ใหม่
    GET    /api/placement/placements/          - List placements
    GET    /api/placement/placements/{id}      - Get placement by ID
    PUT    /api/placement/placements/{id}      - Update placement
    DELETE /api/placement/placements/{id}      - Delete placement
    GET    /api/placement/placements/by-scene/{scene_id} - Get placements by scene
    GET    /api/placement/placements/by-shot/{shot_id} - Get placements by shot
    POST   /api/placement/placements/{id}/approve - Approve placement
    POST   /api/placement/placements/{id}/reject - Reject placement
    
    # Analytics & Ethics
    GET    /api/placement/analytics/summary    - Get analytics summary
    POST   /api/placement/ethics/audit/{id}    - Run ethics audit on placement
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status
from beanie import PydanticObjectId

from documents_placement import (
    Brand,
    Product,
    ProductPlacement,
    ProductCategory,
    PlacementMode,
    DhammaFit,
    Visibility
)
from schemas_placement import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductPlacementCreate,
    ProductPlacementUpdate,
    ProductPlacementResponse,
    PlacementAnalytics,
    EthicsAuditResponse
)

router = APIRouter(prefix="/api/placement", tags=["Product Placement"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def to_brand_response(brand: Brand) -> BrandResponse:
    """Convert Brand document to BrandResponse"""
    data = brand.model_dump()
    data["id"] = str(brand.id)
    return BrandResponse.model_validate(data)


def to_product_response(product: Product) -> ProductResponse:
    """Convert Product document to ProductResponse"""
    data = product.model_dump()
    data["id"] = str(product.id)
    return ProductResponse.model_validate(data)


def to_placement_response(placement: ProductPlacement) -> ProductPlacementResponse:
    """Convert ProductPlacement document to ProductPlacementResponse"""
    data = placement.model_dump()
    data["id"] = str(placement.id)
    return ProductPlacementResponse.model_validate(data)


# ============================================================================
# BRAND ENDPOINTS
# ============================================================================

@router.post("/brands/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand_data: BrandCreate) -> BrandResponse:
    """
    สร้าง Brand ใหม่
    
    Args:
        brand_data: ข้อมูล brand (brand_name, industry, values, etc.)
        
    Returns:
        BrandResponse: Brand ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "brand_name": "Coca-Cola",
            "industry": "Food & Beverage",
            "description": "Leading beverage company",
            "values": ["happiness", "sharing", "refreshment"],
            "website": "https://www.coca-cola.com",
            "contact_email": "contact@coca-cola.com"
        }
        ```
    """
    try:
        brand = Brand(
            brand_name=brand_data.brand_name,
            industry=brand_data.industry,
            description=brand_data.description,
            logo_url=brand_data.logo_url,
            values=brand_data.values,
            website=brand_data.website,
            contact_email=brand_data.contact_email
        )
        
        await brand.insert()
        return to_brand_response(brand)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create brand: {str(e)}"
        )


@router.get("/brands/", response_model=List[BrandResponse])
async def list_brands(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in brand name"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[BrandResponse]:
    """
    List Brands พร้อม filters
    
    Query Parameters:
        - industry: filter by industry type
        - is_active: filter by active status
        - search: search in brand_name
        - limit: max results (default 100)
        - skip: pagination offset
        
    Returns:
        List[BrandResponse]: รายการ brands
    """
    try:
        query = {}
        
        if industry:
            query["industry"] = industry
        
        if is_active is not None:
            query["is_active"] = is_active
        
        if search:
            query["brand_name"] = {"$regex": search, "$options": "i"}
        
        brands = await Brand.find(query).skip(skip).limit(limit).to_list()
        return [to_brand_response(b) for b in brands]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list brands: {str(e)}"
        )


@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: str) -> BrandResponse:
    """Get brand by ID or brand_id"""
    try:
        # Try by brand_id first
        brand = await Brand.find_one({"brand_id": brand_id})
        
        # Try by ObjectId if not found
        if not brand:
            try:
                obj_id = PydanticObjectId(brand_id)
                brand = await Brand.get(obj_id)
            except Exception:
                pass
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {brand_id} not found"
            )
        
        return to_brand_response(brand)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get brand: {str(e)}"
        )


@router.put("/brands/{brand_id}", response_model=BrandResponse)
async def update_brand(brand_id: str, brand_data: BrandUpdate) -> BrandResponse:
    """Update brand"""
    try:
        brand = await Brand.find_one({"brand_id": brand_id})
        if not brand:
            try:
                obj_id = PydanticObjectId(brand_id)
                brand = await Brand.get(obj_id)
            except Exception:
                pass
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {brand_id} not found"
            )
        
        # Update fields
        update_data = brand_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)
        
        brand.updated_at = datetime.utcnow()
        await brand.save()
        
        return to_brand_response(brand)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update brand: {str(e)}"
        )


@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: str):
    """Delete brand"""
    try:
        brand = await Brand.find_one({"brand_id": brand_id})
        if not brand:
            try:
                obj_id = PydanticObjectId(brand_id)
                brand = await Brand.get(obj_id)
            except Exception:
                pass
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {brand_id} not found"
            )
        
        await brand.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete brand: {str(e)}"
        )


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate) -> ProductResponse:
    """
    สร้าง Product ใหม่
    
    Args:
        product_data: ข้อมูล product
        
    Returns:
        ProductResponse: Product ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "product_name": "iPhone 15 Pro",
            "brand_id": "BRD_20250120120000",
            "category": "electronics",
            "description": "Latest flagship smartphone",
            "target_audience": ["young_adult", "adult"],
            "age_restriction": 13,
            "tags": ["smartphone", "5G", "premium"]
        }
        ```
    """
    try:
        # Verify brand exists
        brand = await Brand.find_one({"brand_id": product_data.brand_id})
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand {product_data.brand_id} not found"
            )
        
        product = Product(
            product_name=product_data.product_name,
            brand_id=product_data.brand_id,
            category=product_data.category,
            description=product_data.description,
            image_url=product_data.image_url,
            target_audience=product_data.target_audience,
            age_restriction=product_data.age_restriction,
            ethical_restrictions=product_data.ethical_restrictions,
            tags=product_data.tags
        )
        
        await product.insert()
        return to_product_response(product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("/products/", response_model=List[ProductResponse])
async def list_products(
    brand_id: Optional[str] = Query(None, description="Filter by brand_id"),
    category: Optional[ProductCategory] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in product name"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[ProductResponse]:
    """List Products พร้อม filters"""
    try:
        query = {}
        
        if brand_id:
            query["brand_id"] = brand_id
        
        if category:
            query["category"] = category
        
        if is_active is not None:
            query["is_active"] = is_active
        
        if search:
            query["product_name"] = {"$regex": search, "$options": "i"}
        
        products = await Product.find(query).skip(skip).limit(limit).to_list()
        return [to_product_response(p) for p in products]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list products: {str(e)}"
        )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str) -> ProductResponse:
    """Get product by ID or product_id"""
    try:
        product = await Product.find_one({"product_id": product_id})
        
        if not product:
            try:
                obj_id = PydanticObjectId(product_id)
                product = await Product.get(obj_id)
            except Exception:
                pass
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        return to_product_response(product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product: {str(e)}"
        )


@router.get("/products/by-brand/{brand_id}", response_model=List[ProductResponse])
async def get_products_by_brand(brand_id: str) -> List[ProductResponse]:
    """Get all products by brand_id"""
    try:
        products = await Product.find({"brand_id": brand_id, "is_active": True}).to_list()
        return [to_product_response(p) for p in products]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get products by brand: {str(e)}"
        )


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_data: ProductUpdate) -> ProductResponse:
    """Update product"""
    try:
        product = await Product.find_one({"product_id": product_id})
        if not product:
            try:
                obj_id = PydanticObjectId(product_id)
                product = await Product.get(obj_id)
            except Exception:
                pass
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        # Update fields
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        product.updated_at = datetime.utcnow()
        await product.save()
        
        return to_product_response(product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    """Delete product"""
    try:
        product = await Product.find_one({"product_id": product_id})
        if not product:
            try:
                obj_id = PydanticObjectId(product_id)
                product = await Product.get(obj_id)
            except Exception:
                pass
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        await product.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        )


# ============================================================================
# PRODUCT PLACEMENT ENDPOINTS
# ============================================================================

@router.post("/placements/", response_model=ProductPlacementResponse, status_code=status.HTTP_201_CREATED)
async def create_placement(placement_data: ProductPlacementCreate) -> ProductPlacementResponse:
    """
    สร้าง Product Placement ใหม่
    
    Args:
        placement_data: ข้อมูล placement
        
    Returns:
        ProductPlacementResponse: Placement ที่สร้างแล้ว
        
    Example:
        ```json
        {
            "product_id": "PRD_20250120120000",
            "scene_id": "68fcace553611223c213415c",
            "shot_id": "68fcace553611223c213415d",
            "placement_mode": "organic",
            "visibility": "subtle",
            "position": "background",
            "screen_time_seconds": 3,
            "ethical_score": 85,
            "dhamma_fit": "fit"
        }
        ```
    """
    try:
        # Verify product exists
        product = await Product.find_one({"product_id": placement_data.product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {placement_data.product_id} not found"
            )
        
        placement = ProductPlacement(
            product_id=placement_data.product_id,
            scene_id=placement_data.scene_id,
            shot_id=placement_data.shot_id,
            project_id=placement_data.project_id,
            placement_mode=placement_data.placement_mode,
            visibility=placement_data.visibility,
            context_fit=placement_data.context_fit,
            position=placement_data.position,
            screen_time_seconds=placement_data.screen_time_seconds,
            timestamp_start=placement_data.timestamp_start,
            timestamp_end=placement_data.timestamp_end,
            character_interaction=placement_data.character_interaction,
            interacting_character_ids=placement_data.interacting_character_ids,
            ethical_score=placement_data.ethical_score,
            dhamma_fit=placement_data.dhamma_fit,
            age_appropriate=placement_data.age_appropriate,
            context_description=placement_data.context_description,
            placement_reason=placement_data.placement_reason,
            causal_link=placement_data.causal_link,
            analytic_tag=placement_data.analytic_tag,
            teaching_tag=placement_data.teaching_tag,
            qa_result=placement_data.qa_result,
            notes=placement_data.notes,
            approved_by=None,
            approved_at=None
        )
        
        await placement.insert()
        return to_placement_response(placement)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create placement: {str(e)}"
        )


@router.get("/placements/", response_model=List[ProductPlacementResponse])
async def list_placements(
    scene_id: Optional[str] = Query(None, description="Filter by scene_id"),
    shot_id: Optional[str] = Query(None, description="Filter by shot_id"),
    product_id: Optional[str] = Query(None, description="Filter by product_id"),
    project_id: Optional[str] = Query(None, description="Filter by project_id"),
    is_approved: Optional[bool] = Query(None, description="Filter by approval status"),
    placement_mode: Optional[PlacementMode] = Query(None, description="Filter by placement mode"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[ProductPlacementResponse]:
    """List Product Placements พร้อม filters"""
    try:
        query = {}
        
        if scene_id:
            query["scene_id"] = scene_id
        
        if shot_id:
            query["shot_id"] = shot_id
        
        if product_id:
            query["product_id"] = product_id
        
        if project_id:
            query["project_id"] = project_id
        
        if is_approved is not None:
            query["is_approved"] = is_approved
        
        if placement_mode:
            query["placement_mode"] = placement_mode
        
        placements = await ProductPlacement.find(query).skip(skip).limit(limit).to_list()
        return [to_placement_response(p) for p in placements]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list placements: {str(e)}"
        )


@router.get("/placements/{placement_id}", response_model=ProductPlacementResponse)
async def get_placement(placement_id: str) -> ProductPlacementResponse:
    """Get placement by ID or placement_id"""
    try:
        placement = await ProductPlacement.find_one({"placement_id": placement_id})
        
        if not placement:
            try:
                obj_id = PydanticObjectId(placement_id)
                placement = await ProductPlacement.get(obj_id)
            except Exception:
                pass
        
        if not placement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement {placement_id} not found"
            )
        
        return to_placement_response(placement)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get placement: {str(e)}"
        )


@router.get("/placements/by-scene/{scene_id}", response_model=List[ProductPlacementResponse])
async def get_placements_by_scene(scene_id: str) -> List[ProductPlacementResponse]:
    """Get all placements by scene_id"""
    try:
        placements = await ProductPlacement.find({"scene_id": scene_id}).to_list()
        return [to_placement_response(p) for p in placements]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get placements by scene: {str(e)}"
        )


@router.get("/placements/by-shot/{shot_id}", response_model=List[ProductPlacementResponse])
async def get_placements_by_shot(shot_id: str) -> List[ProductPlacementResponse]:
    """Get all placements by shot_id"""
    try:
        placements = await ProductPlacement.find({"shot_id": shot_id}).to_list()
        return [to_placement_response(p) for p in placements]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get placements by shot: {str(e)}"
        )


@router.put("/placements/{placement_id}", response_model=ProductPlacementResponse)
async def update_placement(placement_id: str, placement_data: ProductPlacementUpdate) -> ProductPlacementResponse:
    """Update placement"""
    try:
        placement = await ProductPlacement.find_one({"placement_id": placement_id})
        if not placement:
            try:
                obj_id = PydanticObjectId(placement_id)
                placement = await ProductPlacement.get(obj_id)
            except Exception:
                pass
        
        if not placement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement {placement_id} not found"
            )
        
        # Update fields
        update_data = placement_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(placement, field, value)
        
        placement.updated_at = datetime.utcnow()
        await placement.save()
        
        return to_placement_response(placement)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update placement: {str(e)}"
        )


@router.delete("/placements/{placement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_placement(placement_id: str):
    """Delete placement"""
    try:
        placement = await ProductPlacement.find_one({"placement_id": placement_id})
        if not placement:
            try:
                obj_id = PydanticObjectId(placement_id)
                placement = await ProductPlacement.get(obj_id)
            except Exception:
                pass
        
        if not placement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement {placement_id} not found"
            )
        
        await placement.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete placement: {str(e)}"
        )


@router.post("/placements/{placement_id}/approve", response_model=ProductPlacementResponse)
async def approve_placement(placement_id: str, approved_by: str) -> ProductPlacementResponse:
    """Approve placement"""
    try:
        placement = await ProductPlacement.find_one({"placement_id": placement_id})
        if not placement:
            try:
                obj_id = PydanticObjectId(placement_id)
                placement = await ProductPlacement.get(obj_id)
            except Exception:
                pass
        
        if not placement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement {placement_id} not found"
            )
        
        placement.is_approved = True
        placement.approved_by = approved_by
        placement.approved_at = datetime.utcnow()
        placement.updated_at = datetime.utcnow()
        
        await placement.save()
        return to_placement_response(placement)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve placement: {str(e)}"
        )


@router.post("/placements/{placement_id}/reject", response_model=ProductPlacementResponse)
async def reject_placement(placement_id: str) -> ProductPlacementResponse:
    """Reject placement"""
    try:
        placement = await ProductPlacement.find_one({"placement_id": placement_id})
        if not placement:
            try:
                obj_id = PydanticObjectId(placement_id)
                placement = await ProductPlacement.get(obj_id)
            except Exception:
                pass
        
        if not placement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement {placement_id} not found"
            )
        
        placement.is_approved = False
        placement.approved_by = None
        placement.approved_at = None
        placement.updated_at = datetime.utcnow()
        
        await placement.save()
        return to_placement_response(placement)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject placement: {str(e)}"
        )


# ============================================================================
# ANALYTICS & ETHICS ENDPOINTS
# ============================================================================

@router.get("/analytics/summary", response_model=PlacementAnalytics)
async def get_analytics_summary(
    project_id: Optional[str] = Query(None, description="Filter by project_id"),
    scene_id: Optional[str] = Query(None, description="Filter by scene_id")
) -> PlacementAnalytics:
    """
    Get placement analytics summary
    
    Returns aggregated statistics:
    - Total placements, products, brands
    - Placements by mode/visibility/position
    - Ethics compliance (avg ethical_score, dhamma_fit distribution, approval rate)
    - Screen time statistics
    - Top products/brands by placement count
    """
    try:
        # Build query
        query = {}
        if project_id:
            query["project_id"] = project_id
        if scene_id:
            query["scene_id"] = scene_id
        
        # Get all placements
        placements = await ProductPlacement.find(query).to_list()
        
        if not placements:
            return PlacementAnalytics(
                total_placements=0,
                total_products=0,
                total_brands=0,
                avg_ethical_score=0.0,
                approval_rate=0.0,
                total_screen_time_seconds=0,
                avg_screen_time_seconds=0.0
            )
        
        # Count unique products and brands
        product_ids = set(p.product_id for p in placements)
        products = await Product.find({"product_id": {"$in": list(product_ids)}}).to_list()
        brand_ids = set(p.brand_id for p in products)
        
        # Analytics by mode
        by_mode = {}
        for mode in PlacementMode:
            count = sum(1 for p in placements if p.placement_mode == mode)
            if count > 0:
                by_mode[mode.value] = count
        
        # Analytics by visibility
        by_visibility = {}
        for vis in Visibility:
            count = sum(1 for p in placements if p.visibility == vis)
            if count > 0:
                by_visibility[vis.value] = count
        
        # Dhamma fit distribution
        dhamma_dist = {}
        for dhamma in DhammaFit:
            count = sum(1 for p in placements if p.dhamma_fit == dhamma)
            if count > 0:
                dhamma_dist[dhamma.value] = count
        
        # Ethics scores
        ethical_scores = [p.ethical_score for p in placements]
        avg_ethical_score = sum(ethical_scores) / len(ethical_scores)
        
        # Approval rate
        approved_count = sum(1 for p in placements if p.is_approved)
        approval_rate = (approved_count / len(placements)) * 100
        
        # Screen time
        total_screen_time = sum(p.screen_time_seconds for p in placements)
        avg_screen_time = total_screen_time / len(placements)
        
        # Top products
        product_counts = {}
        for p in placements:
            product_counts[p.product_id] = product_counts.get(p.product_id, 0) + 1
        
        top_products_data = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_products = []
        for product_id, count in top_products_data:
            product = next((p for p in products if p.product_id == product_id), None)
            if product:
                top_products.append({
                    "product_id": product_id,
                    "product_name": product.product_name,
                    "count": count
                })
        
        # Top brands
        brand_counts = {}
        for p in placements:
            product = next((pr for pr in products if pr.product_id == p.product_id), None)
            if product:
                brand_counts[product.brand_id] = brand_counts.get(product.brand_id, 0) + 1
        
        top_brands_data = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        brands = await Brand.find({"brand_id": {"$in": list(brand_ids)}}).to_list()
        top_brands = []
        for brand_id, count in top_brands_data:
            brand = next((b for b in brands if b.brand_id == brand_id), None)
            if brand:
                top_brands.append({
                    "brand_id": brand_id,
                    "brand_name": brand.brand_name,
                    "count": count
                })
        
        return PlacementAnalytics(
            total_placements=len(placements),
            total_products=len(product_ids),
            total_brands=len(brand_ids),
            by_placement_mode=by_mode,
            by_visibility=by_visibility,
            avg_ethical_score=round(avg_ethical_score, 2),
            dhamma_fit_distribution=dhamma_dist,
            approval_rate=round(approval_rate, 2),
            total_screen_time_seconds=total_screen_time,
            avg_screen_time_seconds=round(avg_screen_time, 2),
            top_products=top_products,
            top_brands=top_brands
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.post("/ethics/audit/{placement_id}", response_model=EthicsAuditResponse)
async def run_ethics_audit(placement_id: str) -> EthicsAuditResponse:
    """
    Run ethics audit on placement
    
    Checks:
    - Dhamma fit (fit/neutral/conflict)
    - Ethical score (0-100)
    - Age appropriateness
    - Product ethical restrictions
    - Context fit
    
    Returns audit result with warnings and recommendations
    """
    try:
        placement = await ProductPlacement.find_one({"placement_id": placement_id})
        if not placement:
            try:
                obj_id = PydanticObjectId(placement_id)
                placement = await ProductPlacement.get(obj_id)
            except Exception:
                pass
        
        if not placement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement {placement_id} not found"
            )
        
        # Get product
        product = await Product.find_one({"product_id": placement.product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {placement.product_id} not found"
            )
        
        warnings = []
        recommendations = []
        
        # Check ethical score
        if placement.ethical_score < 50:
            warnings.append(f"Low ethical score: {placement.ethical_score}/100")
            recommendations.append("Consider reviewing placement context and purpose")
        
        # Check Dhamma fit
        if placement.dhamma_fit == DhammaFit.CONFLICT:
            warnings.append("Dhamma fit conflict detected")
            recommendations.append("Review Buddhist principles alignment")
        
        # Check age appropriateness
        if not placement.age_appropriate:
            warnings.append("Placement marked as not age appropriate")
            recommendations.append("Verify target audience and age restrictions")
        
        # Check ethical restrictions
        if product.ethical_restrictions:
            warnings.append(f"Product has ethical restrictions: {', '.join(product.ethical_restrictions)}")
            recommendations.append("Ensure placement complies with product restrictions")
        
        # Check context fit
        if placement.context_fit == "awkward":
            warnings.append("Awkward context fit detected")
            recommendations.append("Consider repositioning or changing placement mode")
        
        # Overall audit result
        audit_passed = (
            placement.ethical_score >= 50 and
            placement.dhamma_fit != DhammaFit.CONFLICT and
            placement.age_appropriate
        )
        
        return EthicsAuditResponse(
            placement_id=placement_id,
            ethical_score=placement.ethical_score,
            dhamma_fit=placement.dhamma_fit,
            age_appropriate=placement.age_appropriate,
            warnings=warnings,
            recommendations=recommendations,
            audit_passed=audit_passed,
            audit_timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run ethics audit: {str(e)}"
        )
