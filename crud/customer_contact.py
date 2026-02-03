# crud/customer_contact.py
from sqlalchemy.orm import Session
from typing import Optional, List

from models.customer_contact import CustomerContact
from schemas.customer_contact import CustomerContactCreate


def list_contacts(
    db: Session,
    *,
    customer_id: int,
    business_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[CustomerContact]:
    query = db.query(CustomerContact).filter(CustomerContact.customer_id == customer_id)
    if business_id:
        query = query.filter(CustomerContact.business_id == business_id)
    return query.order_by(CustomerContact.contacted_at.desc()).offset(skip).limit(limit).all()


def create_contact(db: Session, contact_in: CustomerContactCreate) -> CustomerContact:
    db_contact = CustomerContact(**contact_in.dict(by_alias=False))
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact
