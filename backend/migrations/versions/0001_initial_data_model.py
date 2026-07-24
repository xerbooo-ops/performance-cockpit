"""Create metric, import batch and measurement tables.

Revision ID: 0001
Revises:
Create Date: 2026-07-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "metric_definitions",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("aggregation", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "aggregation IN ('sum', 'average')",
            name="ck_metric_definitions_aggregation",
        ),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("imported_rows", sa.Integer(), nullable=False),
        sa.Column("failed_rows", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "measurements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("metric_key", sa.String(length=64), nullable=False),
        sa.Column("organizational_unit", sa.String(length=120), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("target_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("import_batch_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("period_end >= period_start", name="ck_measurements_period"),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["metric_key"], ["metric_definitions.key"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "metric_key",
            "organizational_unit",
            "period_start",
            "period_end",
            name="uq_measurement_period",
        ),
    )
    op.create_index(
        op.f("ix_measurements_metric_key"), "measurements", ["metric_key"], unique=False
    )
    op.create_index(
        op.f("ix_measurements_organizational_unit"),
        "measurements",
        ["organizational_unit"],
        unique=False,
    )
    op.create_index(
        op.f("ix_measurements_period_start"),
        "measurements",
        ["period_start"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_measurements_period_start"), table_name="measurements")
    op.drop_index(op.f("ix_measurements_organizational_unit"), table_name="measurements")
    op.drop_index(op.f("ix_measurements_metric_key"), table_name="measurements")
    op.drop_table("measurements")
    op.drop_table("import_batches")
    op.drop_table("metric_definitions")
