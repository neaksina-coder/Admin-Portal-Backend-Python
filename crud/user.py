# crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from models.user import User
from schemas.user import UserCreate
from utils.security import get_password_hash
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        privacy_policy_accepted=user.privacy_policy_accepted,
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
