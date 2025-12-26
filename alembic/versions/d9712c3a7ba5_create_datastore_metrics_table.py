"""create datastore_metrics table

Revision ID: d9712c3a7ba5
Revises: c644bb92027d
Create Date: 2025-12-24 10:10:13.981760

"""
# Idempotent table creation to avoid DuplicateTable errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = "d9712c3a7ba5"
down_revision: Union[str, Sequence[str], None] = "c644bb92027d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'datastore_metrics'
            ) THEN
                CREATE TABLE datastore_metrics (
                    datastore_id UUID NOT NULL,
                    file_count BIGINT DEFAULT '0' NOT NULL,
                    total_bytes BIGINT DEFAULT '0' NOT NULL,
                    dataset_count INTEGER DEFAULT '0' NOT NULL,
                    project_count INTEGER DEFAULT '0' NOT NULL,
                    likes INTEGER DEFAULT '0' NOT NULL,
                    shares INTEGER DEFAULT '0' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (datastore_id),
                    FOREIGN KEY(datastore_id) REFERENCES datastores (id) ON DELETE CASCADE
                );
            END IF;
        END$$;
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS datastore_metrics")
