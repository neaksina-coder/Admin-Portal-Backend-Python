"""add user lookup tables

Revision ID: 7f1d4e2b9c1a
Revises: 3b9f1c8a2d47
Create Date: 2026-01-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "7f1d4e2b9c1a"
down_revision: Union[str, Sequence[str], None] = "3b9f1c8a2d47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "user_roles" not in tables:
        op.create_table(
            "user_roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("value", sa.String(), nullable=False),
            sa.Column("label", sa.String(), nullable=False),
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("value"),
        )
        op.create_index("ix_user_roles_value", "user_roles", ["value"])

    if "user_plans" not in tables:
        op.create_table(
            "user_plans",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("value", sa.String(), nullable=False),
            sa.Column("label", sa.String(), nullable=False),
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("value"),
        )
        op.create_index("ix_user_plans_value", "user_plans", ["value"])

    if "user_statuses" not in tables:
        op.create_table(
            "user_statuses",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("value", sa.String(), nullable=False),
            sa.Column("label", sa.String(), nullable=False),
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("value"),
        )
        op.create_index("ix_user_statuses_value", "user_statuses", ["value"])

    if "user_billings" not in tables:
        op.create_table(
            "user_billings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("value", sa.String(), nullable=False),
            sa.Column("label", sa.String(), nullable=False),
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("value"),
        )
        op.create_index("ix_user_billings_value", "user_billings", ["value"])

    user_columns = {col["name"] for col in inspector.get_columns("users")}
    if "role_id" not in user_columns:
        op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    if "plan_id" not in user_columns:
        op.add_column("users", sa.Column("plan_id", sa.Integer(), nullable=True))
    if "status_id" not in user_columns:
        op.add_column("users", sa.Column("status_id", sa.Integer(), nullable=True))
    if "billing_id" not in user_columns:
        op.add_column("users", sa.Column("billing_id", sa.Integer(), nullable=True))

    fk_names = {fk["name"] for fk in inspector.get_foreign_keys("users")}
    if "fk_users_role_id_user_roles" not in fk_names:
        op.create_foreign_key(
            "fk_users_role_id_user_roles", "users", "user_roles", ["role_id"], ["id"]
        )
    if "fk_users_plan_id_user_plans" not in fk_names:
        op.create_foreign_key(
            "fk_users_plan_id_user_plans", "users", "user_plans", ["plan_id"], ["id"]
        )
    if "fk_users_status_id_user_statuses" not in fk_names:
        op.create_foreign_key(
            "fk_users_status_id_user_statuses",
            "users",
            "user_statuses",
            ["status_id"],
            ["id"],
        )
    if "fk_users_billing_id_user_billings" not in fk_names:
        op.create_foreign_key(
            "fk_users_billing_id_user_billings",
            "users",
            "user_billings",
            ["billing_id"],
            ["id"],
        )

    op.execute(
        "UPDATE user_roles SET created_at = NOW() WHERE created_at IS NULL"
    )
    op.execute(
        "UPDATE user_plans SET created_at = NOW() WHERE created_at IS NULL"
    )
    op.execute(
        "UPDATE user_statuses SET created_at = NOW() WHERE created_at IS NULL"
    )
    op.execute(
        "UPDATE user_billings SET created_at = NOW() WHERE created_at IS NULL"
    )

    op.execute(
        "INSERT INTO user_roles (value, label, sort_order, created_at) VALUES "
        "('user','User',1,NOW()),('admin','Admin',2,NOW()),('superuser','Superuser',3,NOW()) "
        "ON CONFLICT (value) DO NOTHING"
    )
    op.execute(
        "INSERT INTO user_plans (value, label, sort_order, created_at) VALUES "
        "('basic','Basic',1,NOW()),('company','Company',2,NOW()),"
        "('enterprise','Enterprise',3,NOW()),('team','Team',4,NOW()) "
        "ON CONFLICT (value) DO NOTHING"
    )
    op.execute(
        "INSERT INTO user_statuses (value, label, sort_order, created_at) VALUES "
        "('active','Active',1,NOW()),('inactive','Inactive',2,NOW()),('pending','Pending',3,NOW()) "
        "ON CONFLICT (value) DO NOTHING"
    )

    op.execute(
        "UPDATE users SET role_id = (SELECT id FROM user_roles WHERE value = users.role) "
        "WHERE role_id IS NULL AND role IS NOT NULL"
    )

    op.execute(
        "INSERT INTO user_plans (value, label, sort_order, created_at) "
        "SELECT DISTINCT plan, plan, 0, NOW() FROM users "
        "WHERE plan IS NOT NULL AND plan NOT IN (SELECT value FROM user_plans)"
    )
    op.execute(
        "UPDATE users SET plan_id = (SELECT id FROM user_plans WHERE value = users.plan) "
        "WHERE plan_id IS NULL AND plan IS NOT NULL"
    )

    op.execute(
        "UPDATE users SET status_id = (SELECT id FROM user_statuses WHERE value = users.status) "
        "WHERE status_id IS NULL AND status IS NOT NULL"
    )

    op.execute(
        "INSERT INTO user_billings (value, label, sort_order, created_at) "
        "SELECT DISTINCT billing, billing, 0, NOW() FROM users "
        "WHERE billing IS NOT NULL AND billing NOT IN (SELECT value FROM user_billings)"
    )
    op.execute(
        "UPDATE users SET billing_id = (SELECT id FROM user_billings WHERE value = users.billing) "
        "WHERE billing_id IS NULL AND billing IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_billing_id_user_billings", "users", type_="foreignkey")
    op.drop_constraint("fk_users_status_id_user_statuses", "users", type_="foreignkey")
    op.drop_constraint("fk_users_plan_id_user_plans", "users", type_="foreignkey")
    op.drop_constraint("fk_users_role_id_user_roles", "users", type_="foreignkey")

    op.drop_column("users", "billing_id")
    op.drop_column("users", "status_id")
    op.drop_column("users", "plan_id")
    op.drop_column("users", "role_id")

    op.drop_index("ix_user_billings_value", table_name="user_billings")
    op.drop_index("ix_user_statuses_value", table_name="user_statuses")
    op.drop_index("ix_user_plans_value", table_name="user_plans")
    op.drop_index("ix_user_roles_value", table_name="user_roles")

    op.drop_table("user_billings")
    op.drop_table("user_statuses")
    op.drop_table("user_plans")
    op.drop_table("user_roles")
