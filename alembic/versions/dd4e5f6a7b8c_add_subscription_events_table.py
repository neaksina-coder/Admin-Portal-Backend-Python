"""add subscription events table

Revision ID: dd4e5f6a7b8c
Revises: cc3d4e5f6a7b
Create Date: 2026-02-04 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "dd4e5f6a7b8c"
down_revision: Union[str, Sequence[str], None] = "cc3d4e5f6a7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "subscription_events" in tables:
        return

    op.create_table(
        "subscription_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_subscription_events_id"), "subscription_events", ["id"], unique=False)
    op.create_index(op.f("ix_subscription_events_subscription_id"), "subscription_events", ["subscription_id"], unique=False)
    op.create_index(op.f("ix_subscription_events_business_id"), "subscription_events", ["business_id"], unique=False)
    op.create_index(op.f("ix_subscription_events_invoice_id"), "subscription_events", ["invoice_id"], unique=False)
    op.create_index(op.f("ix_subscription_events_actor_user_id"), "subscription_events", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_subscription_events_event_type"), "subscription_events", ["event_type"], unique=False)

    op.create_foreign_key(
        "fk_subscription_events_subscription_id",
        "subscription_events",
        "subscriptions",
        ["subscription_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subscription_events_business_id",
        "subscription_events",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subscription_events_invoice_id",
        "subscription_events",
        "invoices",
        ["invoice_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subscription_events_actor_user_id",
        "subscription_events",
        "users",
        ["actor_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS subscription_events CASCADE")
