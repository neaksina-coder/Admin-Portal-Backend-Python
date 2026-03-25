# crud/product.py
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, *, business_id: int, sku: str) -> Optional[Product]:
    return (
        db.query(Product)
        .filter(Product.business_id == business_id, Product.sku == sku)
        .first()
    )


def list_products(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Product]:
    query = db.query(Product).filter(Product.business_id == business_id)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if status:
        query = query.filter(Product.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(like),
                Product.sku.ilike(like),
            )
        )
    return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()


def count_products(
    db: Session,
    *,
    business_id: int,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
) -> int:
    query = db.query(Product).filter(Product.business_id == business_id)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if status:
        query = query.filter(Product.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(like),
                Product.sku.ilike(like),
            )
        )
    return query.count()


def create_product(db: Session, product_in: ProductCreate) -> Product:
    db_product = Product(**product_in.dict(by_alias=False))
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_in: ProductUpdate) -> Optional[Product]:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    update_data = product_in.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


# def delete_product(db: Session, product_id: int) -> Optional[Product]:
#     db_product = db.query(Product).filter(Product.id == product_id).first()
#     if not db_product:
#         return None
#     db.delete(db_product)
#     db.commit()
#     return db_product
def delete_product(db: Session, product_id: int) -> Optional[Product]:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None 
    db.delete(db_product)
    db.commit()
    return db_product
