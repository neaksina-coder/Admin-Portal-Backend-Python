# api/v1/reports.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from api import deps
from models.sale import Sale
from models.customer import Customer

router = APIRouter()


@router.get("/sales/summary")
def sales_summary(
    businessId: int = Query(...),
    startDate: datetime | None = Query(None),
    endDate: datetime | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    query = db.query(func.coalesce(func.sum(Sale.total_price), 0).label("total_revenue"))
    query = query.filter(Sale.business_id == businessId)
    if startDate:
        query = query.filter(Sale.transaction_date >= startDate)
    if endDate:
        query = query.filter(Sale.transaction_date <= endDate)
    total_revenue = query.scalar() or 0
    total_sales = (
        db.query(func.count(Sale.id))
        .filter(Sale.business_id == businessId)
        .scalar()
        or 0
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Sales summary",
        "data": {
            "totalRevenue": float(total_revenue),
            "totalSales": int(total_sales),
        },
    }


@router.get("/customers/summary")
def customers_summary(
    businessId: int = Query(...),
    startDate: datetime | None = Query(None),
    endDate: datetime | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    query = db.query(func.count(Customer.id)).filter(Customer.business_id == businessId)
    if startDate:
        query = query.filter(Customer.created_at >= startDate)
    if endDate:
        query = query.filter(Customer.created_at <= endDate)
    total_customers = query.scalar() or 0
    return {
        "success": True,
        "status_code": 200,
        "message": "Customers summary",
        "data": {"totalCustomers": int(total_customers)},
    }
