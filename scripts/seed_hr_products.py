#!/usr/bin/env python
# scripts/seed_hr_products.py
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db.session import SessionLocal  # noqa: E402
import db.base  # noqa: E402,F401
from models.category import Category  # noqa: E402
from models.product import Product  # noqa: E402


CATEGORIES = [
    {"name": "HR Platform", "slug": "hr-platform", "description": "Core HR management tools"},
    {"name": "Payroll & Attendance", "slug": "payroll", "description": "Time, attendance, and payroll tools"},
    {"name": "People Analytics", "slug": "people-analytics", "description": "HR insights and reporting"},
    {"name": "Employee Experience", "slug": "employee-experience", "description": "Engagement and policy tools"},
]

PRODUCTS = [
    {
        "name": "Employee Directory & Profiles",
        "sku": "HR-EMP-001",
        "description": "Centralized employee records with roles, departments, and documents.",
        "category_slug": "hr-platform",
        "price": 3.0,
        "cost": 1.0,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
    {
        "name": "Leave Management",
        "sku": "HR-LVE-001",
        "description": "Leave requests, approvals, and policy-based balance tracking.",
        "category_slug": "hr-platform",
        "price": 2.5,
        "cost": 0.8,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
    {
        "name": "Attendance & Time Tracking",
        "sku": "HR-ATT-001",
        "description": "Daily check-in/out, overtime, and attendance summaries.",
        "category_slug": "payroll",
        "price": 2.0,
        "cost": 0.7,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
    {
        "name": "Payroll Processing",
        "sku": "HR-PAY-001",
        "description": "Payroll periods, payslips, and approval workflow.",
        "category_slug": "payroll",
        "price": 4.0,
        "cost": 1.5,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
    {
        "name": "Performance Reviews",
        "sku": "HR-PRF-001",
        "description": "Review cycles, goals, and manager feedback tracking.",
        "category_slug": "people-analytics",
        "price": 3.5,
        "cost": 1.2,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
    {
        "name": "HR Analytics Dashboard",
        "sku": "HR-ANL-001",
        "description": "Headcount, attrition, and workforce insights.",
        "category_slug": "people-analytics",
        "price": 2.5,
        "cost": 0.9,
        "stock": 999,
        "unit": "month",
        "status": "active",
    },
    {
        "name": "Hiring Pipeline",
        "sku": "HR-HIR-001",
        "description": "Open roles, candidates, and hiring stage management.",
        "category_slug": "hr-platform",
        "price": 3.0,
        "cost": 1.1,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
    {
        "name": "Policies & Compliance",
        "sku": "HR-PLC-001",
        "description": "Policy distribution, acknowledgements, and compliance tracking.",
        "category_slug": "employee-experience",
        "price": 1.5,
        "cost": 0.5,
        "stock": 999,
        "unit": "user",
        "status": "active",
    },
]


def main():
    parser = argparse.ArgumentParser(description="Seed HR products for a business.")
    parser.add_argument("--business-id", type=int, required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        # Upsert categories
        category_map = {}
        for cat in CATEGORIES:
            existing = (
                db.query(Category)
                .filter(Category.business_id == args.business_id, Category.slug == cat["slug"])
                .first()
            )
            if existing:
                category_map[cat["slug"]] = existing
                continue

            new_cat = Category(
                business_id=args.business_id,
                name=cat["name"],
                slug=cat["slug"],
                description=cat.get("description"),
                status="active",
            )
            db.add(new_cat)
            db.flush()
            category_map[cat["slug"]] = new_cat

        # Upsert products
        for prod in PRODUCTS:
            existing = (
                db.query(Product)
                .filter(Product.business_id == args.business_id, Product.sku == prod["sku"])
                .first()
            )
            if existing:
                continue

            category = category_map.get(prod["category_slug"])
            db.add(
                Product(
                    business_id=args.business_id,
                    name=prod["name"],
                    sku=prod["sku"],
                    description=prod.get("description"),
                    category_id=category.id if category else None,
                    price=prod["price"],
                    cost=prod["cost"],
                    stock=prod["stock"],
                    unit=prod["unit"],
                    status=prod["status"],
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
