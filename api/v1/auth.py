# api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets
import logging

from api import deps
from crud import user as crud_user
from crud import otp_code as crud_otp
from schemas.user import (
    TokenResponse,
    UserLogin,
    EmailSchema,
    OtpVerifySchema,
    OtpVerifyResponse,
    PasswordResetSchema,
    User,
    UserCreate,
    UserCreateResponse,
)
from utils.security import create_access_token, verify_password, get_password_hash
import hashlib
from utils.email import send_email
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.create_user(db, user=user_in)
    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "User created successfully",
        "user": user,
    }

@router.post("/login", response_model=TokenResponse)
def login(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserLogin,
):
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )
    effective_role = "superuser" if user.is_superuser else user.role
    access_token = create_access_token(data={"sub": user.email, "role": effective_role})
    user.role = effective_role
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Login successful",
        "token": access_token,
        "user": user,
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    *,
    db: Session = Depends(deps.get_db),
    email_in: EmailSchema,
):
    user = crud_user.get_user_by_email(db, email=email_in.email)
    if user:
        otp = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        otp_hash = hashlib.sha256(otp.encode("utf-8")).hexdigest()

        crud_otp.invalidate_active_otps(db, user.id, used_at=datetime.now(timezone.utc))
        crud_otp.create_otp_code(db, user.id, otp_hash, expires_at)

        if (
            settings.EMAIL_FROM
            and settings.SMTP_USER
            and settings.SMTP_PASSWORD
        ):
            subject = "Your password reset OTP"
            content = f"Your OTP code is: {otp}. It expires in {settings.OTP_EXPIRE_MINUTES} minutes."
            try:
                send_email(
                    smtp_host=settings.SMTP_HOST,
                    smtp_port=settings.SMTP_PORT,
                    smtp_user=settings.SMTP_USER,
                    smtp_password=settings.SMTP_PASSWORD,
                    smtp_use_tls=settings.SMTP_USE_TLS,
                    from_email=settings.EMAIL_FROM,
                    to_email=user.email,
                    subject=subject,
                    content=content,
                )
                logger.info("OTP email sent to %s", user.email)
            except Exception as exc:
                logger.exception("Failed to send OTP email to %s: %s", user.email, exc)
        else:
            logger.warning("SMTP not configured; OTP email not sent.")

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "If the email exists, an OTP has been sent.",
    }


@router.post("/otp/verify", response_model=OtpVerifyResponse, status_code=status.HTTP_200_OK)
def verify_otp(
    *,
    db: Session = Depends(deps.get_db),
    otp_in: OtpVerifySchema,
):
    user = crud_user.get_user_by_email(db, email=otp_in.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    otp_record = crud_otp.get_latest_active_otp(db, user.id)
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    now = datetime.now(timezone.utc)
    expires_at = otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now or otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
        crud_otp.mark_used(db, otp_record.id, used_at=now)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    otp_hash = hashlib.sha256(otp_in.otp.encode("utf-8")).hexdigest()
    if otp_hash != otp_record.otp_hash:
        crud_otp.increment_attempts(db, otp_record.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    reset_token = secrets.token_urlsafe(32)
    reset_token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
    reset_token_expires = now + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    crud_user.update_user_reset_token(db, user.id, reset_token_hash, reset_token_expires)
    crud_otp.mark_used(db, otp_record.id, used_at=now)

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "OTP verified successfully.",
        "reset_token": reset_token,
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    *,
    db: Session = Depends(deps.get_db),
    password_reset_in: PasswordResetSchema,
    reset_token: str = Header(..., alias="X-Reset-Token"),
):
    if password_reset_in.new_password != password_reset_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )
    now = datetime.now(timezone.utc)
    reset_token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
    user = crud_user.get_user_by_reset_token(db, reset_token_hash)
    if not user or not user.reset_token_expires:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    expires_at = user.reset_token_expires
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        crud_user.update_user_reset_token(db, user.id, None, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    crud_user.update_user_password(db, user.id, password_reset_in.new_password)

    # Invalidate the token after use
    crud_user.update_user_reset_token(db, user.id, None, None)

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Password has been reset successfully.",
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(_: User = Depends(deps.get_current_user)):
    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Logged out successfully.",
    }
