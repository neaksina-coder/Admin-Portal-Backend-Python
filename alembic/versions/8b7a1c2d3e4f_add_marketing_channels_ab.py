"""add marketing channel and ab testing

Revision ID: 8b7a1c2d3e4f
Revises: 6d1f2a3b4c5e
Create Date: 2026-02-03 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "8b7a1c2d3e4f"
down_revision: Union[str, Sequence[str], None] = "6d1f2a3b4c5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("marketing_campaigns", sa.Column("channel", sa.String(), nullable=True))
    op.add_column(
        "marketing_campaigns",
        sa.Column("ab_variants", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "marketing_campaigns",
        sa.Column("ab_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("marketing_campaigns", sa.Column("ab_winner", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("marketing_campaigns", "ab_winner")
    op.drop_column("marketing_campaigns", "ab_metrics")
    op.drop_column("marketing_campaigns", "ab_variants")
    op.drop_column("marketing_campaigns", "channel")
