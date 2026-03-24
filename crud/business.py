# crud/business.py
from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.business import Business
from schemas.business import BusinessCreate, BusinessAccountUpdate


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


def suspend_business(db: Session, business_id: int, reason: Optional[str] = None) -> Optional[Business]:
    business = get_business(db, business_id)
    if not business:
        return None
    business.status = "suspended"
    business.suspended_at = datetime.utcnow()
    business.suspended_reason = reason
    db.commit()
    db.refresh(business)
    return business


def unsuspend_business(db: Session, business_id: int) -> Optional[Business]:
    business = get_business(db, business_id)
    if not business:
        return None
    business.status = "active"
    business.suspended_at = None
    business.suspended_reason = None
    db.commit()
    db.refresh(business)
    return business


def update_business_account(
    db: Session, business: Business, payload: BusinessAccountUpdate
) -> Business:
    updates = payload.dict(exclude_unset=True, by_alias=False)

    if "tenant_id" in updates:
        tenant_id = (updates["tenant_id"] or "").strip()
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID is required")
        existing = get_business_by_tenant_id(db, tenant_id)
        if existing and existing.id != business.id:
            raise HTTPException(status_code=400, detail="Tenant ID already exists")
        business.tenant_id = tenant_id

    if "name" in updates:
        name = (updates["name"] or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="Business name is required")
        business.name = name

    db.commit()
    db.refresh(business)
    return business
