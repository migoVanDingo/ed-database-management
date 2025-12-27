"""notify dataset files changed and recompute dataset metrics

Revision ID: 77009547f802
Revises: f442ef3ceae1
Create Date: 2025-12-27 11:08:48.292259

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "77009547f802"
down_revision: Union[str, Sequence[str], None] = "f442ef3ceae1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) recompute function
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

    # 2) notify trigger
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_dataset_files_changed()
        RETURNS trigger AS $$
        DECLARE
          dsid text;
          fid text;
          role_val text;
          dstore text;
        BEGIN
          IF TG_OP = 'INSERT' THEN
            dsid := NEW.dataset_id;
            fid := NEW.file_id;
            role_val := NEW.role;
          ELSE
            dsid := OLD.dataset_id;
            fid := OLD.file_id;
            role_val := OLD.role;
          END IF;

          -- recompute metrics inside same transaction
          PERFORM recompute_dataset_metrics(dsid);

          -- attach datastore_id for convenience
          SELECT datastore_id INTO dstore FROM dataset WHERE id = dsid;

          PERFORM pg_notify(
            'dataset_files_changed',
            json_build_object(
              'table', 'dataset_file_link',
              'dataset_id', dsid,
              'file_id', fid,
              'role', role_val,
              'datastore_id', dstore,
              'event_name', 'DATASET_FILES_CHANGED',
              'operation', TG_OP
            )::text
          );

          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 3) attach trigger
    op.execute(
        """
        DROP TRIGGER IF EXISTS dataset_files_changed_trigger ON dataset_file_link;
        CREATE TRIGGER dataset_files_changed_trigger
        AFTER INSERT OR DELETE ON dataset_file_link
        FOR EACH ROW
        EXECUTE FUNCTION notify_dataset_files_changed();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS dataset_files_changed_trigger ON dataset_file_link;
        DROP FUNCTION IF EXISTS notify_dataset_files_changed();
        DROP FUNCTION IF EXISTS recompute_dataset_metrics(text);
        """
    )
