# api/v1/categories.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from schemas.category import (
    Category,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryDeleteResponse
)
from crud import category as crud_category
from api import deps

router = APIRouter()

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    """Create a new category"""
    # Check if slug already exists
    existing_category = crud_category.get_category_by_slug(db, slug=category.slug)
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category with this slug already exists"
        )
    
    new_category = crud_category.create_category(db=db, category=category)
    
    return {
        "success": True,
        "status_code": 201,
        "message": "Category created successfully",
        "data": new_category
    }

@router.get("/", response_model=CategoryListResponse)
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(deps.get_db)
):
    """Get all categories"""
    categories = crud_category.get_categories(
        db,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Categories retrieved successfully",
        "total": len(categories),
        "data": categories
    }

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get a specific category by ID"""
    category = crud_category.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Category retrieved successfully",
        "data": category
    }

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    """Update a category"""
    db_category = crud_category.update_category(db, category_id=category_id, category=category)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Category updated successfully",
        "data": db_category
    }

@router.delete("/{category_id}", response_model=CategoryDeleteResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    """Delete a category"""
    category = crud_category.delete_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Category deleted successfully",
        "id": category_id
    }
