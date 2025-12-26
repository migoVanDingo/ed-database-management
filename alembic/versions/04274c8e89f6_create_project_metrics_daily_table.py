"""create project_metrics_daily table

Revision ID: 04274c8e89f6
Revises: 2c19121d24ba
Create Date: 2025-12-24 10:20:47.862446

"""
# Idempotent table creation to avoid DuplicateTable errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "04274c8e89f6"
down_revision: Union[str, Sequence[str], None] = "2c19121d24ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'project_metrics_daily'
            ) THEN
                CREATE TABLE project_metrics_daily (
                    id UUID DEFAULT gen_random_uuid() NOT NULL,
                    project_id UUID NOT NULL,
                    day DATE NOT NULL,
                    dataset_count INTEGER DEFAULT '0' NOT NULL,
                    file_count BIGINT DEFAULT '0' NOT NULL,
                    total_bytes BIGINT DEFAULT '0' NOT NULL,
                    collaborator_count INTEGER DEFAULT '0' NOT NULL,
                    likes INTEGER DEFAULT '0' NOT NULL,
                    shares INTEGER DEFAULT '0' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (id),
                    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
                );
            END IF;
        END$$;
        """
    )

    op.create_unique_constraint(
        "uq_project_metrics_daily_project_day",
        "project_metrics_daily",
        ["project_id", "day"],
    )

    op.create_index(
        "ix_project_metrics_daily_project_day",
        "project_metrics_daily",
        ["project_id", "day"],
    )


def downgrade():
    op.drop_index(
        "ix_project_metrics_daily_project_day", table_name="project_metrics_daily"
    )
    op.drop_constraint(
        "uq_project_metrics_daily_project_day", "project_metrics_daily", type_="unique"
    )
    op.execute("DROP TABLE IF EXISTS project_metrics_daily")
