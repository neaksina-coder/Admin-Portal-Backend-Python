# api/v1/sales.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from api import deps
from crud import sale as crud_sale
from schemas.sale import SaleCreate, SaleResponse, SaleListResponse
from models.user import User

router = APIRouter()


def _require_sales_read(current_user: User = Depends(deps.require_roles(["admin", "customer_owner", "hr_admin"]))):
    return current_user


def _require_sales_admin(current_user: User = Depends(deps.require_roles(["admin"]))):
    return current_user


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(
    sale_in: SaleCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_sales_admin),
):
    if not current_user.is_superuser and current_user.business_id != sale_in.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    sale = crud_sale.create_sale(db, sale_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "Sale created successfully",
        "data": sale,
    }


@router.get("/", response_model=SaleListResponse)
def list_sales(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    startDate: datetime | None = Query(None),
    endDate: datetime | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_sales_read),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    sales = crud_sale.list_sales(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
        start_date=startDate,
        end_date=endDate,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Sales retrieved successfully",
        "total": len(sales),
        "data": sales,
    }


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_sales_read),
):
    sale = crud_sale.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if not current_user.is_superuser and current_user.business_id != sale.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return {
        "success": True,
        "status_code": 200,
        "message": "Sale retrieved successfully",
        "data": sale,
    }
