"""add sales table

Revision ID: 4c2f7d1a9b0e
Revises: 3e9b4c2d1f7a
Create Date: 2026-02-03 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4c2f7d1a9b0e"
down_revision: Union[str, Sequence[str], None] = "3e9b4c2d1f7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("transaction_date", sa.DateTime(), nullable=False),
        sa.Column("invoice_number", sa.String(), nullable=True),
        sa.Column("demand_prediction", sa.Float(), nullable=True),
        sa.Column("anomaly_flag", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_sales_id"), "sales", ["id"], unique=False)
    op.create_index(op.f("ix_sales_customer_id"), "sales", ["customer_id"], unique=False)
    op.create_index(op.f("ix_sales_business_id"), "sales", ["business_id"], unique=False)
    op.create_index(op.f("ix_sales_product_id"), "sales", ["product_id"], unique=False)
    op.create_index(op.f("ix_sales_invoice_number"), "sales", ["invoice_number"], unique=False)
    op.create_foreign_key(
        "fk_sales_business_id",
        "sales",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_sales_customer_id",
        "sales",
        "customers",
        ["customer_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_sales_product_id",
        "sales",
        "products",
        ["product_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_sales_product_id", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_customer_id", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_business_id", "sales", type_="foreignkey")
    op.drop_index(op.f("ix_sales_invoice_number"), table_name="sales")
    op.drop_index(op.f("ix_sales_product_id"), table_name="sales")
    op.drop_index(op.f("ix_sales_business_id"), table_name="sales")
    op.drop_index(op.f("ix_sales_customer_id"), table_name="sales")
    op.drop_index(op.f("ix_sales_id"), table_name="sales")
    op.drop_table("sales")
