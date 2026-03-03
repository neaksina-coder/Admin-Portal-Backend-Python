# api/v1/contact_inquiries_api.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from core.config import settings
from crud import contact_inquiry as crud_inquiry
from models.business import Business
from schemas.contact_inquiry import (
    ContactInquiryListResponse,
    ContactInquiryReplyRequest,
    ContactInquiryResponse,
    ContactInquiryUpdate,
)
from utils.email import send_email
from utils.email_templates import render_contact_reply_email


router = APIRouter()


@router.get("/", response_model=ContactInquiryListResponse)
def list_inquiries(
    businessId: int = Query(...),
    status: str | None = Query(None),
    q: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    inquiries = crud_inquiry.list_inquiries(
        db,
        business_id=businessId,
        status=status,
        q=q,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Contact inquiries retrieved successfully",
        "total": len(inquiries),
        "data": inquiries,
    }


@router.get("/{inquiry_id}", response_model=ContactInquiryResponse)
def get_inquiry(
    inquiry_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    inquiry = crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Inquiry retrieved successfully",
        "data": inquiry,
    }


@router.put("/{inquiry_id}", response_model=ContactInquiryResponse)
def update_inquiry(
    inquiry_id: int,
    updates: ContactInquiryUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    inquiry = crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    inquiry = crud_inquiry.update_inquiry(db, inquiry, updates)
    return {
        "success": True,
        "status_code": 200,
        "message": "Inquiry updated successfully",
        "data": inquiry,
    }


@router.post("/{inquiry_id}/reply", response_model=ContactInquiryResponse)
def reply_to_inquiry(
    inquiry_id: int,
    payload: ContactInquiryReplyRequest,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    inquiry = crud_inquiry.get_inquiry(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    if not (settings.EMAIL_FROM and settings.SMTP_USER and settings.SMTP_PASSWORD):
        raise HTTPException(status_code=500, detail="SMTP is not configured")

    business_name = settings.PROJECT_NAME
    if inquiry.business_id:
        business = db.query(Business).filter(Business.id == inquiry.business_id).first()
        if business and business.name:
            business_name = business.name

    subject = payload.subject or (
        f"Re: {inquiry.subject}" if inquiry.subject else "Re: Your inquiry"
    )

    plain_text = (
        f"Hi {inquiry.name},\n\n"
        f"{payload.body}\n\n"
        f"Thanks,\n{business_name} Team"
    )

    html = render_contact_reply_email(
        subject=subject,
        reply_body=payload.body,
        customer_name=inquiry.name,
        customer_email=inquiry.email,
        original_subject=inquiry.subject,
        original_message=inquiry.message,
        business_name=business_name,
        support_email=settings.EMAIL_FROM or None,
    )

    send_email(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
        smtp_use_tls=settings.SMTP_USE_TLS,
        from_email=settings.EMAIL_FROM,
        to_email=inquiry.email,
        subject=subject,
        content=plain_text,
        html_content=html,
    )

    inquiry = crud_inquiry.mark_replied(db, inquiry)
    return {
        "success": True,
        "status_code": 200,
        "message": "Reply sent successfully",
        "data": inquiry,
    }
