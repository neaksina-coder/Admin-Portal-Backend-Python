# api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api import deps
from crud import user as crud_user
from schemas.user import Token, UserLogin, EmailSchema, PasswordResetSchema, User, UserCreate, UserCreateResponse
from utils.security import create_access_token, verify_password, generate_password_reset_token, get_password_hash # Added get_password_hash

router = APIRouter()

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
    return {"message": "User created successfully", "user": user}

@router.post("/login", response_model=Token)
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
    access_token = create_access_token(data={"sub": user.email})
    if user.is_superuser:
        user.role = "admin"
    return {"token": access_token, "user": user}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    *,
    db: Session = Depends(deps.get_db),
    email_in: EmailSchema,
):
    user = crud_user.get_user_by_email(db, email=email_in.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No user with the given email address was found.",
        )

    reset_token = generate_password_reset_token()
    reset_token_expires = datetime.utcnow() + timedelta(hours=1) # Token valid for 1 hour

    crud_user.update_user_reset_token(db, user.id, reset_token, reset_token_expires)

    # In a real application, you would send an email here
    print(f"DEBUG: Password reset link for {user.email}: /reset-password?token={reset_token}")

    return {"message": "Password reset link sent successfully."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    *,
    db: Session = Depends(deps.get_db),
    password_reset_in: PasswordResetSchema,
):
    user = crud_user.get_user_by_reset_token(db, password_reset_in.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    crud_user.update_user_password(db, user.id, password_reset_in.new_password)
    
    # Invalidate the token after use
    crud_user.update_user_reset_token(db, user.id, None, None)

    return {"message": "Password has been reset successfully."}
