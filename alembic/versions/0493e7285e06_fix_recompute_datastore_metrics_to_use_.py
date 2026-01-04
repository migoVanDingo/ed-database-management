"""fix recompute_datastore_metrics to use owned dataset/project counts

Revision ID: 0493e7285e06
Revises: 099dc6881eb1
Create Date: 2026-01-04 09:35:06.108504

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0493e7285e06"
down_revision: Union[str, Sequence[str], None] = "099dc6881eb1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION recompute_datastore_metrics(p_datastore_id text)
        RETURNS void AS $$
        BEGIN
          INSERT INTO datastore_metrics (
            datastore_id,
            file_count,
            total_bytes,
            dataset_count,
            project_count,
            likes,
            shares,
            created_at,
            updated_at
          )
          SELECT
            p_datastore_id,

            -- files owned by datastore
            (SELECT COUNT(*) FROM file f WHERE f.datastore_id = p_datastore_id) AS file_count,
            (SELECT COALESCE(SUM(f.size), 0) FROM file f WHERE f.datastore_id = p_datastore_id) AS total_bytes,

            -- datasets owned by datastore
            (SELECT COUNT(*) FROM dataset d WHERE d.datastore_id = p_datastore_id) AS dataset_count,

            -- projects owned by datastore
            (SELECT COUNT(*) FROM project p WHERE p.datastore_id = p_datastore_id) AS project_count,

            -- only used on first insert; on conflict we do NOT overwrite likes/shares
            0 AS likes,
            0 AS shares,
            NOW() AS created_at,
            NOW() AS updated_at

          ON CONFLICT (datastore_id)
          DO UPDATE SET
            file_count = EXCLUDED.file_count,
            total_bytes = EXCLUDED.total_bytes,
            dataset_count = EXCLUDED.dataset_count,
            project_count = EXCLUDED.project_count,
            updated_at = NOW();
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    # revert to previous definition (the join-based version from 099dc6881eb1)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION recompute_datastore_metrics(p_datastore_id text)
        RETURNS void AS $$
        BEGIN
          INSERT INTO datastore_metrics (
            datastore_id,
            file_count,
            total_bytes,
            dataset_count,
            project_count,
            likes,
            shares,
            created_at,
            updated_at
          )
          SELECT
            p_datastore_id,

            -- files
            COUNT(DISTINCT f.id) AS file_count,
            COALESCE(SUM(f.size), 0) AS total_bytes,

            -- datasets
            COUNT(DISTINCT dfl.dataset_id) AS dataset_count,

            -- projects
            COUNT(DISTINCT pdl.project_id) AS project_count,

            0 AS likes,
            0 AS shares,
            NOW() AS created_at,
            NOW() AS updated_at
          FROM file f
          LEFT JOIN dataset_file_link dfl
            ON dfl.file_id = f.id
          LEFT JOIN project_dataset_link pdl
            ON pdl.dataset_id = dfl.dataset_id
          WHERE f.datastore_id = p_datastore_id

          ON CONFLICT (datastore_id)
          DO UPDATE SET
            file_count = EXCLUDED.file_count,
            total_bytes = EXCLUDED.total_bytes,
            dataset_count = EXCLUDED.dataset_count,
            project_count = EXCLUDED.project_count,
            updated_at = NOW();
        END;
        $$ LANGUAGE plpgsql;
        """
    )
