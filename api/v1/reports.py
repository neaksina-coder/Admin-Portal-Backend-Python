# api/v1/reports.py
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api import deps
from models.customer import Customer
from models.invoice import Invoice
from models.sale import Sale

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


@router.get("/payments")
def payments_report(
    businessId: int | None = Query(None),
    status: str | None = Query(None, description="pending|paid|failed|refunded|overdue"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    query = db.query(Invoice)
    if businessId is not None:
        query = query.filter(Invoice.business_id == businessId)

    status_normalized = (status or "").strip().lower()
    if status_normalized == "overdue":
        query = query.filter(
            Invoice.payment_status == "pending",
            Invoice.due_date.isnot(None),
            Invoice.due_date < date.today(),
        )
    elif status_normalized:
        query = query.filter(Invoice.payment_status == status_normalized)

    invoices = (
        query.order_by(Invoice.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total_amount = sum(float(item.amount or 0) for item in invoices)
    data = [
        {
            "id": item.id,
            "businessId": item.business_id,
            "subscriptionId": item.subscription_id,
            "amount": float(item.amount or 0),
            "currency": item.currency,
            "paymentStatus": item.payment_status,
            "paymentMethod": item.payment_method,
            "dueDate": item.due_date,
            "paymentDate": item.payment_date,
            "metadata": item.metadata_json,
            "created_at": item.created_at,
        }
        for item in invoices
    ]

    return {
        "success": True,
        "status_code": 200,
        "message": "Payments report",
        "total": len(data),
        "summary": {
            "totalAmount": total_amount,
            "currency": data[0]["currency"] if data else None,
        },
        "data": data,
    }
