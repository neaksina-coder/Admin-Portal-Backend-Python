"""add leave policies and balances

Revision ID: c9f1a2b3c4d5
Revises: ec29347f3c04
Create Date: 2026-03-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9f1a2b3c4d5"
down_revision: Union[str, Sequence[str], None] = "ec29347f3c04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leave_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_paid", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("business_id", "name", name="uq_leave_types_business_name"),
    )
    op.create_index(op.f("ix_leave_types_id"), "leave_types", ["id"], unique=False)
    op.create_index(op.f("ix_leave_types_business_id"), "leave_types", ["business_id"], unique=False)
    op.create_foreign_key(
        "fk_leave_types_business_id",
        "leave_types",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "leave_policies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("leave_type_id", sa.Integer(), nullable=False),
        sa.Column("annual_allowance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("accrual_method", sa.String(), nullable=False, server_default="monthly"),
        sa.Column("carryover_days", sa.Float(), nullable=True),
        sa.Column("max_balance", sa.Float(), nullable=True),
        sa.Column("allow_negative", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("business_id", "leave_type_id", name="uq_leave_policies_business_type"),
    )
    op.create_index(op.f("ix_leave_policies_id"), "leave_policies", ["id"], unique=False)
    op.create_index(op.f("ix_leave_policies_business_id"), "leave_policies", ["business_id"], unique=False)
    op.create_index(op.f("ix_leave_policies_leave_type_id"), "leave_policies", ["leave_type_id"], unique=False)
    op.create_foreign_key(
        "fk_leave_policies_business_id",
        "leave_policies",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_leave_policies_leave_type_id",
        "leave_policies",
        "leave_types",
        ["leave_type_id"],
        ["id"],
    )

    op.create_table(
        "employee_leave_balances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("leave_type_id", sa.Integer(), nullable=False),
        sa.Column("balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("used", sa.Float(), nullable=False, server_default="0"),
        sa.Column("pending", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_accrual_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "leave_type_id", name="uq_employee_leave_balance_user_type"),
    )
    op.create_index(op.f("ix_employee_leave_balances_id"), "employee_leave_balances", ["id"], unique=False)
    op.create_index(op.f("ix_employee_leave_balances_business_id"), "employee_leave_balances", ["business_id"], unique=False)
    op.create_index(op.f("ix_employee_leave_balances_user_id"), "employee_leave_balances", ["user_id"], unique=False)
    op.create_index(op.f("ix_employee_leave_balances_leave_type_id"), "employee_leave_balances", ["leave_type_id"], unique=False)
    op.create_foreign_key(
        "fk_employee_leave_balances_business_id",
        "employee_leave_balances",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_leave_balances_user_id",
        "employee_leave_balances",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_leave_balances_leave_type_id",
        "employee_leave_balances",
        "leave_types",
        ["leave_type_id"],
        ["id"],
    )

    op.create_table(
        "leave_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("leave_type_id", sa.Integer(), nullable=False),
        sa.Column("change", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("ref_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_leave_transactions_id"), "leave_transactions", ["id"], unique=False)
    op.create_index(op.f("ix_leave_transactions_business_id"), "leave_transactions", ["business_id"], unique=False)
    op.create_index(op.f("ix_leave_transactions_user_id"), "leave_transactions", ["user_id"], unique=False)
    op.create_index(op.f("ix_leave_transactions_leave_type_id"), "leave_transactions", ["leave_type_id"], unique=False)
    op.create_foreign_key(
        "fk_leave_transactions_business_id",
        "leave_transactions",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_leave_transactions_user_id",
        "leave_transactions",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_leave_transactions_leave_type_id",
        "leave_transactions",
        "leave_types",
        ["leave_type_id"],
        ["id"],
    )

    op.add_column("leave_requests", sa.Column("leave_type_id", sa.Integer(), nullable=True))
    op.add_column("leave_requests", sa.Column("days_requested", sa.Float(), nullable=True))
    op.create_index(op.f("ix_leave_requests_leave_type_id"), "leave_requests", ["leave_type_id"], unique=False)
    op.create_foreign_key(
        "fk_leave_requests_leave_type_id",
        "leave_requests",
        "leave_types",
        ["leave_type_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_leave_requests_leave_type_id", "leave_requests", type_="foreignkey")
    op.drop_index(op.f("ix_leave_requests_leave_type_id"), table_name="leave_requests")
    op.drop_column("leave_requests", "days_requested")
    op.drop_column("leave_requests", "leave_type_id")

    op.execute("DROP TABLE IF EXISTS leave_transactions CASCADE")
    op.execute("DROP TABLE IF EXISTS employee_leave_balances CASCADE")
    op.execute("DROP TABLE IF EXISTS leave_policies CASCADE")
    op.execute("DROP TABLE IF EXISTS leave_types CASCADE")
