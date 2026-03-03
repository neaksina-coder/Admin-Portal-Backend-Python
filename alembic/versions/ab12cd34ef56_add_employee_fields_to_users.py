"""add employee fields to users

Revision ID: ab12cd34ef56
Revises: ff6a7b8c9d0e
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ab12cd34ef56"
down_revision: Union[str, Sequence[str], None] = "ff6a7b8c9d0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("employee_id", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("department", sa.String(), nullable=True))
        batch_op.create_index("ix_users_employee_id", ["employee_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_employee_id")
        batch_op.drop_column("department")
        batch_op.drop_column("employee_id")
