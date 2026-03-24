# crud/leave_request.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models.leave_request import LeaveRequest
from crud import leave_balances as crud_leave_balances
from crud import leave_policies as crud_leave_policies
from crud import leave_types as crud_leave_types
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
    leave_type = None
    if payload.leave_type_id:
        leave_type = crud_leave_types.get_leave_type(db, payload.leave_type_id)
        if leave_type and leave_type.business_id != business_id:
            leave_type = None
        if not leave_type:
            raise ValueError("Invalid leave type")
    elif payload.leave_type:
        leave_type = crud_leave_types.get_leave_type_by_name(db, business_id, payload.leave_type)

    leave_type_id = leave_type.id if leave_type else None
    leave_type_name = leave_type.name if leave_type else (payload.leave_type or "Unspecified")

    days_requested = (payload.end_date - payload.start_date).days + 1
    if days_requested <= 0:
        raise ValueError("End date must be on or after start date")

    policy = None
    if leave_type_id:
        policy = crud_leave_policies.get_policy_by_type(db, business_id, leave_type_id)

    if policy and leave_type and leave_type.is_paid:
        balance = crud_leave_balances.ensure_balance(
            db,
            business_id=business_id,
            user_id=user_id,
            leave_type_id=leave_type_id,
            policy=policy,
        )
        available = balance.balance - balance.pending
        if not policy.allow_negative and available < days_requested:
            raise ValueError("Insufficient leave balance")
        crud_leave_balances.add_pending(balance, days_requested)
        crud_leave_balances.add_transaction(
            db,
            business_id=balance.business_id,
            user_id=balance.user_id,
            leave_type_id=balance.leave_type_id,
            change=0,
            reason="pending",
            ref_id=None,
        )
        db.commit()

    db_request = LeaveRequest(
        business_id=business_id,
        user_id=user_id,
        leave_type_id=leave_type_id,
        leave_type=leave_type_name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days_requested=days_requested,
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

    if leave_request.leave_type_id and leave_request.days_requested:
        policy = crud_leave_policies.get_policy_by_type(
            db,
            leave_request.business_id,
            leave_request.leave_type_id,
        )
        if policy:
            balance = crud_leave_balances.ensure_balance(
                db,
                business_id=leave_request.business_id,
                user_id=leave_request.user_id,
                leave_type_id=leave_request.leave_type_id,
                policy=policy,
            )
            if status == "approved":
                crud_leave_balances.apply_approval(balance, days=leave_request.days_requested)
                crud_leave_balances.add_transaction(
                    db,
                    business_id=balance.business_id,
                    user_id=balance.user_id,
                    leave_type_id=balance.leave_type_id,
                    change=-float(leave_request.days_requested),
                    reason="approval",
                    ref_id=leave_request.id,
                )
            else:
                crud_leave_balances.remove_pending(balance, leave_request.days_requested)
            db.commit()

    db.commit()
    db.refresh(leave_request)
    return leave_request
