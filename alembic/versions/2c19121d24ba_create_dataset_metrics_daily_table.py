"""create dataset_metrics_daily table

Revision ID: 2c19121d24ba
Revises: e6e8da811b0d
Create Date: 2025-12-24 10:20:13.578574

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2c19121d24ba"
down_revision: Union[str, Sequence[str], None] = "e6e8da811b0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "dataset_metrics_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("file_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "project_usage_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("version_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "collaborator_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_unique_constraint(
        "uq_dataset_metrics_daily_dataset_day",
        "dataset_metrics_daily",
        ["dataset_id", "day"],
    )

    op.create_index(
        "ix_dataset_metrics_daily_dataset_day",
        "dataset_metrics_daily",
        ["dataset_id", "day"],
    )


def downgrade():
    op.drop_index(
        "ix_dataset_metrics_daily_dataset_day", table_name="dataset_metrics_daily"
    )
    op.drop_constraint(
        "uq_dataset_metrics_daily_dataset_day", "dataset_metrics_daily", type_="unique"
    )
    op.drop_table("dataset_metrics_daily")
