# crud/business.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List
import uuid

from models.business import Business
from schemas.business import BusinessCreate


def get_business(db: Session, business_id: int) -> Optional[Business]:
    return db.query(Business).filter(Business.id == business_id).first()


def get_business_by_tenant_id(db: Session, tenant_id: str) -> Optional[Business]:
    return db.query(Business).filter(Business.tenant_id == tenant_id).first()


def list_businesses(db: Session, skip: int = 0, limit: int = 100) -> List[Business]:
    return db.query(Business).offset(skip).limit(limit).all()


def _generate_tenant_id() -> str:
    return uuid.uuid4().hex


def create_business(db: Session, business_in: BusinessCreate) -> Business:
    tenant_id = business_in.tenant_id or _generate_tenant_id()
    if get_business_by_tenant_id(db, tenant_id):
        raise HTTPException(status_code=400, detail="Tenant ID already exists")

    db_business = Business(
        name=business_in.name,
        tenant_id=tenant_id,
        plan_id=business_in.plan_id,
        status=business_in.status,
    )
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business
