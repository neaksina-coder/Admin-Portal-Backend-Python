# api/v1/customers.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api import deps
from crud import customer as crud_customer
from crud import customer_contact as crud_contact
from schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
)
from schemas.customer_contact import (
    CustomerContactCreate,
    CustomerContactResponse,
    CustomerContactListResponse,
)

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    customer = crud_customer.create_customer(db, customer_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "Customer created successfully",
        "data": customer,
    }


@router.get("/", response_model=CustomerListResponse)
def list_customers(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    q: str | None = Query(None),
    segment: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    customers = crud_customer.list_customers(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
        q=q,
        segment=segment,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Customers retrieved successfully",
        "total": len(customers),
        "data": customers,
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    customer = crud_customer.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Customer retrieved successfully",
        "data": customer,
    }


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    customer = crud_customer.update_customer(db, customer_id, customer_in)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Customer updated successfully",
        "data": customer,
    }


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    customer = crud_customer.delete_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"success": True, "message": "Customer deleted successfully"}


@router.post("/{customer_id}/contacts", response_model=CustomerContactResponse, status_code=201)
def create_contact(
    customer_id: int,
    contact_in: CustomerContactCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    if contact_in.customer_id != customer_id:
        raise HTTPException(status_code=400, detail="Customer ID mismatch")
    contact = crud_contact.create_contact(db, contact_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "Contact history created successfully",
        "data": contact,
    }


@router.get("/{customer_id}/contacts", response_model=CustomerContactListResponse)
def list_contacts(
    customer_id: int,
    businessId: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    contacts = crud_contact.list_contacts(
        db,
        customer_id=customer_id,
        business_id=businessId,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Contact history retrieved successfully",
        "total": len(contacts),
        "data": contacts,
    }
