"""create dataset_metrics_daily table

Revision ID: 2c19121d24ba
Revises: e6e8da811b0d
Create Date: 2025-12-24 10:20:13.578574

"""
# Idempotent table creation to avoid DuplicateTable errors.

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
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'dataset_metrics_daily'
            ) THEN
                CREATE TABLE dataset_metrics_daily (
                    id UUID DEFAULT gen_random_uuid() NOT NULL,
                    dataset_id UUID NOT NULL,
                    day DATE NOT NULL,
                    file_count BIGINT DEFAULT '0' NOT NULL,
                    total_bytes BIGINT DEFAULT '0' NOT NULL,
                    project_usage_count INTEGER DEFAULT '0' NOT NULL,
                    version_count INTEGER DEFAULT '0' NOT NULL,
                    collaborator_count INTEGER DEFAULT '0' NOT NULL,
                    likes INTEGER DEFAULT '0' NOT NULL,
                    shares INTEGER DEFAULT '0' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (id),
                    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
                );
            END IF;
        END$$;
        """
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
    op.execute("DROP TABLE IF EXISTS dataset_metrics_daily")
