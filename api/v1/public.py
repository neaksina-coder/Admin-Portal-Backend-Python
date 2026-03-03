# api/v1/public.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from api import deps
from core.config import settings
from crud import user as crud_user
from crud import contact_inquiry as crud_inquiry
from models.business import Business
from schemas.contact_inquiry import ContactInquiryPublicCreate, ContactInquiryResponse
from schemas.employee_registration import (
    EmployeeRegisterRequest,
    EmployeeRegisterResponse,
)
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


@router.post("/hr/register", response_model=EmployeeRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_hr_employee(
    payload: EmployeeRegisterRequest,
    db: Session = Depends(deps.get_db),
):
    company_code = payload.company_code.strip()
    if not company_code:
        raise HTTPException(status_code=400, detail="Company code is required")

    business = (
        db.query(Business)
        .filter(func.lower(Business.tenant_id) == company_code.lower())
        .first()
    )
    if not business:
        raise HTTPException(status_code=404, detail="Invalid company code")

    existing = crud_user.get_user_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system.",
        )

    crud_user.create_user_with_details(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.name,
        role="employee",
        is_superuser=False,
        is_active=False,
        status="pending",
        contact=payload.phone,
        employee_id=payload.employee_id,
        department=payload.department,
        business_id=business.id,
    )

    return {
        "success": True,
        "status_code": status.HTTP_201_CREATED,
        "message": "Registration submitted. Awaiting HR admin approval.",
    }
