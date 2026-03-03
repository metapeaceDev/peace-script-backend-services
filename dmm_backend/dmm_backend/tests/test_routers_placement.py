"""
Product Placement Router Tests
===============================
Comprehensive test suite for Product Placement API endpoints.
Tests all 21 endpoints including CRUD, analytics, and ethics validation.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
from beanie import PydanticObjectId

from dmm_backend.documents_placement import Brand, Product, ProductPlacement
from dmm_backend.documents import User


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_brand():
    """Create test brand."""
    brand = Brand(
        name="Test Brand",
        logo_url="https://example.com/logo.png",
        website="https://testbrand.com",
        description="Test brand for unit testing",
        industry="Technology",
        ethics_status="Fit",
        dhamma_alignment_score=85,
        approval_status="Approved",
        approved_by=str(PydanticObjectId()),
        approved_at=datetime.utcnow()
    )
    await brand.insert()
    yield brand
    await brand.delete()


@pytest_asyncio.fixture
async def test_product(test_brand):
    """Create test product."""
    product = Product(
        brand_id=test_brand.id,
        name="Test Product",
        category="Electronics",
        description="Test product for unit testing",
        image_url="https://example.com/product.png",
        reference_url="https://testbrand.com/product",
        ethics_status="Fit",
        dhamma_alignment_score=80,
        approval_status="Approved"
    )
    await product.insert()
    yield product
    await product.delete()


@pytest_asyncio.fixture
async def test_placement(test_product):
    """Create test placement."""
    placement = ProductPlacement(
        product_id=test_product.id,
        project_id=str(PydanticObjectId()),
        scene_id=str(PydanticObjectId()),
        placement_type="Prop",
        visibility_level="Prominent",
        duration_seconds=5.0,
        screen_position="Center",
        context_description="Product placed on desk in office scene",
        ethics_review_status="Approved",
        ethics_notes="Aligned with non-commercial Dhamma values",
        approval_status="Approved",
        created_by=str(PydanticObjectId())
    )
    await placement.insert()
    yield placement
    await placement.delete()


# ============================================================================
# Brand Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_brand(async_client: AsyncClient):
    """Test POST /api/placement/brands - Create new brand."""
    brand_data = {
        "name": "New Test Brand",
        "logo_url": "https://example.com/new-logo.png",
        "website": "https://newtestbrand.com",
        "description": "New brand for testing",
        "industry": "Retail"
    }
    
    response = await async_client.post("/api/placement/brands", json=brand_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == brand_data["name"]
    assert data["industry"] == brand_data["industry"]
    assert "id" in data
    
    # Cleanup
    await Brand.get(PydanticObjectId(data["id"])).delete()


@pytest.mark.asyncio
async def test_get_all_brands(async_client: AsyncClient, test_brand):
    """Test GET /api/placement/brands - List all brands."""
    response = await async_client.get("/api/placement/brands")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(b["name"] == test_brand.name for b in data)


@pytest.mark.asyncio
async def test_get_brand_by_id(async_client: AsyncClient, test_brand):
    """Test GET /api/placement/brands/{id} - Get specific brand."""
    response = await async_client.get(f"/api/placement/brands/{test_brand.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_brand.id)
    assert data["name"] == test_brand.name


@pytest.mark.asyncio
async def test_update_brand(async_client: AsyncClient, test_brand):
    """Test PUT /api/placement/brands/{id} - Update brand."""
    update_data = {
        "description": "Updated description for testing",
        "industry": "Updated Industry"
    }
    
    response = await async_client.put(
        f"/api/placement/brands/{test_brand.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["industry"] == update_data["industry"]


@pytest.mark.asyncio
async def test_delete_brand(async_client: AsyncClient):
    """Test DELETE /api/placement/brands/{id} - Delete brand."""
    # Create temporary brand
    brand = Brand(name="Delete Test", industry="Test")
    await brand.insert()
    
    response = await async_client.delete(f"/api/placement/brands/{brand.id}")
    assert response.status_code == 200
    
    # Verify deletion
    deleted_brand = await Brand.get(brand.id)
    assert deleted_brand is None


# ============================================================================
# Product Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_product(async_client: AsyncClient, test_brand):
    """Test POST /api/placement/products - Create new product."""
    product_data = {
        "brand_id": str(test_brand.id),
        "name": "New Test Product",
        "category": "Electronics",
        "description": "New product for testing",
        "image_url": "https://example.com/new-product.png"
    }
    
    response = await async_client.post("/api/placement/products", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["brand_id"] == product_data["brand_id"]
    assert "id" in data
    
    # Cleanup
    await Product.get(PydanticObjectId(data["id"])).delete()


@pytest.mark.asyncio
async def test_get_all_products(async_client: AsyncClient, test_product):
    """Test GET /api/placement/products - List all products."""
    response = await async_client.get("/api/placement/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_products_by_brand(async_client: AsyncClient, test_brand, test_product):
    """Test GET /api/placement/products?brand_id={id} - Filter by brand."""
    response = await async_client.get(
        f"/api/placement/products?brand_id={test_brand.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(p["brand_id"] == str(test_brand.id) for p in data)


@pytest.mark.asyncio
async def test_get_products_by_category(async_client: AsyncClient, test_product):
    """Test GET /api/placement/products?category={cat} - Filter by category."""
    response = await async_client.get(
        f"/api/placement/products?category={test_product.category}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(p["category"] == test_product.category for p in data)


@pytest.mark.asyncio
async def test_get_product_by_id(async_client: AsyncClient, test_product):
    """Test GET /api/placement/products/{id} - Get specific product."""
    response = await async_client.get(f"/api/placement/products/{test_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_product.id)
    assert data["name"] == test_product.name


@pytest.mark.asyncio
async def test_update_product(async_client: AsyncClient, test_product):
    """Test PUT /api/placement/products/{id} - Update product."""
    update_data = {
        "description": "Updated product description",
        "category": "Updated Category"
    }
    
    response = await async_client.put(
        f"/api/placement/products/{test_product.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_delete_product(async_client: AsyncClient, test_brand):
    """Test DELETE /api/placement/products/{id} - Delete product."""
    # Create temporary product
    product = Product(
        brand_id=test_brand.id,
        name="Delete Test Product",
        category="Test"
    )
    await product.insert()
    
    response = await async_client.delete(f"/api/placement/products/{product.id}")
    assert response.status_code == 200
    
    # Verify deletion
    deleted_product = await Product.get(product.id)
    assert deleted_product is None


# ============================================================================
# Placement Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_placement(async_client: AsyncClient, test_product):
    """Test POST /api/placement/placements - Create new placement."""
    placement_data = {
        "product_id": str(test_product.id),
        "project_id": str(PydanticObjectId()),
        "scene_id": str(PydanticObjectId()),
        "placement_type": "Background",
        "visibility_level": "Subtle",
        "duration_seconds": 3.5,
        "context_description": "Product visible in background"
    }
    
    response = await async_client.post("/api/placement/placements", json=placement_data)
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == placement_data["product_id"]
    assert data["placement_type"] == placement_data["placement_type"]
    assert "id" in data
    
    # Cleanup
    await ProductPlacement.get(PydanticObjectId(data["id"])).delete()


@pytest.mark.asyncio
async def test_get_all_placements(async_client: AsyncClient, test_placement):
    """Test GET /api/placement/placements - List all placements."""
    response = await async_client.get("/api/placement/placements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_placements_by_project(async_client: AsyncClient, test_placement):
    """Test GET /api/placement/placements?project_id={id} - Filter by project."""
    response = await async_client.get(
        f"/api/placement/placements?project_id={test_placement.project_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(p["project_id"] == test_placement.project_id for p in data)


@pytest.mark.asyncio
async def test_get_placement_by_id(async_client: AsyncClient, test_placement):
    """Test GET /api/placement/placements/{id} - Get specific placement."""
    response = await async_client.get(f"/api/placement/placements/{test_placement.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_placement.id)
    assert data["placement_type"] == test_placement.placement_type


@pytest.mark.asyncio
async def test_update_placement(async_client: AsyncClient, test_placement):
    """Test PUT /api/placement/placements/{id} - Update placement."""
    update_data = {
        "visibility_level": "Prominent",
        "duration_seconds": 8.0
    }
    
    response = await async_client.put(
        f"/api/placement/placements/{test_placement.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["visibility_level"] == update_data["visibility_level"]


@pytest.mark.asyncio
async def test_approve_placement(async_client: AsyncClient, test_placement):
    """Test POST /api/placement/placements/{id}/approve - Approve placement."""
    approval_data = {
        "approved_by": str(PydanticObjectId()),
        "notes": "Approved for production"
    }
    
    response = await async_client.post(
        f"/api/placement/placements/{test_placement.id}/approve",
        json=approval_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["approval_status"] == "Approved"


@pytest.mark.asyncio
async def test_delete_placement(async_client: AsyncClient, test_product):
    """Test DELETE /api/placement/placements/{id} - Delete placement."""
    # Create temporary placement
    placement = ProductPlacement(
        product_id=test_product.id,
        project_id=str(PydanticObjectId()),
        scene_id=str(PydanticObjectId()),
        placement_type="Test"
    )
    await placement.insert()
    
    response = await async_client.delete(f"/api/placement/placements/{placement.id}")
    assert response.status_code == 200


# ============================================================================
# Analytics Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_analytics(async_client: AsyncClient, test_placement):
    """Test GET /api/placement/analytics - Get analytics data."""
    response = await async_client.get("/api/placement/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_placements" in data
    assert "total_products" in data
    assert "total_brands" in data


@pytest.mark.asyncio
async def test_ethics_audit(async_client: AsyncClient, test_placement):
    """Test GET /api/placement/ethics/audit - Ethics compliance audit."""
    response = await async_client.get("/api/placement/ethics/audit")
    assert response.status_code == 200
    data = response.json()
    assert "total_items_reviewed" in data
    assert "ethics_summary" in data
    assert "Fit" in data["ethics_summary"]
    assert "Neutral" in data["ethics_summary"]
    assert "Conflict" in data["ethics_summary"]


# ============================================================================
# Ethics Validation Tests
# ============================================================================

@pytest.mark.asyncio
async def test_brand_ethics_status_validation(async_client: AsyncClient):
    """Test ethics_status validation on brand creation."""
    invalid_data = {
        "name": "Invalid Ethics Brand",
        "ethics_status": "InvalidStatus"  # Should fail
    }
    
    response = await async_client.post("/api/placement/brands", json=invalid_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_product_dhamma_score_range(async_client: AsyncClient, test_brand):
    """Test dhamma_alignment_score range validation (0-100)."""
    invalid_data = {
        "brand_id": str(test_brand.id),
        "name": "Invalid Score Product",
        "dhamma_alignment_score": 150  # Should fail (> 100)
    }
    
    response = await async_client.post("/api/placement/products", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_placement_visibility_level_validation(async_client: AsyncClient, test_product):
    """Test visibility_level enum validation."""
    invalid_data = {
        "product_id": str(test_product.id),
        "project_id": str(PydanticObjectId()),
        "scene_id": str(PydanticObjectId()),
        "placement_type": "Prop",
        "visibility_level": "InvalidVisibility"  # Should fail
    }
    
    response = await async_client.post("/api/placement/placements", json=invalid_data)
    assert response.status_code == 422


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_nonexistent_brand(async_client: AsyncClient):
    """Test GET brand with invalid ID returns 404."""
    fake_id = str(PydanticObjectId())
    response = await async_client.get(f"/api/placement/brands/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_nonexistent_product(async_client: AsyncClient):
    """Test PUT product with invalid ID returns 404."""
    fake_id = str(PydanticObjectId())
    response = await async_client.put(
        f"/api/placement/products/{fake_id}",
        json={"name": "Updated"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_placement(async_client: AsyncClient):
    """Test DELETE placement with invalid ID returns 404."""
    fake_id = str(PydanticObjectId())
    response = await async_client.delete(f"/api/placement/placements/{fake_id}")
    assert response.status_code == 404
