# api/v1/hr_leave_policies.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import leave_balances as crud_leave_balances
from crud import leave_policies as crud_leave_policies
from crud import leave_types as crud_leave_types
from models.user import User
from schemas.leave_balance import (
    LeaveBalanceAdjustRequest,
    LeaveBalanceListResponse,
    LeaveBalanceResponse,
)
from schemas.leave_policy import (
    LeavePolicyCreate,
    LeavePolicyListResponse,
    LeavePolicyResponse,
    LeavePolicyUpdate,
)
from schemas.leave_type import (
    LeaveTypeCreate,
    LeaveTypeListResponse,
    LeaveTypeResponse,
    LeaveTypeUpdate,
)

router = APIRouter()


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


@router.post("/leave-types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
def create_leave_type(
    payload: LeaveTypeCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    item = crud_leave_types.create_leave_type(db, payload)
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Leave type created",
        "data": item,
    }


@router.get("/leave-types", response_model=LeaveTypeListResponse)
def list_leave_types(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.is_superuser:
        business_id = businessId
    elif current_user.role in {"customer_owner", "hr_admin", "employee"}:
        if current_user.business_id != businessId:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        business_id = businessId
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    items = crud_leave_types.list_leave_types(db, business_id)
    if current_user.role == "employee":
        items = [item for item in items if item.is_active]
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave types retrieved",
        "total": len(items),
        "data": items,
    }


@router.put("/leave-types/{leave_type_id}", response_model=LeaveTypeResponse)
def update_leave_type(
    leave_type_id: int,
    payload: LeaveTypeUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    item = crud_leave_types.get_leave_type(db, leave_type_id)
    if not item:
        raise HTTPException(status_code=404, detail="Leave type not found")
    if not current_user.is_superuser and current_user.business_id != item.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    item = crud_leave_types.update_leave_type(db, item, payload)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave type updated",
        "data": item,
    }


@router.post("/leave-policies", response_model=LeavePolicyResponse, status_code=status.HTTP_201_CREATED)
def create_leave_policy(
    payload: LeavePolicyCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    leave_type = crud_leave_types.get_leave_type(db, payload.leave_type_id)
    if not leave_type or leave_type.business_id != payload.business_id:
        raise HTTPException(status_code=400, detail="Invalid leave type")
    existing = crud_leave_policies.get_policy_by_type(db, payload.business_id, payload.leave_type_id)
    if existing:
        item = crud_leave_policies.update_policy(
            db,
            existing,
            LeavePolicyUpdate(
                annual_allowance=payload.annual_allowance,
                accrual_method=payload.accrual_method,
                carryover_days=payload.carryover_days,
                max_balance=payload.max_balance,
                allow_negative=payload.allow_negative,
            ),
        )
    else:
        item = crud_leave_policies.create_policy(db, payload)
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Leave policy saved",
        "data": item,
    }

@router.get("/leave-po      licies", response_model=LeavePolicyListResponse)
def list_leave_policies(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.is_superuser:
        business_id = businessId
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != businessId:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        business_id = businessId
    # elif current_user.role == "employee":
    #     if current_user.business_id != businessId: 
    #         raise HTTPException(status_code=403, detail="Not Permissions to view policies of another business")
    #     business_id = businessId
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    items = crud_leave_policies.list_policies(db, business_id)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave policies retrieved",
        "total": len(items),
        "data": items,
    }


@router.put("/leave-policies/{policy_id}", response_model=LeavePolicyResponse)
def update_leave_policy(
    policy_id: int,
    payload: LeavePolicyUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    policy = crud_leave_policies.get_leave_policy(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Leave policy not found")
    if not current_user.is_superuser and current_user.business_id != policy.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    policy = crud_leave_policies.update_policy(db, policy, payload)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave policy updated",
        "data": policy,
    }


@router.get("/leave-balances", response_model=LeaveBalanceListResponse)
def list_leave_balances(
    businessId: int = Query(...),
    userId: int | None = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.is_superuser:
        business_id = businessId
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != businessId:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        business_id = businessId
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    items = crud_leave_balances.list_balances(db, business_id, user_id=userId)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave balances retrieved",
        "total": len(items),
        "data": items,
    }


@router.get("/leave-balances/me", response_model=LeaveBalanceListResponse)
def list_my_leave_balances(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    items = crud_leave_balances.list_balances(db, current_user.business_id, user_id=current_user.id)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave balances retrieved",
        "total": len(items),
        "data": items,
    }


@router.post("/leave-balances/{user_id}/adjust", response_model=LeaveBalanceResponse)
def adjust_leave_balance(
    user_id: int,
    payload: LeaveBalanceAdjustRequest,
    leaveTypeId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    balance = crud_leave_balances.get_balance(db, user_id=user_id, leave_type_id=leaveTypeId)
    if not balance:
        raise HTTPException(status_code=404, detail="Leave balance not found")
    if not current_user.is_superuser and current_user.business_id != balance.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = crud_leave_balances.adjust_balance(
        db,
        balance,
        change=payload.change,
        reason=payload.reason or "manual_adjust",
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave balance adjusted",
        "data": updated,
    }
