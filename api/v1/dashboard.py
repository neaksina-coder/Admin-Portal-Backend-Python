# api/v1/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta

from api import deps
from models.customer import Customer
from models.sale import Sale

router = APIRouter()


def _range_to_days(range_key: str) -> int:
    mapping = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "365d": 365,
    }
    return mapping.get(range_key, 7)


def _interval_key(interval: str) -> str:
    if interval in {"day", "week", "month"}:
        return interval
    return "day"


@router.get("/crm")
def crm_dashboard(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    now = datetime.utcnow()
    last_7 = now - timedelta(days=7)
    last_30 = now - timedelta(days=30)

    total_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.business_id == businessId)
        .scalar()
        or 0
    )

    new_customers_7d = (
        db.query(func.count(Customer.id))
        .filter(Customer.business_id == businessId, Customer.created_at >= last_7)
        .scalar()
        or 0
    )
    new_customers_30d = (
        db.query(func.count(Customer.id))
        .filter(Customer.business_id == businessId, Customer.created_at >= last_30)
        .scalar()
        or 0
    )

    segment_rows = (
        db.query(Customer.segment, func.count(Customer.id))
        .filter(Customer.business_id == businessId)
        .group_by(Customer.segment)
        .all()
    )
    customers_by_segment = [
        {"segment": seg or "unknown", "count": count} for seg, count in segment_rows
    ]

    churn_label = case(
        (Customer.churn_risk_score >= 0.7, "high"),
        (Customer.churn_risk_score >= 0.3, "medium"),
        else_="low",
    )
    churn_bucket = (
        db.query(churn_label, func.count(Customer.id))
        .filter(Customer.business_id == businessId, Customer.churn_risk_score.isnot(None))
        .group_by(churn_label)
        .all()
    )
    churn_summary = {bucket: count for bucket, count in churn_bucket}

    lifetime_total = (
        db.query(func.coalesce(func.sum(Customer.lifetime_value), 0))
        .filter(Customer.business_id == businessId)
        .scalar()
        or 0
    )
    lifetime_avg = (
        db.query(func.coalesce(func.avg(Customer.lifetime_value), 0))
        .filter(Customer.business_id == businessId)
        .scalar()
        or 0
    )

    next_best_rows = (
        db.query(Customer.next_best_product, func.count(Customer.id))
        .filter(Customer.business_id == businessId, Customer.next_best_product.isnot(None))
        .group_by(Customer.next_best_product)
        .order_by(func.count(Customer.id).desc())
        .limit(5)
        .all()
    )
    top_next_best_product = [
        {"product": product, "count": count} for product, count in next_best_rows
    ]

    return {
        "success": True,
        "status_code": 200,
        "message": "CRM dashboard summary",
        "data": {
            "totalCustomers": total_customers,
            "newCustomers7d": new_customers_7d,
            "newCustomers30d": new_customers_30d,
            "customersBySegment": customers_by_segment,
            "churnRiskSummary": churn_summary,
            "lifetimeValueTotal": lifetime_total,
            "lifetimeValueAverage": lifetime_avg,
            "topNextBestProduct": top_next_best_product,
        },
    }


