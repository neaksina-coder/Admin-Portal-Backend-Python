# schemas/user.py
from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Literal

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
