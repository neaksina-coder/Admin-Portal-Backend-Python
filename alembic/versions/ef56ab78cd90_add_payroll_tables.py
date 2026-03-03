"""add payroll tables

Revision ID: ef56ab78cd90
Revises: de45f678ab90
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ef56ab78cd90"
down_revision: Union[str, Sequence[str], None] = "de45f678ab90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pay_periods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_pay_periods_id"), "pay_periods", ["id"], unique=False)
    op.create_index(op.f("ix_pay_periods_business_id"), "pay_periods", ["business_id"], unique=False)
    op.create_index(op.f("ix_pay_periods_status"), "pay_periods", ["status"], unique=False)
    op.create_foreign_key(
        "fk_pay_periods_business_id",
        "pay_periods",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "employee_pay_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pay_type", sa.String(), nullable=False, server_default="monthly"),
        sa.Column("monthly_salary", sa.Float(), nullable=True),
        sa.Column("hourly_rate", sa.Float(), nullable=True),
        sa.Column("overtime_rate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_employee_pay_settings_id"), "employee_pay_settings", ["id"], unique=False)
    op.create_index(op.f("ix_employee_pay_settings_business_id"), "employee_pay_settings", ["business_id"], unique=False)
    op.create_index(op.f("ix_employee_pay_settings_user_id"), "employee_pay_settings", ["user_id"], unique=False)
    op.create_foreign_key(
        "fk_employee_pay_settings_business_id",
        "employee_pay_settings",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_pay_settings_user_id",
        "employee_pay_settings",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_table(
        "payslips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pay_period_id", sa.Integer(), nullable=False),
        sa.Column("gross_pay", sa.Float(), nullable=False, server_default="0"),
        sa.Column("overtime_pay", sa.Float(), nullable=False, server_default="0"),
        sa.Column("deductions", sa.Float(), nullable=False, server_default="0"),
        sa.Column("net_pay", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="generated"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_payslips_id"), "payslips", ["id"], unique=False)
    op.create_index(op.f("ix_payslips_business_id"), "payslips", ["business_id"], unique=False)
    op.create_index(op.f("ix_payslips_user_id"), "payslips", ["user_id"], unique=False)
    op.create_index(op.f("ix_payslips_pay_period_id"), "payslips", ["pay_period_id"], unique=False)
    op.create_index(op.f("ix_payslips_status"), "payslips", ["status"], unique=False)
    op.create_foreign_key(
        "fk_payslips_business_id",
        "payslips",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_payslips_user_id",
        "payslips",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_payslips_pay_period_id",
        "payslips",
        "pay_periods",
        ["pay_period_id"],
        ["id"],
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS payslips CASCADE")
    op.execute("DROP TABLE IF EXISTS employee_pay_settings CASCADE")
    op.execute("DROP TABLE IF EXISTS pay_periods CASCADE")
