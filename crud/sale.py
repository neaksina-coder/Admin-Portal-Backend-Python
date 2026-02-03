# crud/sale.py
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from models.sale import Sale
from crud import promo_code as crud_promo
from schemas.sale import SaleCreate


def get_sale(db: Session, sale_id: int) -> Optional[Sale]:
    return db.query(Sale).filter(Sale.id == sale_id).first()


def list_sales(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Sale]:
    query = db.query(Sale).filter(Sale.business_id == business_id)
    if start_date:
        query = query.filter(Sale.transaction_date >= start_date)
    if end_date:
        query = query.filter(Sale.transaction_date <= end_date)
    return query.order_by(Sale.transaction_date.desc()).offset(skip).limit(limit).all()


def create_sale(db: Session, sale_in: SaleCreate) -> Sale:
    payload = sale_in.dict(by_alias=False)
    if not payload.get("invoice_number"):
        payload["invoice_number"] = f"INV-{int(datetime.utcnow().timestamp())}"
    promo_code_id = payload.get("promo_code_id")
    if promo_code_id:
        promo = crud_promo.get_promo(db, promo_code_id)
        if promo:
            promo.used_count += 1
    db_sale = Sale(**payload)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale
