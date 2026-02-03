"""add marketing email logs

Revision ID: 9a1b2c3d4e5f
Revises: 8b7a1c2d3e4f
Create Date: 2026-02-03 14:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "8b7a1c2d3e4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "marketing_email_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("recipient_email", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_marketing_email_logs_id"), "marketing_email_logs", ["id"], unique=False)
    op.create_index(
        op.f("ix_marketing_email_logs_campaign_id"),
        "marketing_email_logs",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_marketing_email_logs_business_id"),
        "marketing_email_logs",
        ["business_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_marketing_email_logs_recipient_email"),
        "marketing_email_logs",
        ["recipient_email"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_marketing_email_logs_campaign_id",
        "marketing_email_logs",
        "marketing_campaigns",
        ["campaign_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_marketing_email_logs_business_id",
        "marketing_email_logs",
        "businesses",
        ["business_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_marketing_email_logs_business_id", "marketing_email_logs", type_="foreignkey")
    op.drop_constraint("fk_marketing_email_logs_campaign_id", "marketing_email_logs", type_="foreignkey")
    op.drop_index(op.f("ix_marketing_email_logs_recipient_email"), table_name="marketing_email_logs")
    op.drop_index(op.f("ix_marketing_email_logs_business_id"), table_name="marketing_email_logs")
    op.drop_index(op.f("ix_marketing_email_logs_campaign_id"), table_name="marketing_email_logs")
    op.drop_index(op.f("ix_marketing_email_logs_id"), table_name="marketing_email_logs")
    op.drop_table("marketing_email_logs")
