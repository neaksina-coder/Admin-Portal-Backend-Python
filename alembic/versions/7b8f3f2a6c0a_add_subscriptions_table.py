"""add subscriptions table

Revision ID: 7b8f3f2a6c0a
Revises: 2d6f1d8f3c3f
Create Date: 2026-02-02 11:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7b8f3f2a6c0a"
down_revision: Union[str, Sequence[str], None] = "2d6f1d8f3c3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("billing_history", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_subscriptions_id"), "subscriptions", ["id"], unique=False)
    op.create_index(
        op.f("ix_subscriptions_business_id"), "subscriptions", ["business_id"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_plan_id"), "subscriptions", ["plan_id"], unique=False
    )
    op.create_foreign_key(
        "fk_subscriptions_business_id",
        "subscriptions",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subscriptions_plan_id",
        "subscriptions",
        "plans",
        ["plan_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_subscriptions_plan_id", "subscriptions", type_="foreignkey")
    op.drop_constraint("fk_subscriptions_business_id", "subscriptions", type_="foreignkey")
    op.drop_index(op.f("ix_subscriptions_plan_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_business_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
