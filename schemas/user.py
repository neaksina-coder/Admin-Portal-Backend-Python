# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional, Literal, List

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    privacy_policy_accepted: bool = False

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    privacy_policy_accepted: bool
    role: str = 'user'

    class Config:
        from_attributes = True

class Token(BaseModel):
    token: str
    user: User

class TokenData(BaseModel):
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class EmailSchema(BaseModel):
    email: EmailStr


class OtpVerifySchema(BaseModel):
    email: EmailStr
    otp: str


class PasswordResetSchema(BaseModel):
    new_password: constr(min_length=8)
    confirm_password: constr(min_length=8)

class UserCreateResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    user: User


class TokenResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    token: str
    user: User


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin", "superuser"]


class OtpVerifyResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    reset_token: str


class UserProfile(BaseModel):
    company: Optional[str] = None
    country: Optional[str] = None
    contact: Optional[str] = None


class UserManagementCreate(BaseModel):
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    password: str
    role: Literal["user", "admin", "superuser"]
    plan: str
    billing: str
    status: str

    class Config:
        allow_population_by_field_name = True


class UserManagementUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    role: Optional[Literal["user", "admin", "superuser"]] = None
    plan: Optional[str] = None
    billing: Optional[str] = None
    status: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    contact: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class UserListItem(BaseModel):
    id: int
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    role: str
    plan: Optional[str] = None
    billing: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class UserDetail(UserListItem):
    profile: Optional[UserProfile] = None


class UserListResponse(BaseModel):
    users: List[UserListItem]
    totalUsers: int
    page: int


class UserDeleteResponse(BaseModel):
    success: bool
