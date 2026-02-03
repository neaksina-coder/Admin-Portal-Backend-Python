"""add businesses and link users

Revision ID: 9c6b9b2e5f1a
Revises: f7047335459d
Create Date: 2026-02-02 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c6b9b2e5f1a"
down_revision: Union[str, Sequence[str], None] = "f7047335459d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(op.f("ix_businesses_id"), "businesses", ["id"], unique=False)
    op.create_index(op.f("ix_businesses_name"), "businesses", ["name"], unique=False)
    op.create_index(
        op.f("ix_businesses_tenant_id"), "businesses", ["tenant_id"], unique=True
    )
    op.create_index(
        op.f("ix_businesses_plan_id"), "businesses", ["plan_id"], unique=False
    )

    op.add_column("users", sa.Column("business_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_users_business_id"), "users", ["business_id"], unique=False)
    op.create_foreign_key(
        "fk_users_business_id",
        "users",
        "businesses",
        ["business_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_users_business_id", "users", type_="foreignkey")
    op.drop_index(op.f("ix_users_business_id"), table_name="users")
    op.drop_column("users", "business_id")

    op.drop_index(op.f("ix_businesses_plan_id"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_tenant_id"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_name"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_id"), table_name="businesses")
    op.drop_table("businesses")
