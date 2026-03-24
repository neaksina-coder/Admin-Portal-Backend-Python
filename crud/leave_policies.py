# crud/leave_policies.py
from typing import List, Optional

from sqlalchemy.orm import Session

from models.leave_policy import LeavePolicy
from schemas.leave_policy import LeavePolicyCreate, LeavePolicyUpdate


def get_leave_policy(db: Session, policy_id: int) -> Optional[LeavePolicy]:
    return db.query(LeavePolicy).filter(LeavePolicy.id == policy_id).first()


def get_policy_by_type(db: Session, business_id: int, leave_type_id: int) -> Optional[LeavePolicy]:
    return (
        db.query(LeavePolicy)
        .filter(
            LeavePolicy.business_id == business_id,
            LeavePolicy.leave_type_id == leave_type_id,
        )
        .first()
    )


def list_policies(db: Session, business_id: int) -> List[LeavePolicy]:
    return (
        db.query(LeavePolicy)
        .filter(LeavePolicy.business_id == business_id)
        .order_by(LeavePolicy.id.desc())
        .all()
    )


def create_policy(db: Session, payload: LeavePolicyCreate) -> LeavePolicy:
    policy = LeavePolicy(
        business_id=payload.business_id,
        leave_type_id=payload.leave_type_id,
        annual_allowance=payload.annual_allowance,
        accrual_method=payload.accrual_method,
        carryover_days=payload.carryover_days,
        max_balance=payload.max_balance,
        allow_negative=payload.allow_negative,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def update_policy(db: Session, policy: LeavePolicy, updates: LeavePolicyUpdate) -> LeavePolicy:
    data = updates.dict(exclude_unset=True, by_alias=False)
    for key, value in data.items():
        setattr(policy, key, value)
    db.commit()
    db.refresh(policy)
    return policy
