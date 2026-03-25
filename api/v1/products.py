# api/v1/products.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import product as crud_product
from crud import category as crud_category
from models.user import User
from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter()


def _require_product_read(current_user: User = Depends(deps.require_roles(["admin", "customer_owner", "hr_admin"]))):
    return current_user


def _require_product_admin(current_user: User = Depends(deps.require_roles(["admin"]))):
    return current_user


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_product_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    existing = crud_product.get_product_by_sku(
        db, business_id=payload.business_id, sku=payload.sku
    )
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")

    if payload.category_id is not None:
        category = crud_category.get_category(db, payload.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        if category.business_id != payload.business_id:
            raise HTTPException(status_code=400, detail="Category does not belong to business")

    product = crud_product.create_product(db, payload)
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Product created successfully",
        "data": product,
    }


@router.get("/", response_model=ProductListResponse)
def list_products(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    q: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_product_read),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    products = crud_product.list_products(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
        category_id=category_id,
        status=status_filter,
        q=q,
    )
    total = crud_product.count_products(
        db,
        business_id=businessId,
        category_id=category_id,
        status=status_filter,
        q=q,
    )

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Products retrieved successfully",
        "total": total,
        "data": products,
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_product_read),
):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and current_user.business_id != product.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Product retrieved successfully",
        "data": product,
    }


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_product_admin),
):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and current_user.business_id != product.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if payload.sku:
        existing = crud_product.get_product_by_sku(
            db, business_id=product.business_id, sku=payload.sku
        )
        if existing and existing.id != product.id:
            raise HTTPException(status_code=409, detail="SKU already exists")

    if payload.category_id is not None:
        category = crud_category.get_category(db, payload.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        if category.business_id != product.business_id:
            raise HTTPException(status_code=400, detail="Category does not belong to business")

    updated = crud_product.update_product(db, product_id, payload)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Product updated successfully",
        "data": updated,
    }


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_product_admin),
):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and current_user.business_id != product.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud_product.delete_product(db, product_id)
    return {"success": True, "message": "Product deleted successfully"}
