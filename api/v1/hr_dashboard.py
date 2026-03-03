# api/v1/hr_dashboard.py
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from api import deps
from models.attendance_log import AttendanceLog
from models.leave_request import LeaveRequest
from models.payslip import Payslip
from models.pay_period import PayPeriod
from models.user import User

router = APIRouter()


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


@router.get("/", status_code=status.HTTP_200_OK)
def hr_dashboard(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Employees
    total_employees = (
        db.query(User)
        .filter(User.business_id == businessId, User.role == "employee")
        .count()
    )
    active_employees = (
        db.query(User)
        .filter(
            User.business_id == businessId,
            User.role == "employee",
            User.is_active == True,  # noqa: E712
        )
        .count()
    )
    pending_employees = (
        db.query(User)
        .filter(
            User.business_id == businessId,
            User.role == "employee",
            User.is_active == False,  # noqa: E712
        )
        .count()
    )
    inactive_employees = max(total_employees - active_employees - pending_employees, 0)

    # Attendance (today)
    today = date.today()
    today_logs = (
        db.query(AttendanceLog)
        .filter(
            AttendanceLog.business_id == businessId,
            AttendanceLog.work_date == today,
        )
        .all()
    )
    today_checked_in = len(today_logs)
    today_checked_out = len([log for log in today_logs if log.check_out_at is not None])
    missing_checkout = len([log for log in today_logs if log.check_out_at is None])

    # Leave (this month)
    start_of_month = date(today.year, today.month, 1)
    pending_leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.business_id == businessId,
            LeaveRequest.status == "pending",
        )
        .count()
    )
    approved_month = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.business_id == businessId,
            LeaveRequest.status == "approved",
            LeaveRequest.start_date >= start_of_month,
        )
        .count()
    )
    rejected_month = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.business_id == businessId,
            LeaveRequest.status == "rejected",
            LeaveRequest.start_date >= start_of_month,
        )
        .count()
    )

    # Payroll summary
    last_period = (
        db.query(PayPeriod)
        .filter(PayPeriod.business_id == businessId)
        .order_by(PayPeriod.period_end.desc())
        .first()
    )
    last_period_net = 0.0
    payslips_generated = 0
    if last_period:
        payslips = (
            db.query(Payslip)
            .filter(
                Payslip.business_id == businessId,
                Payslip.pay_period_id == last_period.id,
            )
            .all()
        )
        payslips_generated = len(payslips)
        last_period_net = float(sum(p.net_pay for p in payslips))

    open_periods = (
        db.query(PayPeriod)
        .filter(PayPeriod.business_id == businessId, PayPeriod.status == "open")
        .count()
    )

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "HR dashboard summary",
        "data": {
            "employees": {
                "total": total_employees,
                "active": active_employees,
                "pending": pending_employees,
                "inactive": inactive_employees,
            },
            "attendance": {
                "todayCheckedIn": today_checked_in,
                "todayCheckedOut": today_checked_out,
                "missingCheckout": missing_checkout,
            },
            "leave": {
                "pending": pending_leaves,
                "approvedThisMonth": approved_month,
                "rejectedThisMonth": rejected_month,
            },
            "payroll": {
                "lastPeriodNetPay": last_period_net,
                "payslipsGenerated": payslips_generated,
                "openPeriods": open_periods,
            },
        },
    }