@router.get("/overview")
def dashboard_overview(
    businessId: int = Query(...),
    range: str = Query("7d"),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    days = _range_to_days(range)
    now = datetime.utcnow()
    start = now - timedelta(days=days)
    prev_start = start - timedelta(days=days)

    orders_count = (
        db.query(func.count(Sale.id))
        .filter(Sale.business_id == businessId, Sale.transaction_date >= start)
        .scalar()
        or 0
    )
    sales_total = (
        db.query(func.coalesce(func.sum(Sale.total_price), 0))
        .filter(Sale.business_id == businessId, Sale.transaction_date >= start)
        .scalar()
        or 0
    )
    profit_total = (
        db.query(func.coalesce(func.sum(Sale.total_price - func.coalesce(Sale.discount_amount, 0)), 0))
        .filter(Sale.business_id == businessId, Sale.transaction_date >= start)
        .scalar()
        or 0
    )
    prev_sales_total = (
        db.query(func.coalesce(func.sum(Sale.total_price), 0))
        .filter(
            Sale.business_id == businessId,
            Sale.transaction_date >= prev_start,
            Sale.transaction_date < start,
        )
        .scalar()
        or 0
    )
    customers_new = (
        db.query(func.count(Customer.id))
        .filter(Customer.business_id == businessId, Customer.created_at >= start)
        .scalar()
        or 0
    )

    growth_pct = 0.0
    if prev_sales_total:
        growth_pct = ((sales_total - prev_sales_total) / prev_sales_total) * 100

    return {
        "success": True,
        "status_code": 200,
        "message": "Dashboard overview",
        "data": {
            "ordersCount": int(orders_count),
            "salesTotal": float(sales_total),
            "profitTotal": float(profit_total),
            "customersNew": int(customers_new),
            "growthPct": float(round(growth_pct, 2)),
            "prevSalesTotal": float(prev_sales_total),
            "rangeDays": days,
        },
    }


@router.get("/revenue-series")
def revenue_series(
    businessId: int = Query(...),
    range: str = Query("7d"),
    interval: str = Query("day"),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    days = _range_to_days(range)
    interval_key = _interval_key(interval)
    start = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(
            func.date_trunc(interval_key, Sale.transaction_date).label("period"),
            func.coalesce(func.sum(Sale.total_price), 0).label("value"),
        )
        .filter(Sale.business_id == businessId, Sale.transaction_date >= start)
        .group_by("period")
        .order_by("period")
        .all()
    )
    data = [
        {"period": period.isoformat() if period else None, "value": float(value or 0)}
        for period, value in rows
    ]
    return {
        "success": True,
        "status_code": 200,
        "message": "Revenue series",
        "data": data,
    }


@router.get("/orders-series")
def orders_series(
    businessId: int = Query(...),
    range: str = Query("7d"),
    interval: str = Query("day"),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    days = _range_to_days(range)
    interval_key = _interval_key(interval)
    start = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(
            func.date_trunc(interval_key, Sale.transaction_date).label("period"),
            func.count(Sale.id).label("value"),
        )
        .filter(Sale.business_id == businessId, Sale.transaction_date >= start)
        .group_by("period")
        .order_by("period")
        .all()
    )
    data = [
        {"period": period.isoformat() if period else None, "value": int(value or 0)}
        for period, value in rows
    ]
    return {
        "success": True,
        "status_code": 200,
        "message": "Orders series",
        "data": data,
    }


@router.get("/customers-series")
def customers_series(
    businessId: int = Query(...),
    range: str = Query("7d"),
    interval: str = Query("day"),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    days = _range_to_days(range)
    interval_key = _interval_key(interval)
    start = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(
            func.date_trunc(interval_key, Customer.created_at).label("period"),
            func.count(Customer.id).label("value"),
        )
        .filter(Customer.business_id == businessId, Customer.created_at >= start)
        .group_by("period")
        .order_by("period")
        .all()
    )
    data = [
        {"period": period.isoformat() if period else None, "value": int(value or 0)}
        for period, value in rows
    ]
    return {
        "success": True,
        "status_code": 200,
        "message": "Customers series",
        "data": data,
    }


@router.get("/segments")
def customer_segments(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    segment_rows = (
        db.query(Customer.segment, func.count(Customer.id))
        .filter(Customer.business_id == businessId)
        .group_by(Customer.segment)
        .all()
    )
    data = [{"segment": seg or "unknown", "count": count} for seg, count in segment_rows]
    return {
        "success": True,
        "status_code": 200,
        "message": "Customer segments",
        "data": data,
    }


@router.get("/churn-risk")
def churn_risk_summary(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    churn_label = case(
        (Customer.churn_risk_score >= 0.7, "high"),
        (Customer.churn_risk_score >= 0.3, "medium"),
        else_="low",
    )
    churn_bucket = (
        db.query(churn_label, func.count(Customer.id))
        .filter(Customer.business_id == businessId, Customer.churn_risk_score.isnot(None))
        .group_by(churn_label)
        .all()
    )
    data = [{"bucket": bucket, "count": count} for bucket, count in churn_bucket]
    return {
        "success": True,
        "status_code": 200,
        "message": "Churn risk summary",
        "data": data,
    }
