"""add leave requests

Revision ID: bc23de45f678
Revises: ab12cd34ef56
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bc23de45f678"
down_revision: Union[str, Sequence[str], None] = "ab12cd34ef56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("leave_type", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("approved_by_user_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_leave_requests_id"), "leave_requests", ["id"], unique=False)
    op.create_index(op.f("ix_leave_requests_business_id"), "leave_requests", ["business_id"], unique=False)
    op.create_index(op.f("ix_leave_requests_user_id"), "leave_requests", ["user_id"], unique=False)
    op.create_index(op.f("ix_leave_requests_status"), "leave_requests", ["status"], unique=False)
    op.create_index(
        op.f("ix_leave_requests_approved_by_user_id"),
        "leave_requests",
        ["approved_by_user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_leave_requests_business_id",
        "leave_requests",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_leave_requests_user_id",
        "leave_requests",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_leave_requests_approved_by_user_id",
        "leave_requests",
        "users",
        ["approved_by_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS leave_requests CASCADE")
