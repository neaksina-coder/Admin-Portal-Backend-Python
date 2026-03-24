# schemas/leave_policy.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeavePolicyBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    leave_type_id: int = Field(..., alias="leaveTypeId")
    annual_allowance: float = Field(default=0, alias="annualAllowance")
    accrual_method: str = Field(default="monthly", alias="accrualMethod")
    carryover_days: Optional[float] = Field(default=None, alias="carryoverDays")
    max_balance: Optional[float] = Field(default=None, alias="maxBalance")
    allow_negative: bool = Field(default=False, alias="allowNegative")
    model_config = ConfigDict(populate_by_name=True)


class LeavePolicyCreate(LeavePolicyBase):
    pass


class LeavePolicyUpdate(BaseModel):
    annual_allowance: Optional[float] = Field(default=None, alias="annualAllowance")
    accrual_method: Optional[str] = Field(default=None, alias="accrualMethod")
    carryover_days: Optional[float] = Field(default=None, alias="carryoverDays")
    max_balance: Optional[float] = Field(default=None, alias="maxBalance")
    allow_negative: Optional[bool] = Field(default=None, alias="allowNegative")
    model_config = ConfigDict(populate_by_name=True)


class LeavePolicy(LeavePolicyBase):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LeavePolicyResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: LeavePolicy


class LeavePolicyListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[LeavePolicy]
