# crud/category.py
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.category import Category
from models.product import Product
from schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, *, business_id: int, slug: str) -> Optional[Category]:
    return (
        db.query(Category)
        .filter(Category.business_id == business_id, Category.slug == slug)
        .first()
    )


def list_categories(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Category]:
    query = db.query(Category).filter(Category.business_id == business_id)
    if status:
        query = query.filter(Category.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Category.name.ilike(like), Category.slug.ilike(like)))
    return query.order_by(Category.created_at.desc()).offset(skip).limit(limit).all()


def count_categories(
    db: Session,
    *,
    business_id: int,
    status: Optional[str] = None,
    q: Optional[str] = None,
) -> int:
    query = db.query(Category).filter(Category.business_id == business_id)
    if status:
        query = query.filter(Category.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Category.name.ilike(like), Category.slug.ilike(like)))
    return query.count()


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    db_category = Category(**category_in.dict(by_alias=False))
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None
    update_data = category_in.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> Optional[Category]:
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None

    db.query(Product).filter(Product.category_id == category_id).update({"category_id": None})
    db.delete(db_category)
    db.commit()
    return db_category
