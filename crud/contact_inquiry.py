# crud/contact_inquiry.py
from datetime import datetime
from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.contact_inquiry import ContactInquiry
from schemas.contact_inquiry import ContactInquiryPublicCreate, ContactInquiryUpdate


def get_inquiry(db: Session, inquiry_id: int) -> Optional[ContactInquiry]:
    return db.query(ContactInquiry).filter(ContactInquiry.id == inquiry_id).first()


def list_inquiries(
    db: Session,
    *,
    business_id: int,
    status: Optional[str] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ContactInquiry]:
    query = db.query(ContactInquiry).filter(ContactInquiry.business_id == business_id)
    if status:
        query = query.filter(ContactInquiry.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                ContactInquiry.name.ilike(like),
                ContactInquiry.email.ilike(like),
                ContactInquiry.subject.ilike(like),
                ContactInquiry.message.ilike(like),
                ContactInquiry.company.ilike(like),
            )
        )
    return (
        query.order_by(ContactInquiry.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_inquiry(
    db: Session, inquiry_in: ContactInquiryPublicCreate
) -> ContactInquiry:
    db_inquiry = ContactInquiry(**inquiry_in.dict(by_alias=False))
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry


def update_inquiry(
    db: Session, inquiry: ContactInquiry, updates: ContactInquiryUpdate
) -> ContactInquiry:
    update_data = updates.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(inquiry, key, value)
    db.commit()
    db.refresh(inquiry)
    return inquiry


def mark_replied(
    db: Session, inquiry: ContactInquiry, *, status: str = "replied"
) -> ContactInquiry:
    inquiry.status = status
    inquiry.replied_at = datetime.utcnow()
    db.commit()
    db.refresh(inquiry)
    return inquiry
