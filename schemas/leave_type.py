# schemas/leave_type.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeaveTypeBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    is_paid: bool = Field(default=True, alias="isPaid")
    is_active: bool = Field(default=True, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)


class LeaveTypeCreate(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    is_paid: bool = Field(default=True, alias="isPaid")
    is_active: bool = Field(default=True, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)


class LeaveTypeUpdate(BaseModel):
    name: Optional[str] = None
    is_paid: Optional[bool] = Field(default=None, alias="isPaid")
    is_active: Optional[bool] = Field(default=None, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)


class LeaveType(LeaveTypeBase):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LeaveTypeResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: LeaveType


class LeaveTypeListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[LeaveType]
