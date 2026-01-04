"""notify datastore changed and recompute datastore metrics

Revision ID: b056acebf277
Revises: 0493e7285e06
Create Date: 2026-01-04 09:36:55.740126

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b056acebf277"
down_revision: Union[str, Sequence[str], None] = "0493e7285e06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) file trigger function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_datastore_files_changed()
        RETURNS trigger AS $$
        DECLARE
          dstore text;
          fid text;
        BEGIN
          IF TG_OP = 'INSERT' THEN
            dstore := NEW.datastore_id;
            fid := NEW.id;
          ELSIF TG_OP = 'DELETE' THEN
            dstore := OLD.datastore_id;
            fid := OLD.id;
          ELSE
            -- UPDATE
            -- If datastore_id changed, recompute both.
            IF NEW.datastore_id IS DISTINCT FROM OLD.datastore_id THEN
              PERFORM recompute_datastore_metrics(OLD.datastore_id);
              PERFORM recompute_datastore_metrics(NEW.datastore_id);

              PERFORM pg_notify(
                'datastore_changed',
                json_build_object(
                  'table', 'file',
                  'event_name', 'DATASTORE_FILES_CHANGED',
                  'operation', TG_OP,
                  'file_id', NEW.id,
                  'datastore_id', NEW.datastore_id,
                  'note', 'datastore_id_changed_recomputed_both'
                )::text
              );

              RETURN NEW;
            END IF;

            dstore := NEW.datastore_id;
            fid := NEW.id;
          END IF;

          PERFORM recompute_datastore_metrics(dstore);

          PERFORM pg_notify(
            'datastore_changed',
            json_build_object(
              'table', 'file',
              'event_name', 'DATASTORE_FILES_CHANGED',
              'operation', TG_OP,
              'file_id', fid,
              'datastore_id', dstore
            )::text
          );

          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 2) dataset trigger function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_datastore_datasets_changed()
        RETURNS trigger AS $$
        DECLARE
          dstore text;
          dsid text;
        BEGIN
          IF TG_OP = 'INSERT' THEN
            dstore := NEW.datastore_id;
            dsid := NEW.id;
          ELSIF TG_OP = 'DELETE' THEN
            dstore := OLD.datastore_id;
            dsid := OLD.id;
          ELSE
            -- UPDATE
            IF NEW.datastore_id IS DISTINCT FROM OLD.datastore_id THEN
              PERFORM recompute_datastore_metrics(OLD.datastore_id);
              PERFORM recompute_datastore_metrics(NEW.datastore_id);

              PERFORM pg_notify(
                'datastore_changed',
                json_build_object(
                  'table', 'dataset',
                  'event_name', 'DATASTORE_DATASETS_CHANGED',
                  'operation', TG_OP,
                  'dataset_id', NEW.id,
                  'datastore_id', NEW.datastore_id,
                  'note', 'datastore_id_changed_recomputed_both'
                )::text
              );

              RETURN NEW;
            END IF;

            dstore := NEW.datastore_id;
            dsid := NEW.id;
          END IF;

          PERFORM recompute_datastore_metrics(dstore);

          PERFORM pg_notify(
            'datastore_changed',
            json_build_object(
              'table', 'dataset',
              'event_name', 'DATASTORE_DATASETS_CHANGED',
              'operation', TG_OP,
              'dataset_id', dsid,
              'datastore_id', dstore
            )::text
          );

          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 3) project trigger function (projects are owned by datastore_id per your clarification)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_datastore_projects_changed()
        RETURNS trigger AS $$
        DECLARE
          dstore text;
          pid text;
        BEGIN
          IF TG_OP = 'INSERT' THEN
            dstore := NEW.datastore_id;
            pid := NEW.id;
          ELSIF TG_OP = 'DELETE' THEN
            dstore := OLD.datastore_id;
            pid := OLD.id;
          ELSE
            -- UPDATE
            IF NEW.datastore_id IS DISTINCT FROM OLD.datastore_id THEN
              PERFORM recompute_datastore_metrics(OLD.datastore_id);
              PERFORM recompute_datastore_metrics(NEW.datastore_id);

              PERFORM pg_notify(
                'datastore_changed',
                json_build_object(
                  'table', 'project',
                  'event_name', 'DATASTORE_PROJECTS_CHANGED',
                  'operation', TG_OP,
                  'project_id', NEW.id,
                  'datastore_id', NEW.datastore_id,
                  'note', 'datastore_id_changed_recomputed_both'
                )::text
              );

              RETURN NEW;
            END IF;

            dstore := NEW.datastore_id;
            pid := NEW.id;
          END IF;

          PERFORM recompute_datastore_metrics(dstore);

          PERFORM pg_notify(
            'datastore_changed',
            json_build_object(
              'table', 'project',
              'event_name', 'DATASTORE_PROJECTS_CHANGED',
              'operation', TG_OP,
              'project_id', pid,
              'datastore_id', dstore
            )::text
          );

          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 4) attach triggers
    op.execute(
        """
        -- file: recompute on upload/delete, and on size/datastore moves
        DROP TRIGGER IF EXISTS datastore_files_changed_trigger ON file;
        CREATE TRIGGER datastore_files_changed_trigger
        AFTER INSERT OR DELETE OR UPDATE OF size, datastore_id ON file
        FOR EACH ROW
        EXECUTE FUNCTION notify_datastore_files_changed();

        -- dataset: recompute on create/delete/move
        DROP TRIGGER IF EXISTS datastore_datasets_changed_trigger ON dataset;
        CREATE TRIGGER datastore_datasets_changed_trigger
        AFTER INSERT OR DELETE OR UPDATE OF datastore_id ON dataset
        FOR EACH ROW
        EXECUTE FUNCTION notify_datastore_datasets_changed();

        -- project: recompute on create/delete/move
        DROP TRIGGER IF EXISTS datastore_projects_changed_trigger ON project;
        CREATE TRIGGER datastore_projects_changed_trigger
        AFTER INSERT OR DELETE OR UPDATE OF datastore_id ON project
        FOR EACH ROW
        EXECUTE FUNCTION notify_datastore_projects_changed();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS datastore_files_changed_trigger ON file;
        DROP TRIGGER IF EXISTS datastore_datasets_changed_trigger ON dataset;
        DROP TRIGGER IF EXISTS datastore_projects_changed_trigger ON project;

        DROP FUNCTION IF EXISTS notify_datastore_projects_changed();
        DROP FUNCTION IF EXISTS notify_datastore_datasets_changed();
        DROP FUNCTION IF EXISTS notify_datastore_files_changed();
        """
    )
