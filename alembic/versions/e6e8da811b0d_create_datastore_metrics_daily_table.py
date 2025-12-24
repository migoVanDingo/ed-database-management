"""create datastore_metrics_daily table

Revision ID: e6e8da811b0d
Revises: c9d34733a311
Create Date: 2025-12-24 10:19:42.740314

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e6e8da811b0d"
down_revision: Union[str, Sequence[str], None] = "c9d34733a311"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "datastore_metrics_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "datastore_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datastores.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # UTC day snapshot (date-only)
        sa.Column("day", sa.Date(), nullable=False),
        # Snapshot fields
        sa.Column("file_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("dataset_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("project_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # One row per datastore per day
    op.create_unique_constraint(
        "uq_datastore_metrics_daily_datastore_day",
        "datastore_metrics_daily",
        ["datastore_id", "day"],
    )

    # Helpful index for time-series queries (e.g., last 30 days)
    op.create_index(
        "ix_datastore_metrics_daily_datastore_day",
        "datastore_metrics_daily",
        ["datastore_id", "day"],
    )


def downgrade():
    op.drop_index(
        "ix_datastore_metrics_daily_datastore_day", table_name="datastore_metrics_daily"
    )
    op.drop_constraint(
        "uq_datastore_metrics_daily_datastore_day",
        "datastore_metrics_daily",
        type_="unique",
    )
    op.drop_table("datastore_metrics_daily")
