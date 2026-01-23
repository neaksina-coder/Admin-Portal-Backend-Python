# crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from models.user import User
from schemas.user import UserCreate
from typing import Optional, Tuple, List
from utils.security import get_password_hash
from datetime import datetime
import re

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_users_filtered(
    db: Session,
    *,
    q: Optional[str] = None,
    role: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    items_per_page: int = 10,
    sort_by: Optional[str] = None,
    order_by: str = "asc",
    current_user: Optional[User] = None,
) -> Tuple[List[User], int]:
    query = db.query(User)

    if current_user and not current_user.is_superuser:
        query = query.filter(User.role == "user", User.is_superuser == False)

    if role:
        if role == "superuser":
            query = query.filter(User.is_superuser == True)
        else:
            query = query.filter(User.role == role, User.is_superuser == False)
    if plan:
        query = query.filter(User.plan == plan)
    if status:
        query = query.filter(User.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                User.full_name.ilike(like),
                User.email.ilike(like),
                User.username.ilike(like),
            )
        )

    sort_map = {
        "user": User.full_name,
        "email": User.email,
        "role": User.role,
        "plan": User.plan,
        "status": User.status,
        "billing": User.billing,
    }
    if sort_by:
        sort_column = sort_map.get(sort_by)
        if sort_column is None:
            raise ValueError("Invalid sortBy value")
        if order_by.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    total = query.count()
    offset = (page - 1) * items_per_page
    users = query.offset(offset).limit(items_per_page).all()
    return users, total

def create_user(
    db: Session,
    user: UserCreate,
    role: Optional[str] = None,
    is_superuser: Optional[bool] = None,
):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        full_name=user.username,
        email=user.email,
        hashed_password=hashed_password,
        privacy_policy_accepted=user.privacy_policy_accepted,
        role=role if role is not None else "user",
        is_superuser=is_superuser if is_superuser is not None else False,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A user with this email or username already exists.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    return db_user


def update_user_reset_token(db: Session, user_id: int, reset_token: str, reset_token_expires: datetime):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db_user.reset_token = reset_token
    db_user.reset_token_expires = reset_token_expires
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_reset_token(db: Session, reset_token: str):
    return db.query(User).filter(User.reset_token == reset_token).first()


def update_user_password(db: Session, user_id: int, new_password: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db_user.hashed_password = get_password_hash(new_password)
    db_user.reset_token = None
    db_user.reset_token_expires = None
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def _normalize_username(base: str) -> str:
    base = (base or "user").lower()
    base = re.sub(r"[^a-z0-9._-]+", "", base)
    return base or "user"


def _generate_unique_username(db: Session, email: str) -> str:
    base = _normalize_username(email.split("@")[0] if email else "user")
    candidate = base
    suffix = 1
    while get_user_by_username(db, candidate):
        candidate = f"{base}{suffix}"
        suffix += 1
    return candidate


def create_user_with_details(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
    is_superuser: bool = False,
    plan: Optional[str] = None,
    billing: Optional[str] = None,
    status: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    contact: Optional[str] = None,
) -> User:
    hashed_password = get_password_hash(password)
    username = _generate_unique_username(db, email)
    db_user = User(
        username=username,
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
        role=role,
        is_superuser=is_superuser,
        privacy_policy_accepted=False,
        plan=plan,
        billing=billing,
        status=status or "active",
        company=company,
        country=country,
        contact=contact,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A user with this email or username already exists.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    return db_user


def update_user_role(db: Session, user_id: int, role: str, is_superuser: bool):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db_user.role = role
    db_user.is_superuser = is_superuser
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_details(db: Session, user_id: int, updates: dict) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    for key, value in updates.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
