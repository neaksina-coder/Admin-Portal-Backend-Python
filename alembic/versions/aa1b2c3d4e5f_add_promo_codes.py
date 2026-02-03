"""add promo codes

Revision ID: aa1b2c3d4e5f
Revises: 9a1b2c3d4e5f
Create Date: 2026-02-03 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aa1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "9a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "promo_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("discount_type", sa.String(), nullable=False),
        sa.Column("discount_value", sa.Float(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("usage_limit", sa.Integer(), nullable=True),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_promo_codes_id"), "promo_codes", ["id"], unique=False)
    op.create_index(op.f("ix_promo_codes_business_id"), "promo_codes", ["business_id"], unique=False)
    op.create_index(op.f("ix_promo_codes_code"), "promo_codes", ["code"], unique=False)
    op.create_foreign_key(
        "fk_promo_codes_business_id",
        "promo_codes",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.add_column("sales", sa.Column("original_amount", sa.Float(), nullable=True))
    op.add_column("sales", sa.Column("discount_amount", sa.Float(), nullable=True))
    op.add_column("sales", sa.Column("promo_code_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_sales_promo_code_id"), "sales", ["promo_code_id"], unique=False)
    op.create_foreign_key(
        "fk_sales_promo_code_id",
        "sales",
        "promo_codes",
        ["promo_code_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_sales_promo_code_id", "sales", type_="foreignkey")
    op.drop_index(op.f("ix_sales_promo_code_id"), table_name="sales")
    op.drop_column("sales", "promo_code_id")
    op.drop_column("sales", "discount_amount")
    op.drop_column("sales", "original_amount")

    op.drop_constraint("fk_promo_codes_business_id", "promo_codes", type_="foreignkey")
    op.drop_index(op.f("ix_promo_codes_code"), table_name="promo_codes")
    op.drop_index(op.f("ix_promo_codes_business_id"), table_name="promo_codes")
    op.drop_index(op.f("ix_promo_codes_id"), table_name="promo_codes")
    op.drop_table("promo_codes")
