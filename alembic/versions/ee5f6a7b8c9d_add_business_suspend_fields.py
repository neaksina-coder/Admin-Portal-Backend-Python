"""add business suspend fields

Revision ID: ee5f6a7b8c9d
Revises: dd4e5f6a7b8c
Create Date: 2026-02-04 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ee5f6a7b8c9d"
down_revision: Union[str, Sequence[str], None] = "dd4e5f6a7b8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("businesses")}

    if "suspended_at" not in columns:
        op.add_column("businesses", sa.Column("suspended_at", sa.DateTime(), nullable=True))
    if "suspended_reason" not in columns:
        op.add_column("businesses", sa.Column("suspended_reason", sa.String(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("businesses")}

    if "suspended_reason" in columns:
        op.drop_column("businesses", "suspended_reason")
    if "suspended_at" in columns:
        op.drop_column("businesses", "suspended_at")
