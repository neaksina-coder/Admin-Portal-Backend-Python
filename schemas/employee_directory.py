# schemas/employee_directory.py
from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional


class EmployeeCreateRequest(BaseModel):
    business_id: int = Field(..., alias="businessId")
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    phone: Optional[str] = None
    employee_id: Optional[str] = Field(None, alias="employeeId")
    department: Optional[str] = None
    password: constr(min_length=8)

    class Config:
        allow_population_by_field_name = True


class EmployeeUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = Field(None, alias="employeeId")
    department: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="isActive")

    class Config:
        allow_population_by_field_name = True


class EmployeeListItem(BaseModel):
    id: int
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    phone: Optional[str] = None
    employee_id: Optional[str] = Field(None, alias="employeeId")
    department: Optional[str] = None
    status: Optional[str] = None
    is_active: bool = Field(..., alias="isActive")

    class Config:
        allow_population_by_field_name = True


class EmployeeListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[EmployeeListItem]


class EmployeeDetailItem(EmployeeListItem):
    business_id: Optional[int] = Field(None, alias="businessId")

    class Config:
        allow_population_by_field_name = True


class EmployeeDetailResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: EmployeeDetailItem
