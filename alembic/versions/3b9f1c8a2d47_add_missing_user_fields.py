"""add missing user fields

Revision ID: 3b9f1c8a2d47
Revises: a2662aa5167c
Create Date: 2026-01-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3b9f1c8a2d47"
down_revision: Union[str, Sequence[str], None] = "a2662aa5167c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("full_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("plan", sa.String(), nullable=True))
    op.add_column("users", sa.Column("billing", sa.String(), nullable=True))
    op.add_column(
        "users",
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'active'")),
    )
    op.add_column("users", sa.Column("company", sa.String(), nullable=True))
    op.add_column("users", sa.Column("country", sa.String(), nullable=True))
    op.add_column("users", sa.Column("contact", sa.String(), nullable=True))

    # Remove default now that existing rows are populated.
    op.alter_column("users", "status", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "contact")
    op.drop_column("users", "country")
    op.drop_column("users", "company")
    op.drop_column("users", "status")
    op.drop_column("users", "billing")
    op.drop_column("users", "plan")
    op.drop_column("users", "full_name")
