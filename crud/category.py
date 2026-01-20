# crud/category.py
from sqlalchemy.orm import Session
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate
from typing import Optional, List

def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get a single category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    """Get a single category by slug"""
    return db.query(Category).filter(Category.slug == slug).first()

def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
) -> List[Category]:
    """Get all categories with optional filters"""
    query = db.query(Category)
    
    if status:
        query = query.filter(Category.status == status)
    
    return query.offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate) -> Category:
    """Create a new category"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(
    db: Session, 
    category_id: int, 
    category: CategoryUpdate
) -> Optional[Category]:
    """Update an existing category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category:
        update_data = category.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Optional[Category]:
    """Delete a category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category