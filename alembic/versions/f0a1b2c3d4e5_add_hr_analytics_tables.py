"""add hr analytics tables

Revision ID: f0a1b2c3d4e5
Revises: d7e8f9a0b1c2
Create Date: 2026-03-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f0a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "d7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hr_performance_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("review_period", sa.Date(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("goals_achieved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend", sa.String(), nullable=False, server_default="flat"),
        sa.Column("metric_quality", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metric_speed", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metric_collaboration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metric_initiative", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metric_reliability", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_hr_performance_reviews_id"), "hr_performance_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_hr_performance_reviews_business_id"), "hr_performance_reviews", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_performance_reviews_user_id"), "hr_performance_reviews", ["user_id"], unique=False)
    op.create_index(op.f("ix_hr_performance_reviews_review_period"), "hr_performance_reviews", ["review_period"], unique=False)
    op.create_foreign_key(
        "fk_hr_performance_reviews_business_id",
        "hr_performance_reviews",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_hr_performance_reviews_user_id",
        "hr_performance_reviews",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_table(
        "hr_budget_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("annual_budget", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("business_id", "year", name="uq_hr_budget_plan_business_year"),
    )
    op.create_index(op.f("ix_hr_budget_plans_id"), "hr_budget_plans", ["id"], unique=False)
    op.create_index(op.f("ix_hr_budget_plans_business_id"), "hr_budget_plans", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_budget_plans_year"), "hr_budget_plans", ["year"], unique=False)
    op.create_foreign_key(
        "fk_hr_budget_plans_business_id",
        "hr_budget_plans",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "hr_budget_months",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("budget", sa.Float(), nullable=False, server_default="0"),
        sa.Column("actual", sa.Float(), nullable=False, server_default="0"),
        sa.Column("forecast", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("business_id", "year", "month", name="uq_hr_budget_month_business_year_month"),
    )
    op.create_index(op.f("ix_hr_budget_months_id"), "hr_budget_months", ["id"], unique=False)
    op.create_index(op.f("ix_hr_budget_months_business_id"), "hr_budget_months", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_budget_months_year"), "hr_budget_months", ["year"], unique=False)
    op.create_index(op.f("ix_hr_budget_months_month"), "hr_budget_months", ["month"], unique=False)
    op.create_foreign_key(
        "fk_hr_budget_months_business_id",
        "hr_budget_months",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "hr_budget_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("allocated", sa.Float(), nullable=False, server_default="0"),
        sa.Column("spent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_hr_budget_categories_id"), "hr_budget_categories", ["id"], unique=False)
    op.create_index(op.f("ix_hr_budget_categories_business_id"), "hr_budget_categories", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_budget_categories_year"), "hr_budget_categories", ["year"], unique=False)
    op.create_index(op.f("ix_hr_budget_categories_name"), "hr_budget_categories", ["name"], unique=False)
    op.create_foreign_key(
        "fk_hr_budget_categories_business_id",
        "hr_budget_categories",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "hr_headcount_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_month", sa.Date(), nullable=False),
        sa.Column("headcount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("business_id", "snapshot_month", name="uq_hr_headcount_business_month"),
    )
    op.create_index(op.f("ix_hr_headcount_snapshots_id"), "hr_headcount_snapshots", ["id"], unique=False)
    op.create_index(op.f("ix_hr_headcount_snapshots_business_id"), "hr_headcount_snapshots", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_headcount_snapshots_snapshot_month"), "hr_headcount_snapshots", ["snapshot_month"], unique=False)
    op.create_foreign_key(
        "fk_hr_headcount_snapshots_business_id",
        "hr_headcount_snapshots",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "hr_employee_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_hr_employee_events_id"), "hr_employee_events", ["id"], unique=False)
    op.create_index(op.f("ix_hr_employee_events_business_id"), "hr_employee_events", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_employee_events_user_id"), "hr_employee_events", ["user_id"], unique=False)
    op.create_index(op.f("ix_hr_employee_events_event_type"), "hr_employee_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_hr_employee_events_event_date"), "hr_employee_events", ["event_date"], unique=False)
    op.create_foreign_key(
        "fk_hr_employee_events_business_id",
        "hr_employee_events",
        "businesses",
        ["business_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_hr_employee_events_user_id",
        "hr_employee_events",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_table(
        "hr_hiring_positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("opened_at", sa.Date(), nullable=False),
        sa.Column("closed_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_hr_hiring_positions_id"), "hr_hiring_positions", ["id"], unique=False)
    op.create_index(op.f("ix_hr_hiring_positions_business_id"), "hr_hiring_positions", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_hiring_positions_department"), "hr_hiring_positions", ["department"], unique=False)
    op.create_index(op.f("ix_hr_hiring_positions_status"), "hr_hiring_positions", ["status"], unique=False)
    op.create_foreign_key(
        "fk_hr_hiring_positions_business_id",
        "hr_hiring_positions",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_table(
        "hr_hiring_pipeline",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False),
        sa.Column("applicants", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("business_id", "stage", name="uq_hr_hiring_pipeline_business_stage"),
    )
    op.create_index(op.f("ix_hr_hiring_pipeline_id"), "hr_hiring_pipeline", ["id"], unique=False)
    op.create_index(op.f("ix_hr_hiring_pipeline_business_id"), "hr_hiring_pipeline", ["business_id"], unique=False)
    op.create_index(op.f("ix_hr_hiring_pipeline_stage"), "hr_hiring_pipeline", ["stage"], unique=False)
    op.create_foreign_key(
        "fk_hr_hiring_pipeline_business_id",
        "hr_hiring_pipeline",
        "businesses",
        ["business_id"],
        ["id"],
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS hr_hiring_pipeline CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_hiring_positions CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_employee_events CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_headcount_snapshots CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_budget_categories CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_budget_months CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_budget_plans CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_performance_reviews CASCADE")
