# api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api import deps
from crud import user as crud_user
from schemas.user import User, UserCreate, UserRoleUpdate

router = APIRouter()


@router.get("/", response_model=List[User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_roles(["admin"])),
):
    return crud_user.get_users(db, skip=skip, limit=limit)


@router.post("/admins", response_model=User, status_code=status.HTTP_201_CREATED)
def create_admin(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_superuser),
):
    existing = crud_user.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    existing = crud_user.get_user_by_username(db, username=user_in.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    return crud_user.create_user(db, user=user_in, role="admin", is_superuser=False)


@router.put("/{user_id}/role", response_model=User)
def update_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
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
    return user
