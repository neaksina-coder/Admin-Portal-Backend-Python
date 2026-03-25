# api/v1/public.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from api import deps
from core.config import settings
from crud import business as crud_business
from crud import plan as crud_plan
from crud import subscription as crud_subscription
from crud import user as crud_user
from crud import contact_inquiry as crud_inquiry
from models.business import Business
from models.invoice import Invoice
from models.subscription import Subscription
from schemas.contact_inquiry import ContactInquiryPublicCreate, ContactInquiryResponse
from schemas.business import BusinessCreate
from schemas.subscription import SubscriptionCreate
from schemas.employee_registration import (
    EmployeeRegisterRequest,
    EmployeeRegisterResponse,
)
from schemas.payment import (
    PayPalOrderCreate,
    PayPalOrderResponse,
    PayPalCaptureRequest,
    PayPalCaptureResponse,
)
from utils.email import send_email
from utils.paypal import create_order, capture_order


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


@router.get("/paypal/config")
def paypal_config():
    if not settings.PAYPAL_CLIENT_ID:
        raise HTTPException(status_code=500, detail="PayPal is not configured")
    return {
        "clientId": settings.PAYPAL_CLIENT_ID,
        "env": settings.PAYPAL_ENV,
        "currency": settings.PAYPAL_CURRENCY,
    }


@router.get("/plans")
def list_public_plans(
    db: Session = Depends(deps.get_db),
):
    plans = crud_plan.list_plans(db, skip=0, limit=100)
    allowed = ["basic", "pro", "enterprise"]
    filtered = [plan for plan in plans if (plan.plan_name or "").lower() in allowed]
    order_map = {name: idx for idx, name in enumerate(allowed)}
    filtered.sort(key=lambda p: order_map.get((p.plan_name or "").lower(), 99))
    return {
        "success": True,
        "data": [
            {
                "id": plan.id,
                "name": plan.plan_name,
                "price": float(plan.price or 0),
                "features": plan.features,
            }
            for plan in filtered
        ],
    }


@router.post("/paypal/orders", response_model=PayPalOrderResponse)
def create_paypal_order(
    payload: PayPalOrderCreate,
    db: Session = Depends(deps.get_db),
):
    plan = crud_plan.get_plan_by_name(db, payload.plan_name)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    price = float(plan.price or 0)
    if payload.billing_cycle == "yearly":
        price = price * 12

    # Create business + owner before payment (pending subscription)
    business = crud_business.create_business(
        db,
        BusinessCreate(name=payload.business_name, plan_id=plan.id, status="active"),
    )

    owner = crud_user.create_user_with_details(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.business_name,
        role="customer_owner",
        is_superuser=False,
        is_active=True,
        status="active",
        business_id=business.id,
    )

    start_date = date.today()
    end_date = start_date + timedelta(days=365 if payload.billing_cycle == "yearly" else 30)

    sub = crud_subscription.create_subscription(
        db,
        SubscriptionCreate(
            businessId=business.id,
            planId=plan.id,
            startDate=start_date,
            endDate=end_date,
            status="pending",
            billingHistory={
                "source": "paypal",
                "planName": plan.plan_name,
                "billingCycle": payload.billing_cycle,
                "ownerUserId": owner.id,
            },
        ),
    )

    order = create_order(
        amount=price,
        currency=settings.PAYPAL_CURRENCY,
        description=f"{plan.plan_name} ({payload.billing_cycle})",
        custom_id=str(sub.id),
    )

    return {"orderId": order["id"]}


@router.post("/paypal/capture", response_model=PayPalCaptureResponse)
def capture_paypal_order(
    payload: PayPalCaptureRequest,
    db: Session = Depends(deps.get_db),
):
    result = capture_order(payload.order_id)
    status_value = (result.get("status") or "").upper()
    if status_value != "COMPLETED":
        raise HTTPException(status_code=400, detail="Payment not completed")

    purchase_units = result.get("purchase_units", [])
    custom_id = None
    if purchase_units:
        custom_id = purchase_units[0].get("custom_id")

    if not custom_id:
        raise HTTPException(status_code=400, detail="Missing subscription reference")

    sub = db.query(Subscription).filter(Subscription.id == int(custom_id)).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub.status = "active"
    if isinstance(sub.billing_history, dict):
        sub.billing_history["paypalOrderId"] = payload.order_id

    invoice = (
        db.query(Invoice)
        .filter(Invoice.subscription_id == sub.id)
        .order_by(Invoice.created_at.desc())
        .first()
    )
    if invoice:
        invoice.payment_status = "paid"
        if isinstance(invoice.metadata_json, dict):
            invoice.metadata_json["paypalOrderId"] = payload.order_id

    db.add(sub)
    if invoice:
        db.add(invoice)
    db.commit()

    return {
        "success": True,
        "message": "Payment captured",
        "businessId": sub.business_id,
        "subscriptionId": sub.id,
    }
