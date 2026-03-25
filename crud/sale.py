# crud/sale.py
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from models.sale import Sale
from models.sale_item import SaleItem
from models.product import Product
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
    items = payload.pop("items", None) or []

    if not payload.get("invoice_number"):
        payload["invoice_number"] = f"INV-{int(datetime.utcnow().timestamp())}"

    # Calculate totals from items if provided
    resolved_items = []
    if items:
        subtotal = 0.0
        for item in items:
            product = db.query(Product).filter(Product.id == item["product_id"]).first()
            if not product:
                raise ValueError("Product not found")
            if product.business_id != payload.get("business_id"):
                raise ValueError("Product does not belong to business")
            unit_price = float(item.get("unit_price", product.price))
            quantity = int(item.get("quantity", 1))
            line_total = unit_price * quantity
            subtotal += line_total
            resolved_items.append(
                {
                    "product_id": product.id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": line_total,
                }
            )

        payload["original_amount"] = subtotal
        discount = float(payload.get("discount_amount") or 0)
        payload["total_price"] = max(subtotal - discount, 0)

    promo_code_id = payload.get("promo_code_id")
    if promo_code_id:
        promo = crud_promo.get_promo(db, promo_code_id)
        if promo:
            promo.used_count += 1

    db_sale = Sale(**payload)
    db.add(db_sale)
    db.flush()

    for item in resolved_items:
        db.add(
            SaleItem(
                sale_id=db_sale.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
            )
        )

    db.commit()
    db.refresh(db_sale)
    return db_sale
