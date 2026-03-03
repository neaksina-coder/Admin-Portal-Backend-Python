"""add leave decision note

Revision ID: cd34ef56ab78
Revises: bc23de45f678
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cd34ef56ab78"
down_revision: Union[str, Sequence[str], None] = "bc23de45f678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("leave_requests") as batch_op:
        batch_op.add_column(sa.Column("decision_note", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("leave_requests") as batch_op:
        batch_op.drop_column("decision_note")
