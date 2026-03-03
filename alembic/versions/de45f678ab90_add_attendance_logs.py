"""add attendance logs

Revision ID: de45f678ab90
Revises: cd34ef56ab78
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "de45f678ab90"
down_revision: Union[str, Sequence[str], None] = "cd34ef56ab78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attendance_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("check_in_at", sa.DateTime(), nullable=False),
        sa.Column("check_out_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="present"),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_attendance_logs_id"), "attendance_logs", ["id"], unique=False)
    op.create_index(op.f("ix_attendance_logs_business_id"), "attendance_logs", ["business_id"], unique=False)
    op.create_index(op.f("ix_attendance_logs_user_id"), "attendance_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_attendance_logs_work_date"), "attendance_logs", ["work_date"], unique=False)
    op.create_index(op.f("ix_attendance_logs_status"), "attendance_logs", ["status"], unique=False)
    op.create_foreign_key(
        "fk_attendance_logs_business_id",
        "attendance_logs",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_attendance_logs_user_id",
        "attendance_logs",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS attendance_logs CASCADE")
