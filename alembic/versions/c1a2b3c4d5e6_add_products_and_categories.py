"""add products and categories

Revision ID: c1a2b3c4d5e6
Revises: f0a1b2c3d4e5
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "c1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "categories" not in existing_tables:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("business_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("slug", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("business_id", "slug", name="uq_categories_business_slug"),
        )
        op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
        op.create_index(op.f("ix_categories_business_id"), "categories", ["business_id"], unique=False)
        op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=False)
        op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=False)
        op.create_foreign_key(
            "fk_categories_business_id",
            "categories",
            "businesses",
            ["business_id"],
            ["id"],
        )

    if "products" not in existing_tables:
        op.create_table(
            "products",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("business_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("sku", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("price", sa.Float(), nullable=False),
            sa.Column("cost", sa.Float(), nullable=True),
            sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("unit", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("business_id", "sku", name="uq_products_business_sku"),
        )
        op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
        op.create_index(op.f("ix_products_business_id"), "products", ["business_id"], unique=False)
        op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
        op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=False)
        op.create_index(op.f("ix_products_category_id"), "products", ["category_id"], unique=False)
        op.create_foreign_key(
            "fk_products_business_id",
            "products",
            "businesses",
            ["business_id"],
            ["id"],
        )
        op.create_foreign_key(
            "fk_products_category_id",
            "products",
            "categories",
            ["category_id"],
            ["id"],
        )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS products CASCADE")
    op.execute("DROP TABLE IF EXISTS categories CASCADE")
