# api/v1/businesses.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import audit_log as crud_audit_log
from crud import business as crud_business
from models.plan import Plan
from schemas.business import (
    BusinessCreate,
    BusinessListResponse,
    BusinessResponse,
    BusinessSuspendRequest,
)
from utils.alert_templates import build_alert
from utils.telegram import send_telegram_alert

router = APIRouter()


def _serialize_business_with_plan(db: Session, business):
    plan_payload = None
    if business.plan_id:
        plan = db.query(Plan).filter(Plan.id == business.plan_id).first()
        if plan:
            plan_payload = {"id": plan.id, "name": plan.plan_name}
    return {
        "id": business.id,
        "name": business.name,
        "tenantId": business.tenant_id,
        "planId": business.plan_id,
        "plan": plan_payload,
        "status": business.status,
        "suspendedAt": business.suspended_at,
        "suspendedReason": business.suspended_reason,
        "timestamps": {
            "created": business.created_at,
            "updated": business.updated_at,
        },
    }


@router.post("/", response_model=BusinessResponse, status_code=201)
def create_business(
    business_in: BusinessCreate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    business = crud_business.create_business(db, business_in)
    crud_audit_log.create_audit_log(
        db,
        action="business_created",
        actor_user_id=current_user.id,
        business_id=business.id,
        target_type="business",
        target_id=business.id,
        metadata_json={"name": business.name, "tenantId": business.tenant_id},
    )
    db.commit()

    send_telegram_alert(
        build_alert(
            title="Business Created",
            level="success",
            fields=[
                ("Business ID", business.id),
                ("Name", business.name),
                ("Tenant ID", business.tenant_id),
                ("By User ID", current_user.id),
            ],
        ),
        level="success",
    )

    return {
        "success": True,
        "status_code": 201,
        "message": "Business created successfully",
        "data": _serialize_business_with_plan(db, business),
    }


@router.get("/", response_model=BusinessListResponse)
def list_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    businesses = crud_business.list_businesses(db, skip=skip, limit=limit)
    return {
        "success": True,
        "status_code": 200,
        "message": "Businesses retrieved successfully",
        "total": len(businesses),
        "data": [_serialize_business_with_plan(db, business) for business in businesses],
    }


@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(
    business_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    business = crud_business.get_business(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Business retrieved successfully",
        "data": _serialize_business_with_plan(db, business),
    }


@router.put("/{business_id}/suspend", response_model=BusinessResponse)
def suspend_business(
    business_id: int,
    payload: BusinessSuspendRequest,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    business = crud_business.suspend_business(db, business_id, reason=payload.reason)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    crud_audit_log.create_audit_log(
        db,
        action="business_suspended",
        actor_user_id=current_user.id,
        business_id=business.id,
        target_type="business",
        target_id=business.id,
        metadata_json={"reason": payload.reason},
    )
    db.commit()

    send_telegram_alert(
        build_alert(
            title="Business Suspended",
            level="warning",
            fields=[
                ("Business ID", business.id),
                ("Reason", payload.reason),
                ("By User ID", current_user.id),
            ],
        ),
        level="warning",
    )

    return {
        "success": True,
        "status_code": 200,
        "message": "Business suspended successfully",
        "data": _serialize_business_with_plan(db, business),
    }


@router.put("/{business_id}/unsuspend", response_model=BusinessResponse)
def unsuspend_business(
    business_id: int,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    business = crud_business.unsuspend_business(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    crud_audit_log.create_audit_log(
        db,
        action="business_unsuspended",
        actor_user_id=current_user.id,
        business_id=business.id,
        target_type="business",
        target_id=business.id,
    )
    db.commit()

    send_telegram_alert(
        build_alert(
            title="Business Unsuspended",
            level="success",
            fields=[
                ("Business ID", business.id),
                ("By User ID", current_user.id),
            ],
        ),
        level="success",
    )

    return {
        "success": True,
        "status_code": 200,
        "message": "Business unsuspended successfully",
        "data": _serialize_business_with_plan(db, business),
    }
