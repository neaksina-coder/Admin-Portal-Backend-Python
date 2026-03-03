# schemas/attendance.py
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AttendanceCheckInRequest(BaseModel):
    note: Optional[str] = None


class AttendanceCheckOutRequest(BaseModel):
    note: Optional[str] = None


class AttendanceUpdateRequest(BaseModel):
    check_in_at: Optional[datetime] = Field(None, alias="checkInAt")
    check_out_at: Optional[datetime] = Field(None, alias="checkOutAt")
    status: Optional[str] = None
    note: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class AttendanceLog(BaseModel):
    id: int
    business_id: int = Field(..., alias="businessId")
    user_id: int = Field(..., alias="userId")
    work_date: date = Field(..., alias="workDate")
    check_in_at: datetime = Field(..., alias="checkInAt")
    check_out_at: Optional[datetime] = Field(None, alias="checkOutAt")
    status: str
    note: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AttendanceResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: AttendanceLog


class AttendanceListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[AttendanceLog]
