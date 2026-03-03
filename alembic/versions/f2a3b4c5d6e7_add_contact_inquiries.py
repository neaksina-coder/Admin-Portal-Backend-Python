"""add contact inquiries

Revision ID: f2a3b4c5d6e7
Revises: e1a2b3c4d5e6
Create Date: 2026-03-02 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "contact_inquiries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("service_interest", sa.String(), nullable=True),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("assigned_to_user_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("replied_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
    )
    op.create_index("ix_contact_inquiries_business_id", "contact_inquiries", ["business_id"])
    op.create_index("ix_contact_inquiries_email", "contact_inquiries", ["email"])
    op.create_index("ix_contact_inquiries_status", "contact_inquiries", ["status"])
    op.create_index("ix_contact_inquiries_assigned_to_user_id", "contact_inquiries", ["assigned_to_user_id"])
    op.create_index("ix_contact_inquiries_source", "contact_inquiries", ["source"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_contact_inquiries_source", table_name="contact_inquiries")
    op.drop_index("ix_contact_inquiries_assigned_to_user_id", table_name="contact_inquiries")
    op.drop_index("ix_contact_inquiries_status", table_name="contact_inquiries")
    op.drop_index("ix_contact_inquiries_email", table_name="contact_inquiries")
    op.drop_index("ix_contact_inquiries_business_id", table_name="contact_inquiries")
    op.drop_table("contact_inquiries")
