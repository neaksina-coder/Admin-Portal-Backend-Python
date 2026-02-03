# api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import subscription as crud_subscription
from schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionListResponse,
)

router = APIRouter()


@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    sub_in: SubscriptionCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    sub = crud_subscription.create_subscription(db, sub_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "Subscription created successfully",
        "data": sub,
    }


@router.get("/", response_model=SubscriptionListResponse)
def list_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    businessId: int | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    subs = crud_subscription.list_subscriptions(
        db,
        skip=skip,
        limit=limit,
        business_id=businessId,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Subscriptions retrieved successfully",
        "total": len(subs),
        "data": subs,
    }


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    sub = crud_subscription.get_subscription(db, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Subscription retrieved successfully",
        "data": sub,
    }
