# schemas/leave_balance.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeaveBalance(BaseModel):
    id: int
    business_id: int = Field(..., alias="businessId")
    user_id: int = Field(..., alias="userId")
    leave_type_id: int = Field(..., alias="leaveTypeId")
    balance: float
    used: float
    pending: float
    last_accrual_at: Optional[datetime] = Field(None, alias="lastAccrualAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LeaveBalanceListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[LeaveBalance]


class LeaveBalanceResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: LeaveBalance


class LeaveBalanceAdjustRequest(BaseModel):
    change: float
    reason: Optional[str] = None
