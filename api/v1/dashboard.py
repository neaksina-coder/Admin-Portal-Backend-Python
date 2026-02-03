# api/v1/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta

from api import deps
from models.customer import Customer

router = APIRouter()


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
