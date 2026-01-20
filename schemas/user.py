# schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

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
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class EmailSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    token: str
    new_password: str

class UserCreateResponse(BaseModel):
    message: str
    user: User
