# api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import EmailStr
import os
import shutil
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import pyotp

from api import deps
from crud import user as crud_user
from utils.security import verify_password, get_password_hash
from models.user_lookups import UserRole, UserPlan, UserStatus
from core.config import settings
from schemas.user import (
    User,
    UserRoleUpdate,
    UserManagementCreate,
    UserManagementUpdate,
    UserListResponse,
    UserDetail,
    UserDeleteResponse,
    AccountSettingsResponse,
    AccountPasswordUpdate,
    TwoFactorStatusResponse,
    TwoFactorMethodRequest,
    TwoFactorTotpSetupResponse,
    TwoFactorTotpVerifyRequest,
    TwoFactorSmsStartRequest,
    TwoFactorSmsVerifyRequest,
)

router = APIRouter()

USER_FILTERS_RESPONSE = {
    "roles": [
        {"label": "User", "value": "user"},
        {"label": "Admin", "value": "admin"},
        {"label": "Superuser", "value": "superuser"},
    ],
    "plans": [
        {"label": "Basic", "value": "basic"},
        {"label": "Company", "value": "company"},
        {"label": "Enterprise", "value": "enterprise"},
        {"label": "Team", "value": "team"},
    ],
    "statuses": [
        {"label": "Active", "value": "active"},
        {"label": "Inactive", "value": "inactive"},
        {"label": "Pending", "value": "pending"},
    ],
}


def _serialize_user_list_item(user):
    return {
        "id": user.id,
        "fullName": user.full_name or user.username,
        "email": user.email,
        "role": user.role,
        "plan": user.plan,
        "billing": user.billing,
        "status": user.status,
    }


def _serialize_user_detail(user, base_url: Optional[str] = None):
    profile_image = user.profile_image
    if base_url and profile_image and profile_image.startswith("/uploads/"):
        profile_image = f"{base_url.rstrip('/')}{profile_image}"
    data = _serialize_user_list_item(user)
    data["profile"] = {
        "company": user.company,
        "country": user.country,
        "contact": user.contact,
        "profileImage": profile_image,
    }
    return data


def _serialize_account_settings(user, base_url: Optional[str] = None):
    profile_image = user.profile_image
    if base_url and profile_image and profile_image.startswith("/uploads/"):
        profile_image = f"{base_url.rstrip('/')}{profile_image}"
    return {
        "id": user.id,
        "fullName": user.full_name or user.username,
        "email": user.email,
        "role": "superuser" if user.is_superuser else user.role,
        "isSuperuser": user.is_superuser,
        "profile": {
            "company": user.company,
            "country": user.country,
            "contact": user.contact,
            "profileImage": profile_image,
        },
    }


def _save_profile_image(upload: UploadFile) -> str:
    upload_dir = os.path.join("uploads", "profile_images")
    os.makedirs(upload_dir, exist_ok=True)
    _, ext = os.path.splitext(upload.filename or "")
    filename = f"{uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return f"/uploads/profile_images/{filename}"


