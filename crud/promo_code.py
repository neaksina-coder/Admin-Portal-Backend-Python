# crud/promo_code.py
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from models.promo_code import PromoCode
from schemas.promo_code import PromoCodeCreate, PromoCodeUpdate


def get_promo(db: Session, promo_id: int) -> Optional[PromoCode]:
    return db.query(PromoCode).filter(PromoCode.id == promo_id).first()


def get_promo_by_code(db: Session, business_id: int, code: str) -> Optional[PromoCode]:
    return (
        db.query(PromoCode)
        .filter(PromoCode.business_id == business_id, PromoCode.code == code)
        .first()
    )


def list_promos(db: Session, business_id: int, skip: int = 0, limit: int = 100) -> List[PromoCode]:
    return (
        db.query(PromoCode)
        .filter(PromoCode.business_id == business_id)
        .order_by(PromoCode.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_promo(db: Session, promo_in: PromoCodeCreate) -> PromoCode:
    db_promo = PromoCode(**promo_in.dict(by_alias=False))
    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)
    return db_promo


def update_promo(db: Session, promo_id: int, promo_in: PromoCodeUpdate) -> Optional[PromoCode]:
    db_promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not db_promo:
        return None
    update_data = promo_in.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_promo, key, value)
    db.commit()
    db.refresh(db_promo)
    return db_promo


def delete_promo(db: Session, promo_id: int) -> Optional[PromoCode]:
    db_promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not db_promo:
        return None
    db.delete(db_promo)
    db.commit()
    return db_promo


def validate_and_apply(db: Session, business_id: int, code: str, amount: float):
    promo = get_promo_by_code(db, business_id, code)
    if not promo:
        return None, "Invalid code"
    if not promo.is_active:
        return None, "Promo code inactive"
    now = datetime.utcnow()
    if promo.start_date and now < promo.start_date:
        return None, "Promo code not active yet"
    if promo.end_date and now > promo.end_date:
        return None, "Promo code expired"
    if promo.usage_limit is not None and promo.used_count >= promo.usage_limit:
        return None, "Promo code usage limit reached"

    if promo.discount_type == "percent":
        discount = amount * (promo.discount_value / 100.0)
    else:
        discount = promo.discount_value
    discount = max(0, min(discount, amount))
    final_amount = amount - discount
    return promo, {
        "originalAmount": amount,
        "discountAmount": discount,
        "finalAmount": final_amount,
        "promoCodeId": promo.id,
    }
