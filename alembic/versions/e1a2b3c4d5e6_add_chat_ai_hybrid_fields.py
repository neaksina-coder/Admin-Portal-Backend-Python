"""add chat ai hybrid fields

Revision ID: e1a2b3c4d5e6
Revises: d3e4f5a6b7c8
Create Date: 2026-02-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("chat_conversations", sa.Column("last_admin_reply_at", sa.DateTime(), nullable=True))
    op.add_column("chat_conversations", sa.Column("dify_conversation_id", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chat_conversations", "dify_conversation_id")
    op.drop_column("chat_conversations", "last_admin_reply_at")
