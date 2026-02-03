"""add marketing campaigns

Revision ID: 6d1f2a3b4c5e
Revises: 5a1c9f8b3d2e
Create Date: 2026-02-03 13:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "6d1f2a3b4c5e"
down_revision: Union[str, Sequence[str], None] = "5a1c9f8b3d2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "marketing_campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target_segment", sa.String(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("performance_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("best_time_to_send", sa.String(), nullable=True),
        sa.Column("content_suggestions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_marketing_campaigns_id"), "marketing_campaigns", ["id"], unique=False)
    op.create_index(op.f("ix_marketing_campaigns_business_id"), "marketing_campaigns", ["business_id"], unique=False)
    op.create_index(op.f("ix_marketing_campaigns_name"), "marketing_campaigns", ["name"], unique=False)
    op.create_foreign_key(
        "fk_marketing_campaigns_business_id",
        "marketing_campaigns",
        "businesses",
        ["business_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_marketing_campaigns_business_id", "marketing_campaigns", type_="foreignkey")
    op.drop_index(op.f("ix_marketing_campaigns_name"), table_name="marketing_campaigns")
    op.drop_index(op.f("ix_marketing_campaigns_business_id"), table_name="marketing_campaigns")
    op.drop_index(op.f("ix_marketing_campaigns_id"), table_name="marketing_campaigns")
    op.drop_table("marketing_campaigns")
