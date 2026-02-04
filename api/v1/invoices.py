# api/v1/invoices.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import audit_log as crud_audit_log
from crud import invoice as crud_invoice
from schemas.invoice import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceStatusUpdate,
)
from utils.alert_templates import build_alert
from utils.telegram import send_telegram_alert

router = APIRouter()


def _serialize_invoice(invoice):
    return {
        "id": invoice.id,
        "businessId": invoice.business_id,
        "subscriptionId": invoice.subscription_id,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "paymentStatus": invoice.payment_status,
        "paymentMethod": invoice.payment_method,
        "dueDate": invoice.due_date,
        "paymentDate": invoice.payment_date,
        "metadata": invoice.metadata_json,
        "created_at": invoice.created_at,
    }


@router.post("/", response_model=InvoiceResponse, status_code=201)
def create_invoice(
    invoice_in: InvoiceCreate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    invoice = crud_invoice.create_invoice(db, invoice_in)
    crud_audit_log.create_audit_log(
        db,
        action="invoice_created",
        actor_user_id=current_user.id,
        business_id=invoice.business_id,
        target_type="invoice",
        target_id=invoice.id,
        metadata_json={"amount": invoice.amount, "status": invoice.payment_status},
    )
    db.commit()

    send_telegram_alert(
        build_alert(
            title="Invoice Created",
            level="info",
            fields=[
                ("Invoice ID", invoice.id),
                ("Business ID", invoice.business_id),
                ("Status", invoice.payment_status),
                ("Amount", f"{invoice.amount} {invoice.currency}"),
                ("By User ID", current_user.id),
            ],
        ),
        level="info",
    )

    return {
        "success": True,
        "status_code": 201,
        "message": "Invoice created successfully",
        "data": _serialize_invoice(invoice),
    }


@router.get("/", response_model=InvoiceListResponse)
def list_invoices(
    businessId: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    invoices = crud_invoice.list_invoices(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Invoices retrieved successfully",
        "total": len(invoices),
        "data": [_serialize_invoice(invoice) for invoice in invoices],
    }


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    invoice = crud_invoice.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Invoice retrieved successfully",
        "data": _serialize_invoice(invoice),
    }


@router.put("/{invoice_id}/status", response_model=InvoiceResponse)
def update_invoice_status(
    invoice_id: int,
    payload: InvoiceStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    previous = crud_invoice.get_invoice(db, invoice_id)
    if not previous:
        raise HTTPException(status_code=404, detail="Invoice not found")
    previous_status = previous.payment_status

    invoice = crud_invoice.update_invoice_status(db, invoice_id, payload)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    crud_audit_log.create_audit_log(
        db,
        action="invoice_status_updated",
        actor_user_id=current_user.id,
        business_id=invoice.business_id,
        target_type="invoice",
        target_id=invoice.id,
        metadata_json={
            "previousStatus": previous_status,
            "newStatus": invoice.payment_status,
            "paymentMethod": invoice.payment_method,
        },
    )
    db.commit()

    level = "success" if (invoice.payment_status or "").lower() == "paid" else "warning"
    send_telegram_alert(
        build_alert(
            title="Invoice Status Updated",
            level=level,
            fields=[
                ("Invoice ID", invoice.id),
                ("Business ID", invoice.business_id),
                ("From", previous_status),
                ("To", invoice.payment_status),
                ("By User ID", current_user.id),
            ],
        ),
        level=level,
    )

    return {
        "success": True,
        "status_code": 200,
        "message": "Invoice status updated successfully",
        "data": _serialize_invoice(invoice),
    }
