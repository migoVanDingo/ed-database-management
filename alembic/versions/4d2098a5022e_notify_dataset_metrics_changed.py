"""notify dataset metrics changed

Revision ID: 4d2098a5022e
Revises: 77009547f802
Create Date: 2025-12-27 11:09:20.088704

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4d2098a5022e"
down_revision: Union[str, Sequence[str], None] = "77009547f802"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_dataset_metrics_changed()
        RETURNS trigger AS $$
        BEGIN
          IF TG_OP = 'UPDATE' THEN
            IF NEW.file_count IS DISTINCT FROM OLD.file_count
               OR NEW.total_bytes IS DISTINCT FROM OLD.total_bytes THEN
              PERFORM pg_notify(
                'dataset_metrics_changed',
                json_build_object(
                  'table', 'dataset_metrics',
                  'dataset_id', NEW.dataset_id,
                  'file_count', NEW.file_count,
                  'total_bytes', NEW.total_bytes,
                  'event_name', 'DATASET_METRICS_CHANGED',
                  'operation', TG_OP,
                  'updated_at', NEW.updated_at
                )::text
              );
            END IF;
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS dataset_metrics_changed_trigger ON dataset_metrics;
        CREATE TRIGGER dataset_metrics_changed_trigger
        AFTER UPDATE ON dataset_metrics
        FOR EACH ROW
        EXECUTE FUNCTION notify_dataset_metrics_changed();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS dataset_metrics_changed_trigger ON dataset_metrics;
        DROP FUNCTION IF EXISTS notify_dataset_metrics_changed();
        """
    )
