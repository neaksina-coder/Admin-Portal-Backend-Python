# api/v1/categories.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import category as crud_category
from models.user import User
from schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

router = APIRouter()


def _require_category_read(current_user: User = Depends(deps.require_roles(["admin", "customer_owner", "hr_admin"]))):
    return current_user


def _require_category_admin(current_user: User = Depends(deps.require_roles(["admin"]))):
    return current_user


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_category_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    existing = crud_category.get_category_by_slug(
        db, business_id=payload.business_id, slug=payload.slug
    )
    if existing:
        raise HTTPException(status_code=409, detail="Category slug already exists")

    category = crud_category.create_category(db, payload)
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Category created successfully",
        "data": category,
    }


@router.get("/", response_model=CategoryListResponse)
def list_categories(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    q: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_category_read),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    categories = crud_category.list_categories(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
        status=status_filter,
        q=q,
    )
    total = crud_category.count_categories(
        db,
        business_id=businessId,
        status=status_filter,
        q=q,
    )

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Categories retrieved successfully",
        "total": total,
        "data": categories,
    }


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_category_read),
):
    category = crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not current_user.is_superuser and current_user.business_id != category.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Category retrieved successfully",
        "data": category,
    }


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_category_admin),
):
    category = crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not current_user.is_superuser and current_user.business_id != category.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if payload.slug:
        existing = crud_category.get_category_by_slug(
            db, business_id=category.business_id, slug=payload.slug
        )
        if existing and existing.id != category.id:
            raise HTTPException(status_code=409, detail="Category slug already exists")

    updated = crud_category.update_category(db, category_id, payload)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Category updated successfully",
        "data": updated,
    }


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_category_admin),
):
    category = crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not current_user.is_superuser and current_user.business_id != category.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud_category.delete_category(db, category_id)
    return {"success": True, "message": "Category deleted successfully"}
