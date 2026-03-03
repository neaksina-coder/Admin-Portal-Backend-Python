# api/v1/hr_attendance.py
from datetime import datetime, date
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import attendance_log as crud_attendance
from models.user import User
from schemas.attendance import (
    AttendanceCheckInRequest,
    AttendanceCheckOutRequest,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceUpdateRequest,
)

router = APIRouter()
LOCAL_TZ = ZoneInfo("Asia/Phnom_Penh")


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


@router.post("/check-in", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def check_in(
    payload: AttendanceCheckInRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "employee" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only employees can check in")

    business_id = current_user.business_id
    if not business_id:
        raise HTTPException(status_code=400, detail="Business not assigned")

    now_local = datetime.now(LOCAL_TZ)
    today = now_local.date()
    existing = crud_attendance.get_open_log_for_day(
        db,
        business_id=business_id,
        user_id=current_user.id,
        work_date=today,
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already checked in")

    log = crud_attendance.create_check_in(
        db,
        business_id=business_id,
        user_id=current_user.id,
        work_date=today,
        check_in_at=now_local.replace(tzinfo=None),
        note=payload.note,
    )
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Checked in successfully",
        "data": log,
    }


@router.post("/check-out", response_model=AttendanceResponse)
def check_out(
    payload: AttendanceCheckOutRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "employee" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only employees can check out")

    business_id = current_user.business_id
    if not business_id:
        raise HTTPException(status_code=400, detail="Business not assigned")

    now_local = datetime.now(LOCAL_TZ)
    today = now_local.date()
    log = crud_attendance.get_open_log_for_day(
        db,
        business_id=business_id,
        user_id=current_user.id,
        work_date=today,
    )
    if not log:
        raise HTTPException(status_code=404, detail="No open check-in found")

    updated = crud_attendance.check_out(
        db,
        log,
        check_out_at=now_local.replace(tzinfo=None),
        note=payload.note,
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Checked out successfully",
        "data": updated,
    }


@router.get("/", response_model=AttendanceListResponse)
def list_attendance(
    businessId: int = Query(...),
    userId: int | None = Query(None),
    startDate: date | None = Query(None),
    endDate: date | None = Query(None),
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

    logs = crud_attendance.list_attendance_logs(
        db,
        business_id=business_id,
        user_id=target_user_id,
        start_date=startDate,
        end_date=endDate,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Attendance logs retrieved successfully",
        "total": len(logs),
        "data": logs,
    }


@router.get("/{log_id}", response_model=AttendanceResponse)
def get_attendance_log(
    log_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    log = crud_attendance.get_attendance_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Attendance log not found")

    if current_user.is_superuser:
        pass
    elif current_user.role in {"customer_owner", "hr_admin"}:
        if current_user.business_id != log.business_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "employee":
        if log.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Attendance log retrieved successfully",
        "data": log,
    }


@router.put("/{log_id}", response_model=AttendanceResponse)
def update_attendance_log(
    log_id: int,
    payload: AttendanceUpdateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    log = crud_attendance.get_attendance_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Attendance log not found")

    if not current_user.is_superuser and current_user.business_id != log.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updates = payload.dict(exclude_unset=True, by_alias=False)
    updated = crud_attendance.update_attendance(db, log, updates)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Attendance log updated successfully",
        "data": updated,
    }
