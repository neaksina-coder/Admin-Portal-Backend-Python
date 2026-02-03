# api/v1/sales.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from api import deps
from crud import sale as crud_sale
from schemas.sale import SaleCreate, SaleResponse, SaleListResponse

router = APIRouter()


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(
    sale_in: SaleCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
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
    _: dict = Depends(deps.require_roles(["admin"])),
):
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
    _: dict = Depends(deps.require_roles(["admin"])),
):
    sale = crud_sale.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Sale retrieved successfully",
        "data": sale,
    }

