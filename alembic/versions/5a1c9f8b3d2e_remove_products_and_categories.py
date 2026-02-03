"""remove products and categories

Revision ID: 5a1c9f8b3d2e
Revises: 4c2f7d1a9b0e
Create Date: 2026-02-03 13:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a1c9f8b3d2e"
down_revision: Union[str, Sequence[str], None] = "4c2f7d1a9b0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE sales DROP CONSTRAINT IF EXISTS fk_sales_product_id")
    op.execute("DROP INDEX IF EXISTS ix_sales_product_id")
    op.execute("ALTER TABLE sales DROP COLUMN IF EXISTS product_id")

    op.execute("DROP TABLE IF EXISTS products")
    op.execute("DROP TABLE IF EXISTS categories")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=False)
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
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
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)
    op.create_index(op.f("ix_products_category_id"), "products", ["category_id"], unique=False)
    op.create_foreign_key(
        "fk_products_category_id",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )

    op.add_column("sales", sa.Column("product_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_sales_product_id"), "sales", ["product_id"], unique=False)
    op.create_foreign_key(
        "fk_sales_product_id",
        "sales",
        "products",
        ["product_id"],
        ["id"],
    )
