# api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import deps
from crud import user as crud_user
from schemas.user import User
from models.user import User as UserModel
router = APIRouter()
