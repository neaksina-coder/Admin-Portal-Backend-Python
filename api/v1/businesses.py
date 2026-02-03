# api/v1/businesses.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import business as crud_business
from models.plan import Plan
from schemas.business import BusinessCreate, BusinessResponse, BusinessListResponse

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
        "plan": plan_payload,
        "status": business.status,
        "timestamps": {
            "created": business.created_at,
            "updated": business.updated_at,
        },
    }


@router.post("/", response_model=BusinessResponse, status_code=201)
def create_business(
    business_in: BusinessCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    business = crud_business.create_business(db, business_in)
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
