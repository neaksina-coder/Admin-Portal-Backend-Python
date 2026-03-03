# api/v1/public.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import deps
from core.config import settings
from crud import contact_inquiry as crud_inquiry
from models.business import Business
from schemas.contact_inquiry import ContactInquiryPublicCreate, ContactInquiryResponse
from utils.email import send_email


router = APIRouter()


def _admin_inbox_emails() -> list[str]:
    return [
        email.strip()
        for email in (settings.ADMIN_INBOX_EMAILS or "").split(",")
        if email.strip()
    ]


@router.post("/contact-inquiries", response_model=ContactInquiryResponse, status_code=201)
def submit_contact_inquiry(
    payload: ContactInquiryPublicCreate,
    db: Session = Depends(deps.get_db),
):
    business = db.query(Business).filter(Business.id == payload.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    inquiry = crud_inquiry.create_inquiry(db, payload)

    admin_emails = _admin_inbox_emails()
    if admin_emails and settings.EMAIL_FROM and settings.SMTP_USER and settings.SMTP_PASSWORD:
        subject = payload.subject or f"New website inquiry from {payload.name}"
        content = (
            "A new contact inquiry was received from the public website.\n\n"
            f"Name: {payload.name}\n"
            f"Email: {payload.email}\n"
            f"Phone: {payload.phone or '-'}\n"
            f"Company: {payload.company or '-'}\n"
            f"Service Interest: {payload.service_interest or '-'}\n"
            f"Message:\n{payload.message}\n"
        )
        for email in admin_emails:
            try:
                send_email(
                    smtp_host=settings.SMTP_HOST,
                    smtp_port=settings.SMTP_PORT,
                    smtp_user=settings.SMTP_USER,
                    smtp_password=settings.SMTP_PASSWORD,
                    smtp_use_tls=settings.SMTP_USE_TLS,
                    from_email=settings.EMAIL_FROM,
                    to_email=email,
                    subject=subject,
                    content=content,
                )
            except Exception:
                # Do not block the public request if internal alert fails.
                pass

    return {
        "success": True,
        "status_code": 201,
        "message": "Contact inquiry submitted successfully",
        "data": inquiry,
    }
