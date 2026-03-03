# schemas/payroll.py
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PayPeriodCreate(BaseModel):
    business_id: int = Field(..., alias="businessId")
    period_start: date = Field(..., alias="periodStart")
    period_end: date = Field(..., alias="periodEnd")

    model_config = ConfigDict(populate_by_name=True)


class PayPeriod(BaseModel):
    id: int
    business_id: int = Field(..., alias="businessId")
    period_start: date = Field(..., alias="periodStart")
    period_end: date = Field(..., alias="periodEnd")
    status: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PayPeriodResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: PayPeriod


class PayPeriodListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[PayPeriod]


class EmployeePaySettingCreate(BaseModel):
    business_id: int = Field(..., alias="businessId")
    user_id: int = Field(..., alias="userId")
    pay_type: str = Field(..., alias="payType")
    monthly_salary: Optional[float] = Field(None, alias="monthlySalary")
    hourly_rate: Optional[float] = Field(None, alias="hourlyRate")
    overtime_rate: Optional[float] = Field(None, alias="overtimeRate")

    model_config = ConfigDict(populate_by_name=True)


class EmployeePaySettingUpdate(BaseModel):
    pay_type: Optional[str] = Field(None, alias="payType")
    monthly_salary: Optional[float] = Field(None, alias="monthlySalary")
    hourly_rate: Optional[float] = Field(None, alias="hourlyRate")
    overtime_rate: Optional[float] = Field(None, alias="overtimeRate")

    model_config = ConfigDict(populate_by_name=True)


class EmployeePaySetting(BaseModel):
    id: int
    business_id: int = Field(..., alias="businessId")
    user_id: int = Field(..., alias="userId")
    pay_type: str = Field(..., alias="payType")
    monthly_salary: Optional[float] = Field(None, alias="monthlySalary")
    hourly_rate: Optional[float] = Field(None, alias="hourlyRate")
    overtime_rate: Optional[float] = Field(None, alias="overtimeRate")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EmployeePaySettingResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: EmployeePaySetting


class Payslip(BaseModel):
    id: int
    business_id: int = Field(..., alias="businessId")
    user_id: int = Field(..., alias="userId")
    pay_period_id: int = Field(..., alias="payPeriodId")
    gross_pay: float = Field(..., alias="grossPay")
    overtime_pay: float = Field(..., alias="overtimePay")
    deductions: float
    net_pay: float = Field(..., alias="netPay")
    status: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PayslipResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Payslip


class PayslipListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Payslip]


class PayrollRunRequest(BaseModel):
    business_id: int = Field(..., alias="businessId")
    pay_period_id: int = Field(..., alias="payPeriodId")

    model_config = ConfigDict(populate_by_name=True)
