# api/v1/hr_payroll.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api import deps
from crud import payroll as crud_payroll
from models.employee_pay_setting import EmployeePaySetting
from models.user import User
from schemas.payroll import (
    EmployeePaySettingCreate,
    EmployeePaySettingResponse,
    PayPeriodCreate,
    PayPeriodListResponse,
    PayPeriodResponse,
    PayslipListResponse,
    PayrollRunRequest,
)

router = APIRouter()


def _require_hr_admin(current_user: User = Depends(deps.require_roles(["customer_owner", "hr_admin"]))):
    return current_user


@router.post("/periods", response_model=PayPeriodResponse, status_code=status.HTTP_201_CREATED)
def create_pay_period(
    payload: PayPeriodCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    period = crud_payroll.create_pay_period(
        db,
        business_id=payload.business_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
    )
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Pay period created successfully",
        "data": period,
    }


@router.get("/periods", response_model=PayPeriodListResponse)
def list_pay_periods(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != businessId:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    periods = crud_payroll.list_pay_periods(db, business_id=businessId)
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Pay periods retrieved successfully",
        "total": len(periods),
        "data": periods,
    }


@router.post("/settings", response_model=EmployeePaySettingResponse, status_code=status.HTTP_201_CREATED)
def upsert_pay_setting(
    payload: EmployeePaySettingCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    setting = crud_payroll.upsert_employee_pay_setting(
        db,
        business_id=payload.business_id,
        user_id=payload.user_id,
        pay_type=payload.pay_type,
        monthly_salary=payload.monthly_salary,
        hourly_rate=payload.hourly_rate,
        overtime_rate=payload.overtime_rate,
    )
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Employee pay setting saved",
        "data": setting,
    }


@router.post("/run", response_model=PayslipListResponse)
def run_payroll(
    payload: PayrollRunRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(_require_hr_admin),
):
    if not current_user.is_superuser and current_user.business_id != payload.business_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    period = crud_payroll.get_pay_period(db, payload.pay_period_id)
    if not period or period.business_id != payload.business_id:
        raise HTTPException(status_code=404, detail="Pay period not found")

    # MVP: create payslips for employees with pay settings
    employee_settings = (
        db.query(EmployeePaySetting)
        .filter(EmployeePaySetting.business_id == payload.business_id)
        .all()
    )
    slips = []
    for setting in employee_settings:
        gross = setting.monthly_salary or 0
        overtime = 0
        deductions = 0
        net = gross + overtime - deductions
        slip = crud_payroll.create_payslip(
            db,
            business_id=payload.business_id,
            user_id=setting.user_id,
            pay_period_id=payload.pay_period_id,
            gross_pay=gross,
            overtime_pay=overtime,
            deductions=deductions,
            net_pay=net,
        )
        slips.append(slip)

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Payroll run completed",
        "total": len(slips),
        "data": slips,
    }


@router.get("/payslips", response_model=PayslipListResponse)
def list_payslips(
    businessId: int = Query(...),
    userId: int | None = Query(None),
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

    slips = crud_payroll.list_payslips(
        db,
        business_id=business_id,
        user_id=target_user_id,
    )
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Payslips retrieved successfully",
        "total": len(slips),
        "data": slips,
    }
