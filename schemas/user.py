# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, constr, field_validator
from typing import Optional, Literal, List
import re

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
    profile_image: Optional[str] = Field(None, alias="profileImage")

    class Config:
        allow_population_by_field_name = True


class AccountSettingsUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    country: Optional[str] = None
    contact: Optional[str] = None
    profile_image: Optional[str] = Field(None, alias="profileImage")

    class Config:
        allow_population_by_field_name = True


class AccountSettingsResponse(BaseModel):
    id: int
    full_name: Optional[str] = Field(None, alias="fullName")
    email: EmailStr
    role: str
    is_superuser: bool = Field(..., alias="isSuperuser")
    profile: UserProfile

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class AccountPasswordUpdate(BaseModel):
    current_password: str = Field(..., alias="currentPassword")
    new_password: constr(min_length=8) = Field(..., alias="newPassword")
    confirm_password: constr(min_length=8) = Field(..., alias="confirmPassword")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str):
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[\d\s\W]", value):
            raise ValueError("Password must include at least one number, symbol, or whitespace")
        return value

    class Config:
        allow_population_by_field_name = True


class TwoFactorStatusResponse(BaseModel):
    enabled: bool
    method: Optional[Literal["authenticator", "sms"]] = None
    sms_phone: Optional[str] = Field(None, alias="smsPhone")
    sms_verified: bool = Field(False, alias="smsVerified")

    class Config:
        allow_population_by_field_name = True


class TwoFactorMethodRequest(BaseModel):
    method: Literal["authenticator", "sms"]


class TwoFactorTotpSetupResponse(BaseModel):
    secret: str
    otpauth_url: str = Field(..., alias="otpauthUrl")

    class Config:
        allow_population_by_field_name = True


class TwoFactorTotpVerifyRequest(BaseModel):
    code: str


class TwoFactorSmsStartRequest(BaseModel):
    phone: str


class TwoFactorSmsVerifyRequest(BaseModel):
    code: str


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
