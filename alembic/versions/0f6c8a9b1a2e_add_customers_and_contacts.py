"""add customers and contacts

Revision ID: 0f6c8a9b1a2e
Revises: 7b8f3f2a6c0a
Create Date: 2026-02-02 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f6c8a9b1a2e"
down_revision: Union[str, Sequence[str], None] = "7b8f3f2a6c0a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("segment", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("churn_risk_score", sa.Float(), nullable=True),
        sa.Column("lifetime_value", sa.Float(), nullable=True),
        sa.Column("next_best_product", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_customers_id"), "customers", ["id"], unique=False)
    op.create_index(op.f("ix_customers_business_id"), "customers", ["business_id"], unique=False)
    op.create_index(op.f("ix_customers_name"), "customers", ["name"], unique=False)
    op.create_index(op.f("ix_customers_email"), "customers", ["email"], unique=False)
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=False)
    op.create_index(op.f("ix_customers_segment"), "customers", ["segment"], unique=False)
    op.create_foreign_key(
        "fk_customers_business_id",
        "customers",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "customer_contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("contacted_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        op.f("ix_customer_contacts_id"), "customer_contacts", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_customer_contacts_business_id"),
        "customer_contacts",
        ["business_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_contacts_customer_id"),
        "customer_contacts",
        ["customer_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_customer_contacts_business_id",
        "customer_contacts",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_customer_contacts_customer_id",
        "customer_contacts",
        "customers",
        ["customer_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_customer_contacts_customer_id", "customer_contacts", type_="foreignkey")
    op.drop_constraint("fk_customer_contacts_business_id", "customer_contacts", type_="foreignkey")
    op.drop_index(op.f("ix_customer_contacts_customer_id"), table_name="customer_contacts")
    op.drop_index(op.f("ix_customer_contacts_business_id"), table_name="customer_contacts")
    op.drop_index(op.f("ix_customer_contacts_id"), table_name="customer_contacts")
    op.drop_table("customer_contacts")

    op.drop_constraint("fk_customers_business_id", "customers", type_="foreignkey")
    op.drop_index(op.f("ix_customers_segment"), table_name="customers")
    op.drop_index(op.f("ix_customers_phone"), table_name="customers")
    op.drop_index(op.f("ix_customers_email"), table_name="customers")
    op.drop_index(op.f("ix_customers_name"), table_name="customers")
    op.drop_index(op.f("ix_customers_business_id"), table_name="customers")
    op.drop_index(op.f("ix_customers_id"), table_name="customers")
    op.drop_table("customers")
