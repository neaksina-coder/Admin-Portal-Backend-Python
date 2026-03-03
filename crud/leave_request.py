# crud/leave_request.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models.leave_request import LeaveRequest
from schemas.leave_request import LeaveRequestCreate, LeaveRequestUpdate


def get_leave_request(db: Session, request_id: int) -> Optional[LeaveRequest]:
    return db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()


def list_leave_requests(
    db: Session,
    *,
    business_id: int,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[LeaveRequest]:
    query = db.query(LeaveRequest).filter(LeaveRequest.business_id == business_id)
    if user_id:
        query = query.filter(LeaveRequest.user_id == user_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    return (
        query.order_by(LeaveRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_leave_request(
    db: Session,
    payload: LeaveRequestCreate,
    *,
    business_id: int,
    user_id: int,
) -> LeaveRequest:
    db_request = LeaveRequest(
        business_id=business_id,
        user_id=user_id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status="pending",
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_leave_request(
    db: Session,
    leave_request: LeaveRequest,
    updates: LeaveRequestUpdate,
) -> LeaveRequest:
    data = updates.dict(exclude_unset=True, by_alias=False)
    for key, value in data.items():
        setattr(leave_request, key, value)
    db.commit()
    db.refresh(leave_request)
    return leave_request


def approve_leave_request(
    db: Session,
    leave_request: LeaveRequest,
    *,
    approved_by_user_id: int,
    status: str = "approved",
    decision_note: Optional[str] = None,
) -> LeaveRequest:
    leave_request.status = status
    leave_request.approved_by_user_id = approved_by_user_id
    leave_request.approved_at = datetime.utcnow()
    leave_request.decision_note = decision_note
    db.commit()
    db.refresh(leave_request)
    return leave_request
