# schemas/leave_request.py
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class LeaveRequestBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    user_id: int = Field(..., alias="userId")
    leave_type: str = Field(..., alias="leaveType")
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    reason: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class LeaveRequestCreate(BaseModel):
    business_id: Optional[int] = Field(None, alias="businessId")
    user_id: Optional[int] = Field(None, alias="userId")
    leave_type: str = Field(..., alias="leaveType")
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    reason: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class LeaveRequestUpdate(BaseModel):
    leave_type: Optional[str] = Field(None, alias="leaveType")
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    reason: Optional[str] = None
    status: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class LeaveRequest(LeaveRequestBase):
    id: int
    status: str
    decision_note: Optional[str] = Field(None, alias="decisionNote")
    approved_by_user_id: Optional[int] = Field(None, alias="approvedByUserId")
    approved_at: Optional[datetime] = Field(None, alias="approvedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LeaveRequestResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: LeaveRequest


class LeaveRequestListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[LeaveRequest]


class LeaveDecisionRequest(BaseModel):
    note: Optional[str] = None
