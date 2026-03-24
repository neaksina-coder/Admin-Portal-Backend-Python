# crud/leave_types.py
from typing import List, Optional

from sqlalchemy.orm import Session

from models.leave_type import LeaveType
from schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate


def get_leave_type(db: Session, leave_type_id: int) -> Optional[LeaveType]:
    return db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()


def get_leave_type_by_name(db: Session, business_id: int, name: str) -> Optional[LeaveType]:
    return (
        db.query(LeaveType)
        .filter(LeaveType.business_id == business_id, LeaveType.name == name)
        .first()
    )


def list_leave_types(db: Session, business_id: int) -> List[LeaveType]:
    return (
        db.query(LeaveType)
        .filter(LeaveType.business_id == business_id)
        .order_by(LeaveType.name.asc())
        .all()
    )


def create_leave_type(db: Session, payload: LeaveTypeCreate) -> LeaveType:
    item = LeaveType(
        business_id=payload.business_id,
        name=payload.name.strip(),
        is_paid=payload.is_paid,
        is_active=payload.is_active,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_leave_type(db: Session, leave_type: LeaveType, updates: LeaveTypeUpdate) -> LeaveType:
    data = updates.dict(exclude_unset=True, by_alias=False)
    for key, value in data.items():
        setattr(leave_type, key, value)
    db.commit()
    db.refresh(leave_type)
    return leave_type
