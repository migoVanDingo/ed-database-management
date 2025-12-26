"""Add dataset active_version and annotation dataset link

Revision ID: 6b0728a1d712
Revises: 79a3964fbdc1
Create Date: 2025-12-23 10:59:00.091070

"""
# Idempotent column/constraint creation to avoid DuplicateColumn errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6b0728a1d712"
down_revision: Union[str, Sequence[str], None] = "79a3964fbdc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ─────────────────────────────────────────
    # dataset: add active_version_id
    # ─────────────────────────────────────────
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'dataset'
                  AND column_name = 'active_version_id'
            ) THEN
                ALTER TABLE dataset ADD COLUMN active_version_id VARCHAR;
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.constraint_name = 'fk_dataset_active_version'
                  AND tc.table_name = 'dataset'
            ) THEN
                ALTER TABLE dataset
                ADD CONSTRAINT fk_dataset_active_version
                FOREIGN KEY (active_version_id)
                REFERENCES dataset_version (id);
            END IF;
        END$$;
        """
    )

    # ─────────────────────────────────────────
    # annotation: add dataset_id
    # ─────────────────────────────────────────
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'annotation'
                  AND column_name = 'dataset_id'
            ) THEN
                ALTER TABLE annotation ADD COLUMN dataset_id VARCHAR;
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.constraint_name = 'fk_annotation_dataset'
                  AND tc.table_name = 'annotation'
            ) THEN
                ALTER TABLE annotation
                ADD CONSTRAINT fk_annotation_dataset
                FOREIGN KEY (dataset_id)
                REFERENCES dataset (id);
            END IF;
        END$$;
        """
    )


def downgrade():
    # Reverse changes

    # annotation
    op.execute(
        """
        ALTER TABLE annotation
        DROP CONSTRAINT IF EXISTS fk_annotation_dataset;
        """
    )
    op.execute(
        """
        ALTER TABLE annotation
        DROP COLUMN IF EXISTS dataset_id;
        """
    )

    # dataset
    op.execute(
        """
        ALTER TABLE dataset
        DROP CONSTRAINT IF EXISTS fk_dataset_active_version;
        """
    )
    op.execute(
        """
        ALTER TABLE dataset
        DROP COLUMN IF EXISTS active_version_id;
        """
    )
