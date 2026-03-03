# schemas/employee_registration.py
from pydantic import BaseModel, EmailStr, Field, constr, field_validator


class EmployeeRegisterRequest(BaseModel):
    company_code: str = Field(..., alias="companyCode")
    name: str
    email: EmailStr
    phone: str
    employee_id: str = Field(..., alias="employeeId")
    department: str
    password: constr(min_length=8)
    confirm_password: constr(min_length=8) = Field(..., alias="confirmPassword")

    @field_validator("confirm_password")
    @classmethod
    def validate_passwords(cls, value: str, values):
        password = values.data.get("password")
        if password and value != password:
            raise ValueError("Passwords do not match")
        return value

    class Config:
        allow_population_by_field_name = True


class EmployeeRegisterResponse(BaseModel):
    success: bool
    status_code: int
    message: str


class PendingEmployeeItem(BaseModel):
    id: int
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    phone: str | None = None
    employee_id: str | None = Field(None, alias="employeeId")
    department: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class PendingEmployeeListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[PendingEmployeeItem]


class EmployeeApprovalResponse(BaseModel):
    success: bool
    status_code: int
    message: str
