# crud/product.py
from sqlalchemy.orm import Session
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from typing import Optional, List

def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get a single product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """Get a single product by SKU"""
    return db.query(Product).filter(Product.sku == sku).first()

def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,  # Changed from category string
    status: Optional[str] = None
) -> List[Product]:
    """Get all products with optional filters"""
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if status:
        query = query.filter(Product.status == status)
    
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate) -> Product:
    """Create a new product"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(
    db: Session, 
    product_id: int, 
    product: ProductUpdate
) -> Optional[Product]:
    """Update an existing product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> Optional[Product]:
    """Delete a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product