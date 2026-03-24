# api/v1/business_account.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import deps
from crud import business as crud_business
from models.plan import Plan
from schemas.business import BusinessAccountUpdate, BusinessResponse

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


@router.get("/me", response_model=BusinessResponse)
def get_business_account(
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    if not current_user.business_id:
        raise HTTPException(status_code=404, detail="Business not assigned")
    business = crud_business.get_business(db, current_user.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Business account retrieved successfully",
        "data": _serialize_business_with_plan(db, business),
    }

# @router.put("/me/plan", response_class=BusinessResponse)
# def update_business_plan(
#     db : Session = Depends(deps.get_db),
#     current_user = Depends(deps.get_current_user),
# ):
#     if not current_user.business_id:
#         raise HTTPException(status_code= 404, detail= "Business Not Assigned yet ")
#     return{
#         "success": True,
#         "status_code": 200,
#         "message": "Business Plane Updated Succcessfully",
#         "data": crud_business.update_business_plan(db, current_user.business_id)
#     }


@router.put("/me", response_model=BusinessResponse)
def update_business_account(
    payload: BusinessAccountUpdate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    if not current_user.business_id:
        raise HTTPException(status_code=404, detail="Business not assigned")
    business = crud_business.get_business(db, current_user.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    updated = crud_business.update_business_account(db, business, payload)
    return {
        "success": True,
        "status_code": 200,
        "message": "Business account updated successfully",
        "data": _serialize_business_with_plan(db, updated),
    }



# @router.delete("/me", response_class=BusinessResponse)
# def delete_bisiness_account(
#     payload: BusinessAccountUpdate,
#     db: Session = Depends(deps.get_db),
#     current_user = Depends(deps.get_current_user)

# ):
#     if not current_user.business_id:
#         raise HTTPException(status_code=404, detail="Business not assigned")
#     business = crud_business.get_business(db, current_user.business_id)
#     if not business:
#         raise HTTPException(status_code=404, detail="Business not found")
#     return {
#         "success" : True,
#          "status_code" : 200,
#          "message" : "Business Account has been deleted successfully",
#          "data" : crud_business.delete_business_account(db, business)
#     }