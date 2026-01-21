# api/v1/products.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from schemas.product import (
    Product, 
    ProductCreate, 
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductDeleteResponse
)
from crud import product as crud_product
from api import deps

router = APIRouter()

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    """Create a new product"""
    # Check if SKU already exists
    existing_product = crud_product.get_product_by_sku(db, sku=product.sku)
    if existing_product:
        raise HTTPException(
            status_code=400, 
            detail="Product with this SKU already exists"
        )
    
    new_product = crud_product.create_product(db=db, product=product)
    
    return {
    "success": True,
    "status_code": 201,
    "message": "Product created successfully",
    "data": new_product
    }


@router.get("/", response_model=ProductListResponse)
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None,  # Changed from category
    status: Optional[str] = None,
    db: Session = Depends(deps.get_db)
):
    """Get all products with optional filters"""
    products = crud_product.get_products(
        db, 
        skip=skip, 
        limit=limit,
        category_id=category_id,  # Changed
        status=status
    )
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Products retrieved successfully",
        "total": len(products),
        "data": products
    }

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get a specific product by ID"""
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Product retrieved successfully",
        "data": product
    }

@router.get("/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(
    sku: str,
    db: Session = Depends(deps.get_db)
):
    """Get a specific product by SKU"""
    product = crud_product.get_product_by_sku(db, sku=sku)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,          # ← ADD THIS
        "status_code": 200,       # ← ADD THIS
        "message": "Product retrieved successfully",
        "data": product
    }
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    """Update a product"""
    # If updating SKU, check it doesn't conflict
    if product.sku:
        existing = crud_product.get_product_by_sku(db, sku=product.sku)
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=400,
                detail="Product with this SKU already exists"
            )
    
    db_product = crud_product.update_product(db, product_id=product_id, product=product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Product updated successfully",
        "data": db_product
    }

@router.delete("/{product_id}", response_model=ProductDeleteResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    """Delete a product"""
    product = crud_product.delete_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Product deleted successfully",
        "id": product_id
    }
