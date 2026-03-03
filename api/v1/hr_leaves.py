# api/v1/hr_leaves.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import leave_request as crud_leave
from models.user import User
from schemas.leave_request import (
    LeaveRequestCreate,
    LeaveDecisionRequest,
    LeaveRequestListResponse,
    LeaveRequestResponse,
    LeaveRequestUpdate,
)

router = APIRouter()


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


@router.get("/", response_model=LeaveRequestListResponse)
def list_leave_requests(
    businessId: int = Query(...),
    status_filter: str | None = Query(None, alias="status"),
    userId: int | None = Query(None, alias="userId"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.is_superuser:
        business_id = businessId
        target_user_id = userId
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != businessId:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        business_id = businessId
        target_user_id = userId
    elif current_user.role == "employee":
        business_id = current_user.business_id
        target_user_id = current_user.id
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    leaves = crud_leave.list_leave_requests(
        db,
        business_id=business_id,
        user_id=target_user_id,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave requests retrieved successfully",
        "total": len(leaves),
        "data": leaves,
    }


@router.get("/{request_id}", response_model=LeaveRequestResponse)
def get_leave_request(
    request_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    leave_request = crud_leave.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if current_user.is_superuser:
        pass
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != leave_request.business_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "employee":
        if leave_request.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave request retrieved successfully",
        "data": leave_request,
    }


@router.post("/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def create_leave_request(
    payload: LeaveRequestCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role == "employee":
        business_id = current_user.business_id
        user_id = current_user.id
    elif current_user.role in {"customer_owner", "hr_admin"} or current_user.is_superuser:
        if not payload.business_id or not payload.user_id:
            raise HTTPException(status_code=400, detail="businessId and userId are required")
        business_id = payload.business_id
        user_id = payload.user_id
        if not current_user.is_superuser and current_user.business_id != business_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    leave_request = crud_leave.create_leave_request(
        db,
        payload,
        business_id=business_id,
        user_id=user_id,
    )
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Leave request created successfully",
        "data": leave_request,
    }


@router.put("/{request_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    request_id: int,
    payload: LeaveRequestUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    leave_request = crud_leave.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if current_user.is_superuser:
        pass
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != leave_request.business_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "employee":
        if leave_request.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        if payload.status and payload.status != leave_request.status:
            raise HTTPException(status_code=403, detail="Employees cannot change status")
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = crud_leave.update_leave_request(db, leave_request, payload)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave request updated successfully",
        "data": updated,
    }


@router.post("/{request_id}/approve", response_model=LeaveRequestResponse)
def approve_leave_request(
    request_id: int,
    payload: LeaveDecisionRequest | None = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    leave_request = crud_leave.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if not current_user.is_superuser and current_user.business_id != leave_request.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    approved = crud_leave.approve_leave_request(
        db,
        leave_request,
        approved_by_user_id=current_user.id,
        status="approved",
        decision_note=payload.note if payload else None,
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave request approved",
        "data": approved,
    }


@router.post("/{request_id}/reject", response_model=LeaveRequestResponse)
def reject_leave_request(
    request_id: int,
    payload: LeaveDecisionRequest | None = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    leave_request = crud_leave.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if not current_user.is_superuser and current_user.business_id != leave_request.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    rejected = crud_leave.approve_leave_request(
        db,
        leave_request,
        approved_by_user_id=current_user.id,
        status="rejected",
        decision_note=payload.note if payload else None,
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Leave request rejected",
        "data": rejected,
    }
