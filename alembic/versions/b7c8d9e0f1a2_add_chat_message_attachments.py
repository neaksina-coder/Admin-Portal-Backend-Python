"""add chat message attachments

Revision ID: b7c8d9e0f1a2
Revises: 0e25f0cd9ae0
Create Date: 2026-02-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "0e25f0cd9ae0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("chat_messages", sa.Column("attachment_url", sa.String(), nullable=True))
    op.add_column("chat_messages", sa.Column("attachment_type", sa.String(), nullable=True))
    op.add_column("chat_messages", sa.Column("attachment_name", sa.String(), nullable=True))
    op.add_column("chat_messages", sa.Column("attachment_size", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chat_messages", "attachment_size")
    op.drop_column("chat_messages", "attachment_name")
    op.drop_column("chat_messages", "attachment_type")
    op.drop_column("chat_messages", "attachment_url")
