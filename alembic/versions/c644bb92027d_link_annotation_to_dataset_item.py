"""Link annotation to dataset_item

Revision ID: c644bb92027d
Revises: 62559db29ad8
Create Date: 2025-12-23 11:52:00.766386

"""
# Idempotent column/constraint creation to avoid DuplicateColumn errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c644bb92027d"
down_revision: Union[str, Sequence[str], None] = "62559db29ad8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add dataset_item_id column to annotation
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'annotation'
                  AND column_name = 'dataset_item_id'
            ) THEN
                ALTER TABLE annotation ADD COLUMN dataset_item_id VARCHAR;
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
                  AND tc.constraint_name = 'fk_annotation_dataset_item'
                  AND tc.table_name = 'annotation'
            ) THEN
                ALTER TABLE annotation
                ADD CONSTRAINT fk_annotation_dataset_item
                FOREIGN KEY (dataset_item_id)
                REFERENCES dataset_item (id);
            END IF;
        END$$;
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE annotation
        DROP CONSTRAINT IF EXISTS fk_annotation_dataset_item;
        """
    )
    op.execute(
        """
        ALTER TABLE annotation
        DROP COLUMN IF EXISTS dataset_item_id;
        """
    )
