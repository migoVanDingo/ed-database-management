"""add capacity_bytes to datastore

Revision ID: 72cb4d53717c
Revises: f3ab62a67516
Create Date: 2025-12-07 08:02:49.457732

"""
# Idempotent column creation to avoid DuplicateColumn errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72cb4d53717c"
down_revision: Union[str, Sequence[str], None] = "f3ab62a67516"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'datastore'
                  AND column_name = 'capacity_bytes'
            ) THEN
                ALTER TABLE datastore
                ADD COLUMN capacity_bytes BIGINT DEFAULT 10737418240;
            END IF;
        END$$;
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'datastore'
                  AND column_name = 'capacity_bytes'
            ) THEN
                UPDATE datastore
                SET capacity_bytes = 10737418240
                WHERE capacity_bytes IS NULL;
            END IF;
        END$$;
        """
    )


def downgrade():
    op.drop_column("datastore", "capacity_bytes")
