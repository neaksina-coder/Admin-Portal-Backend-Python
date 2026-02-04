# api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import audit_log as crud_audit_log
from crud import subscription as crud_subscription
from crud import subscription_event as crud_subscription_event
from schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionListResponse,
)
from schemas.subscription_event import SubscriptionEventListResponse
from utils.alert_templates import build_alert
from utils.telegram import send_telegram_alert

router = APIRouter()


@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    sub_in: SubscriptionCreate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    sub = crud_subscription.create_subscription(db, sub_in)
    crud_audit_log.create_audit_log(
        db,
        action="subscription_created",
        actor_user_id=current_user.id,
        business_id=sub.business_id,
        target_type="subscription",
        target_id=sub.id,
        metadata_json={"planId": sub.plan_id, "status": sub.status},
    )
    db.commit()

    send_telegram_alert(
        build_alert(
            title="Subscription Created",
            level="info",
            fields=[
                ("Subscription ID", sub.id),
                ("Business ID", sub.business_id),
                ("Plan ID", sub.plan_id),
                ("Status", sub.status),
                ("By User ID", current_user.id),
            ],
        ),
        level="info",
    )

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


@router.get("/{subscription_id}/events", response_model=SubscriptionEventListResponse)
def get_subscription_events(
    subscription_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    sub = crud_subscription.get_subscription(db, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    events = crud_subscription_event.list_subscription_events(
        db,
        subscription_id=subscription_id,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Subscription events retrieved successfully",
        "total": len(events),
        "data": events,
    }
