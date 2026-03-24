# crud/leave_balances.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models.employee_leave_balance import EmployeeLeaveBalance
from models.leave_policy import LeavePolicy
from models.leave_transaction import LeaveTransaction


def get_balance(db: Session, user_id: int, leave_type_id: int) -> Optional[EmployeeLeaveBalance]:
    return (
        db.query(EmployeeLeaveBalance)
        .filter(
            EmployeeLeaveBalance.user_id == user_id,
            EmployeeLeaveBalance.leave_type_id == leave_type_id,
        )
        .first()
    )


def list_balances(db: Session, business_id: int, user_id: Optional[int] = None) -> List[EmployeeLeaveBalance]:
    query = db.query(EmployeeLeaveBalance).filter(EmployeeLeaveBalance.business_id == business_id)
    if user_id:
        query = query.filter(EmployeeLeaveBalance.user_id == user_id)
    return query.order_by(EmployeeLeaveBalance.user_id.asc()).all()


def _apply_monthly_accrual(balance: EmployeeLeaveBalance, policy: LeavePolicy) -> None:
    if policy.annual_allowance <= 0:
        return
    if not balance.last_accrual_at:
        return
    now = datetime.utcnow()
    months = (now.year - balance.last_accrual_at.year) * 12 + (now.month - balance.last_accrual_at.month)
    if months <= 0:
        return
    increment = (policy.annual_allowance / 12.0) * months
    balance.balance += increment
    if policy.max_balance is not None:
        balance.balance = min(balance.balance, policy.max_balance)
    balance.last_accrual_at = now


def ensure_balance(
    db: Session,
    *,
    business_id: int,
    user_id: int,
    leave_type_id: int,
    policy: Optional[LeavePolicy],
) -> EmployeeLeaveBalance:
    existing = get_balance(db, user_id=user_id, leave_type_id=leave_type_id)
    if existing:
        if policy and policy.accrual_method == "monthly":
            _apply_monthly_accrual(existing, policy)
            db.commit()
            db.refresh(existing)
        return existing

    base_balance = 0.0
    now = datetime.utcnow()
    if policy:
        if policy.accrual_method == "yearly":
            base_balance = policy.annual_allowance or 0
        elif policy.accrual_method == "monthly":
            base_balance = (policy.annual_allowance or 0) / 12.0

    if policy and policy.max_balance is not None:
        base_balance = min(base_balance, policy.max_balance)

    balance = EmployeeLeaveBalance(
        business_id=business_id,
        user_id=user_id,
        leave_type_id=leave_type_id,
        balance=base_balance,
        used=0,
        pending=0,
        last_accrual_at=now if policy else None,
    )
    db.add(balance)
    db.commit()
    db.refresh(balance)
    return balance


def add_transaction(
    db: Session,
    *,
    business_id: int,
    user_id: int,
    leave_type_id: int,
    change: float,
    reason: str,
    ref_id: Optional[int] = None,
) -> LeaveTransaction:
    tx = LeaveTransaction(
        business_id=business_id,
        user_id=user_id,
        leave_type_id=leave_type_id,
        change=change,
        reason=reason,
        ref_id=ref_id,
    )
    db.add(tx)
    return tx


def adjust_balance(
    db: Session,
    balance: EmployeeLeaveBalance,
    *,
    change: float,
    reason: str,
    ref_id: Optional[int] = None,
) -> EmployeeLeaveBalance:
    balance.balance += change
    add_transaction(
        db,
        business_id=balance.business_id,
        user_id=balance.user_id,
        leave_type_id=balance.leave_type_id,
        change=change,
        reason=reason,
        ref_id=ref_id,
    )
    db.commit()
    db.refresh(balance)
    return balance


def add_pending(balance: EmployeeLeaveBalance, days: float) -> None:
    balance.pending += days


def remove_pending(balance: EmployeeLeaveBalance, days: float) -> None:
    balance.pending = max(balance.pending - days, 0)


def apply_approval(
    balance: EmployeeLeaveBalance,
    *,
    days: float,
) -> None:
    balance.pending = max(balance.pending - days, 0)
    balance.used += days
    balance.balance -= days
