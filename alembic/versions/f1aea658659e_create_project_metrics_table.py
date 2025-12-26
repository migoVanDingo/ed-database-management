"""create project_metrics table

Revision ID: f1aea658659e
Revises: d8d86a9b8020
Create Date: 2025-12-24 10:18:00.039785

"""
# Idempotent table creation to avoid DuplicateTable errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f1aea658659e"
down_revision: Union[str, Sequence[str], None] = "d8d86a9b8020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'project_metrics'
            ) THEN
                CREATE TABLE project_metrics (
                    project_id UUID NOT NULL,
                    dataset_count INTEGER DEFAULT '0' NOT NULL,
                    file_count BIGINT DEFAULT '0' NOT NULL,
                    total_bytes BIGINT DEFAULT '0' NOT NULL,
                    collaborator_count INTEGER DEFAULT '0' NOT NULL,
                    likes INTEGER DEFAULT '0' NOT NULL,
                    shares INTEGER DEFAULT '0' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (project_id),
                    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
                );
            END IF;
        END$$;
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS project_metrics")
