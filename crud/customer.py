# crud/customer.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List

from models.customer import Customer
from models.business import Business
from models.plan import Plan
from schemas.customer import CustomerCreate, CustomerUpdate


def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def list_customers(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    segment: Optional[str] = None,
) -> List[Customer]:
    query = db.query(Customer).filter(Customer.business_id == business_id)
    if segment:
        query = query.filter(Customer.segment == segment)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Customer.name.ilike(like),
                Customer.email.ilike(like),
                Customer.phone.ilike(like),
            )
        )
    return query.offset(skip).limit(limit).all()


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    business = db.query(Business).filter(Business.id == customer_in.business_id).first()
    if business and business.plan_id:
        plan = db.query(Plan).filter(Plan.id == business.plan_id).first()
        if plan and isinstance(plan.features, dict):
            max_customers = plan.features.get("maxCustomers")
            if isinstance(max_customers, int):
                current_count = (
                    db.query(Customer)
                    .filter(Customer.business_id == customer_in.business_id)
                    .count()
                )
                if current_count >= max_customers:
                    raise ValueError("Customer limit reached for current plan")

    db_customer = Customer(**customer_in.dict(by_alias=False))
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer_in: CustomerUpdate) -> Optional[Customer]:
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        return None
    update_data = customer_in.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> Optional[Customer]:
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        return None
    db.delete(db_customer)
    db.commit()
    return db_customer
