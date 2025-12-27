"""fix recompute_dataset_metrics timestamps

Revision ID: b1e25e4c8a0b
Revises: c945bdb585a8
Create Date: 2025-12-27 11:27:23.895564

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "b1e25e4c8a0b"
down_revision: Union[str, Sequence[str], None] = "c945bdb585a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION recompute_dataset_metrics(p_dataset_id text)
        RETURNS void AS $$
        BEGIN
          INSERT INTO dataset_metrics (
            dataset_id,
            file_count,
            total_bytes,
            created_at,
            updated_at
          )
          SELECT
            p_dataset_id,
            COUNT(DISTINCT dfl.file_id) AS file_count,
            COALESCE(SUM(f.size), 0) AS total_bytes,
            NOW() AS created_at,
            NOW() AS updated_at
          FROM dataset_file_link dfl
          JOIN file f ON f.id = dfl.file_id
          WHERE dfl.dataset_id = p_dataset_id
            AND (dfl.role IS NULL OR dfl.role = 'input')
          ON CONFLICT (dataset_id)
          DO UPDATE SET
            file_count = EXCLUDED.file_count,
            total_bytes = EXCLUDED.total_bytes,
            updated_at = NOW();
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    # revert to the older definition (no created_at, and updated_at from EXCLUDED)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION recompute_dataset_metrics(p_dataset_id text)
        RETURNS void AS $$
        BEGIN
          INSERT INTO dataset_metrics (dataset_id, file_count, total_bytes, updated_at)
          SELECT
            p_dataset_id,
            COUNT(DISTINCT dfl.file_id) AS file_count,
            COALESCE(SUM(f.size), 0) AS total_bytes,
            NOW()
          FROM dataset_file_link dfl
          JOIN file f ON f.id = dfl.file_id
          WHERE dfl.dataset_id = p_dataset_id
            AND (dfl.role IS NULL OR dfl.role = 'input')
          ON CONFLICT (dataset_id)
          DO UPDATE SET
            file_count = EXCLUDED.file_count,
            total_bytes = EXCLUDED.total_bytes,
            updated_at = EXCLUDED.updated_at;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
