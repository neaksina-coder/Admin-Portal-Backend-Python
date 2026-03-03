# crud/payroll.py
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from models.pay_period import PayPeriod
from models.employee_pay_setting import EmployeePaySetting
from models.payslip import Payslip


def create_pay_period(
    db: Session, *, business_id: int, period_start: date, period_end: date
) -> PayPeriod:
    period = PayPeriod(
        business_id=business_id,
        period_start=period_start,
        period_end=period_end,
        status="open",
    )
    db.add(period)
    db.commit()
    db.refresh(period)
    return period


def list_pay_periods(db: Session, *, business_id: int) -> List[PayPeriod]:
    return (
        db.query(PayPeriod)
        .filter(PayPeriod.business_id == business_id)
        .order_by(PayPeriod.period_start.desc())
        .all()
    )


def get_pay_period(db: Session, period_id: int) -> Optional[PayPeriod]:
    return db.query(PayPeriod).filter(PayPeriod.id == period_id).first()


def get_employee_pay_setting(
    db: Session, *, business_id: int, user_id: int
) -> Optional[EmployeePaySetting]:
    return (
        db.query(EmployeePaySetting)
        .filter(
            EmployeePaySetting.business_id == business_id,
            EmployeePaySetting.user_id == user_id,
        )
        .first()
    )


def upsert_employee_pay_setting(
    db: Session,
    *,
    business_id: int,
    user_id: int,
    pay_type: str,
    monthly_salary: Optional[float],
    hourly_rate: Optional[float],
    overtime_rate: Optional[float],
) -> EmployeePaySetting:
    existing = get_employee_pay_setting(db, business_id=business_id, user_id=user_id)
    if existing:
        existing.pay_type = pay_type
        existing.monthly_salary = monthly_salary
        existing.hourly_rate = hourly_rate
        existing.overtime_rate = overtime_rate
        db.commit()
        db.refresh(existing)
        return existing
    setting = EmployeePaySetting(
        business_id=business_id,
        user_id=user_id,
        pay_type=pay_type,
        monthly_salary=monthly_salary,
        hourly_rate=hourly_rate,
        overtime_rate=overtime_rate,
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def list_payslips(
    db: Session, *, business_id: int, user_id: Optional[int] = None
) -> List[Payslip]:
    query = db.query(Payslip).filter(Payslip.business_id == business_id)
    if user_id:
        query = query.filter(Payslip.user_id == user_id)
    return query.order_by(Payslip.created_at.desc()).all()


def create_payslip(
    db: Session,
    *,
    business_id: int,
    user_id: int,
    pay_period_id: int,
    gross_pay: float,
    overtime_pay: float,
    deductions: float,
    net_pay: float,
) -> Payslip:
    slip = Payslip(
        business_id=business_id,
        user_id=user_id,
        pay_period_id=pay_period_id,
        gross_pay=gross_pay,
        overtime_pay=overtime_pay,
        deductions=deductions,
        net_pay=net_pay,
        status="generated",
    )
    db.add(slip)
    db.commit()
    db.refresh(slip)
    return slip
