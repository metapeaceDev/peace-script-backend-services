"""
Product Placement Schemas Tests
================================
Test suite for Pydantic schemas validation (BrandCreate, ProductCreate, ProductPlacementCreate, etc.).
"""

import pytest
from pydantic import ValidationError
from beanie import PydanticObjectId

from dmm_backend.schemas_placement import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductPlacementCreate,
    ProductPlacementUpdate,
    ProductPlacementResponse
)


# ============================================================================
# Brand Schema Tests
# ============================================================================

def test_brand_create_valid():
    """Test BrandCreate with valid data."""
    data = {
        "name": "Test Brand",
        "logo_url": "https://example.com/logo.png",
        "website": "https://testbrand.com",
        "description": "Test brand description",
        "industry": "Technology"
    }
    brand = BrandCreate(**data)
    assert brand.name == "Test Brand"
    assert brand.industry == "Technology"


def test_brand_create_minimal():
    """Test BrandCreate with minimal required fields."""
    brand = BrandCreate(name="Minimal Brand")
    assert brand.name == "Minimal Brand"
    assert brand.logo_url is None
    assert brand.website is None


def test_brand_update_partial():
    """Test BrandUpdate allows partial updates."""
    update = BrandUpdate(description="Updated description")
    assert update.description == "Updated description"
    assert update.name is None  # Optional


def test_brand_response_serialization():
    """Test BrandResponse includes id field."""
    data = {
        "id": str(PydanticObjectId()),
        "name": "Response Test Brand",
        "logo_url": "https://example.com/logo.png",
        "ethics_status": "Fit",
        "dhamma_alignment_score": 85,
        "approval_status": "Approved"
    }
    brand = BrandResponse(**data)
    assert brand.id == data["id"]
    assert brand.name == "Response Test Brand"


# ============================================================================
# Product Schema Tests
# ============================================================================

def test_product_create_valid():
    """Test ProductCreate with valid data."""
    data = {
        "brand_id": str(PydanticObjectId()),
        "name": "Test Product",
        "category": "Electronics",
        "description": "Test product description",
        "image_url": "https://example.com/product.png"
    }
    product = ProductCreate(**data)
    assert product.name == "Test Product"
    assert product.category == "Electronics"


def test_product_create_minimal():
    """Test ProductCreate with required fields only."""
    product = ProductCreate(
        brand_id=str(PydanticObjectId()),
        name="Minimal Product",
        category="Electronics"
    )
    assert product.name == "Minimal Product"
    assert product.description is None


def test_product_update_partial():
    """Test ProductUpdate allows partial updates."""
    update = ProductUpdate(
        name="Updated Product Name",
        description="Updated description"
    )
    assert update.name == "Updated Product Name"
    assert update.category is None  # Optional


def test_product_response_with_brand_id():
    """Test ProductResponse includes brand_id."""
    data = {
        "id": str(PydanticObjectId()),
        "brand_id": str(PydanticObjectId()),
        "name": "Response Test Product",
        "category": "Technology",
        "ethics_status": "Neutral",
        "approval_status": "Pending"
    }
    product = ProductResponse(**data)
    assert product.id is not None
    assert product.brand_id is not None


# ============================================================================
# ProductPlacement Schema Tests
# ============================================================================

def test_placement_create_valid():
    """Test ProductPlacementCreate with valid data."""
    data = {
        "product_id": str(PydanticObjectId()),
        "project_id": str(PydanticObjectId()),
        "scene_id": str(PydanticObjectId()),
        "placement_type": "Prop",
        "visibility_level": "Prominent",
        "duration_seconds": 5.5,
        "screen_position": "Center",
        "context_description": "Product on desk in office scene"
    }
    placement = ProductPlacementCreate(**data)
    assert placement.placement_type == "Prop"
    assert placement.visibility_level == "Prominent"
    assert placement.duration_seconds == 5.5


def test_placement_create_minimal():
    """Test ProductPlacementCreate with required fields only."""
    placement = ProductPlacementCreate(
        product_id=str(PydanticObjectId()),
        project_id=str(PydanticObjectId()),
        scene_id=str(PydanticObjectId()),
        placement_type="Background"
    )
    assert placement.placement_type == "Background"
    assert placement.visibility_level is None


def test_placement_update_partial():
    """Test ProductPlacementUpdate allows partial updates."""
    update = ProductPlacementUpdate(
        visibility_level="Featured",
        duration_seconds=10.0
    )
    assert update.visibility_level == "Featured"
    assert update.placement_type is None  # Optional


def test_placement_response_complete():
    """Test ProductPlacementResponse with all fields."""
    data = {
        "id": str(PydanticObjectId()),
        "product_id": str(PydanticObjectId()),
        "project_id": str(PydanticObjectId()),
        "scene_id": str(PydanticObjectId()),
        "placement_type": "Prop",
        "visibility_level": "Prominent",
        "duration_seconds": 7.5,
        "ethics_review_status": "Approved",
        "approval_status": "Approved"
    }
    placement = ProductPlacementResponse(**data)
    assert placement.id is not None
    assert placement.product_id is not None
    assert placement.placement_type == "Prop"
