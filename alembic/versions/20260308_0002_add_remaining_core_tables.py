"""add remaining core tables

Revision ID: 20260308_0002
Revises: 20260308_0001
Create Date: 2026-03-08 19:15:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260308_0002"
down_revision: Union[str, Sequence[str], None] = "20260308_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_project_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "version_no", name="uq_course_project_versions_course_id_version_no"),
    )
    op.create_index(
        op.f("ix_course_project_versions_course_id"),
        "course_project_versions",
        ["course_id"],
        unique=False,
    )

    op.create_table(
        "course_plan_options",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("option_key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "option_key", name="uq_course_plan_options_course_id_option_key"),
    )
    op.create_index(
        op.f("ix_course_plan_options_course_id"),
        "course_plan_options",
        ["course_id"],
        unique=False,
    )

    op.create_table(
        "generation_tasks",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("progress_key", sa.String(length=128), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_generation_tasks_course_id"),
        "generation_tasks",
        ["course_id"],
        unique=False,
    )

    op.create_table(
        "generation_task_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("item_key", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("output_json", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["generation_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "item_key", name="uq_generation_task_items_task_id_item_key"),
    )
    op.create_index(
        op.f("ix_generation_task_items_task_id"),
        "generation_task_items",
        ["task_id"],
        unique=False,
    )

    op.create_table(
        "export_records",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=False),
        sa.Column("download_url", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_export_records_course_id"),
        "export_records",
        ["course_id"],
        unique=False,
    )

    op.create_table(
        "usage_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usage_logs_course_id"), "usage_logs", ["course_id"], unique=False)
    op.create_index(op.f("ix_usage_logs_event_type"), "usage_logs", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_usage_logs_event_type"), table_name="usage_logs")
    op.drop_index(op.f("ix_usage_logs_course_id"), table_name="usage_logs")
    op.drop_table("usage_logs")

    op.drop_index(op.f("ix_export_records_course_id"), table_name="export_records")
    op.drop_table("export_records")

    op.drop_index(op.f("ix_generation_task_items_task_id"), table_name="generation_task_items")
    op.drop_table("generation_task_items")

    op.drop_index(op.f("ix_generation_tasks_course_id"), table_name="generation_tasks")
    op.drop_table("generation_tasks")

    op.drop_index(op.f("ix_course_plan_options_course_id"), table_name="course_plan_options")
    op.drop_table("course_plan_options")

    op.drop_index(op.f("ix_course_project_versions_course_id"), table_name="course_project_versions")
    op.drop_table("course_project_versions")