@router.get("/", response_model=UserListResponse)
def list_users(
    q: Optional[str] = None,
    role: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    itemsPerPage: int = 10,
    sortBy: Optional[str] = None,
    orderBy: str = "asc",
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if page < 1 or itemsPerPage < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination values")
    if orderBy.lower() not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid orderBy value")
    if role and role not in {"user", "admin", "superuser"}:
        raise HTTPException(status_code=400, detail="Invalid role filter")
    if not current_user.is_superuser and role and role != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        users, total = crud_user.get_users_filtered(
            db,
            q=q,
            role=role,
            plan=plan,
            status=status,
            page=page,
            items_per_page=itemsPerPage,
            sort_by=sortBy,
            order_by=orderBy,
            current_user=current_user,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sortBy value")

    return {
        "users": [_serialize_user_list_item(user) for user in users],
        "totalUsers": total,
        "page": page,
    }


@router.get("/filters")
def get_user_filters(
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_roles(["admin"])),
):
    roles = (
        db.query(UserRole)
        .order_by(UserRole.sort_order.asc(), UserRole.label.asc())
        .all()
    )
    plans = (
        db.query(UserPlan)
        .order_by(UserPlan.sort_order.asc(), UserPlan.label.asc())
        .all()
    )
    statuses = (
        db.query(UserStatus)
        .order_by(UserStatus.sort_order.asc(), UserStatus.label.asc())
        .all()
    )

    return {
        "roles": [
            {"label": role.label, "value": role.value} for role in roles
        ]
        if roles
        else USER_FILTERS_RESPONSE["roles"],
        "plans": [
            {"label": plan.label, "value": plan.value} for plan in plans
        ]
        if plans
        else USER_FILTERS_RESPONSE["plans"],
        "statuses": [
            {"label": status.label, "value": status.value} for status in statuses
        ]
        if statuses
        else USER_FILTERS_RESPONSE["statuses"],
    }


@router.get("/me", response_model=AccountSettingsResponse)
def get_account_settings(
    request: Request,
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    return _serialize_account_settings(current_user, base_url=str(request.base_url))


@router.put("/me", response_model=AccountSettingsResponse)
def update_account_settings(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
    fullName: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    company: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    contact: Optional[str] = Form(None),
    profileImage: Optional[UploadFile] = File(None),
):
    updates = {}
    if fullName is not None:
        updates["full_name"] = fullName
    if email is not None:
        if email != current_user.email:
            existing = crud_user.get_user_by_email(db, email=email)
            if existing and existing.id != current_user.id:
                raise HTTPException(status_code=409, detail="Email already exists")
        updates["email"] = email
    if company is not None:
        updates["company"] = company
    if country is not None:
        updates["country"] = country
    if contact is not None:
        updates["contact"] = contact
    if profileImage is not None:
        updates["profile_image"] = _save_profile_image(profileImage)

    updated = crud_user.update_user_details(db, user_id=current_user.id, updates=updates)
    return _serialize_account_settings(updated, base_url=str(request.base_url))


@router.put("/me/password")
def update_account_password(
    password_in: AccountPasswordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if password_in.new_password != password_in.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"success": True, "message": "Password updated successfully"}


@router.get("/me/2fa", response_model=TwoFactorStatusResponse)
def get_two_factor_status(
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    return {
        "enabled": current_user.two_factor_enabled,
        "method": current_user.two_factor_method,
        "smsPhone": current_user.sms_phone,
        "smsVerified": current_user.sms_verified,
    }


@router.post("/me/2fa/method", response_model=TwoFactorStatusResponse)
def select_two_factor_method(
    method_in: TwoFactorMethodRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    current_user.two_factor_method = method_in.method
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "enabled": current_user.two_factor_enabled,
        "method": current_user.two_factor_method,
        "smsPhone": current_user.sms_phone,
        "smsVerified": current_user.sms_verified,
    }


@router.post("/me/2fa/authenticator/setup", response_model=TwoFactorTotpSetupResponse)
def setup_totp(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    current_user.two_factor_method = "authenticator"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    issuer = "Sina Neak"
    otpauth_url = pyotp.TOTP(secret).provisioning_uri(
        name=current_user.email, issuer_name=issuer
    )
    return {"secret": secret, "otpauthUrl": otpauth_url}


@router.post("/me/2fa/authenticator/verify", response_model=TwoFactorStatusResponse)
def verify_totp(
    verify_in: TwoFactorTotpVerifyRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="Authenticator not set up")
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(verify_in.code):
        raise HTTPException(status_code=400, detail="Invalid authentication code")
    current_user.two_factor_enabled = True
    current_user.two_factor_method = "authenticator"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "enabled": current_user.two_factor_enabled,
        "method": current_user.two_factor_method,
        "smsPhone": current_user.sms_phone,
        "smsVerified": current_user.sms_verified,
    }


@router.post("/me/2fa/sms/start", response_model=TwoFactorStatusResponse)
def start_sms_2fa(
    sms_in: TwoFactorSmsStartRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    code = f"{secrets.randbelow(1_000_000):06d}"
    otp_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.SMS_OTP_EXPIRE_MINUTES
    )
    current_user.sms_phone = sms_in.phone
    current_user.sms_verified = False
    current_user.sms_otp_hash = otp_hash
    current_user.sms_otp_expires = expires_at
    current_user.sms_otp_attempts = 0
    current_user.two_factor_method = "sms"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # TODO: integrate real SMS provider; for now we only store the code hash.
    return {
        "enabled": current_user.two_factor_enabled,
        "method": current_user.two_factor_method,
        "smsPhone": current_user.sms_phone,
        "smsVerified": current_user.sms_verified,
    }


@router.post("/me/2fa/sms/verify", response_model=TwoFactorStatusResponse)
def verify_sms_2fa(
    sms_in: TwoFactorSmsVerifyRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if not current_user.sms_otp_hash or not current_user.sms_otp_expires:
        raise HTTPException(status_code=400, detail="SMS verification not started")
    now = datetime.now(timezone.utc)
    expires_at = current_user.sms_otp_expires
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now or current_user.sms_otp_attempts >= settings.SMS_OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    otp_hash = hashlib.sha256(sms_in.code.encode("utf-8")).hexdigest()
    if otp_hash != current_user.sms_otp_hash:
        current_user.sms_otp_attempts += 1
        db.add(current_user)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    current_user.sms_verified = True
    current_user.two_factor_enabled = True
    current_user.two_factor_method = "sms"
    current_user.sms_otp_hash = None
    current_user.sms_otp_expires = None
    current_user.sms_otp_attempts = 0
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "enabled": current_user.two_factor_enabled,
        "method": current_user.two_factor_method,
        "smsPhone": current_user.sms_phone,
        "smsVerified": current_user.sms_verified,
    }


@router.get("/{user_id}", response_model=UserDetail)
def get_user_detail(
    user_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if user.is_superuser or user.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")
    return _serialize_user_detail(user, base_url=str(request.base_url))


@router.post("/", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserManagementCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    if not current_user.is_superuser and user_in.role != "user":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    is_superuser = user_in.role == "superuser"
    user = crud_user.create_user_with_details(
        db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=user_in.role,
        is_superuser=is_superuser,
        plan=user_in.plan,
        billing=user_in.billing,
        status=user_in.status,
        company=None,
        country=None,
        contact=None,
    )
    return _serialize_user_detail(user, base_url=str(request.base_url))


@router.put("/{user_id}", response_model=UserDetail)
def update_user(
    user_id: int,
    user_in: UserManagementUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if user.is_superuser or user.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        if user_in.role and user_in.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")

    updates = user_in.dict(exclude_unset=True, by_alias=False)
    if "role" in updates and updates["role"] is not None:
        updates["is_superuser"] = updates["role"] == "superuser"
    updated = crud_user.update_user_details(db, user_id=user_id, updates=updates)
    return _serialize_user_detail(updated, base_url=str(request.base_url))


@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(["admin"])),
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        if user.is_superuser or user.role != "user":
            raise HTTPException(status_code=403, detail="Not enough permissions")
    crud_user.delete_user(db, user_id=user_id)
    return {"success": True}


@router.post("/admins", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_admin(
    user_in: UserManagementCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    if user_in.role != "admin":
        raise HTTPException(status_code=400, detail="Role must be admin")
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = crud_user.create_user_with_details(
        db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role="admin",
        is_superuser=False,
        plan=user_in.plan,
        billing=user_in.billing,
        status=user_in.status,
        company=None,
        country=None,
        contact=None,
    )
    return _serialize_user_detail(user, base_url=str(request.base_url))


@router.put("/{user_id}/role", response_model=UserDetail)
def update_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    if role_in.role == "superuser":
        role = "superuser"
        is_superuser = True
    elif role_in.role == "admin":
        role = "admin"
        is_superuser = False
    else:
        role = "user"
        is_superuser = False
    user = crud_user.update_user_role(
        db, user_id=user_id, role=role, is_superuser=is_superuser
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user_detail(user, base_url=str(request.base_url))


@router.post("/superusers", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_superuser(
    user_in: UserManagementCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    if user_in.role != "superuser":
        raise HTTPException(status_code=400, detail="Role must be superuser")
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = crud_user.create_user_with_details(
        db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role="superuser",
        is_superuser=True,
        plan=user_in.plan,
        billing=user_in.billing,
        status=user_in.status,
        company=None,
        country=None,
        contact=None,
    )
    return _serialize_user_detail(user, base_url=str(request.base_url))
