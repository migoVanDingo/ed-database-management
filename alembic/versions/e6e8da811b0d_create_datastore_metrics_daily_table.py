"""create datastore_metrics_daily table

Revision ID: e6e8da811b0d
Revises: c9d34733a311
Create Date: 2025-12-24 10:19:42.740314

"""
# Idempotent table creation to avoid DuplicateTable errors.

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
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'datastore_metrics_daily'
            ) THEN
                CREATE TABLE datastore_metrics_daily (
                    id UUID DEFAULT gen_random_uuid() NOT NULL,
                    datastore_id UUID NOT NULL,
                    day DATE NOT NULL,
                    file_count BIGINT DEFAULT '0' NOT NULL,
                    total_bytes BIGINT DEFAULT '0' NOT NULL,
                    dataset_count INTEGER DEFAULT '0' NOT NULL,
                    project_count INTEGER DEFAULT '0' NOT NULL,
                    likes INTEGER DEFAULT '0' NOT NULL,
                    shares INTEGER DEFAULT '0' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (id),
                    FOREIGN KEY(datastore_id) REFERENCES datastores (id) ON DELETE CASCADE
                );
            END IF;
        END$$;
        """
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
    op.execute("DROP TABLE IF EXISTS datastore_metrics_daily")
