"""add ai insights table

Revision ID: 3e9b4c2d1f7a
Revises: 0f6c8a9b1a2e
Create Date: 2026-02-02 12:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3e9b4c2d1f7a"
down_revision: Union[str, Sequence[str], None] = "0f6c8a9b1a2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("input_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("output_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_ai_insights_id"), "ai_insights", ["id"], unique=False)
    op.create_index(op.f("ix_ai_insights_business_id"), "ai_insights", ["business_id"], unique=False)
    op.create_index(op.f("ix_ai_insights_type"), "ai_insights", ["type"], unique=False)
    op.create_foreign_key(
        "fk_ai_insights_business_id",
        "ai_insights",
        "businesses",
        ["business_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_ai_insights_business_id", "ai_insights", type_="foreignkey")
    op.drop_index(op.f("ix_ai_insights_type"), table_name="ai_insights")
    op.drop_index(op.f("ix_ai_insights_business_id"), table_name="ai_insights")
    op.drop_index(op.f("ix_ai_insights_id"), table_name="ai_insights")
    op.drop_table("ai_insights")
