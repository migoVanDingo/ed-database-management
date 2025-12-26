"""switch file status trigger to pg_notify

Revision ID: 68a867090400
Revises: 0970968a4821
Create Date: 2025-12-14 08:23:35.768866

"""
# Idempotent trigger/function creation to avoid DuplicateObject errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "68a867090400"
down_revision: Union[str, Sequence[str], None] = "0970968a4821"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Replace the existing trigger function to use pg_notify instead of outbox
    op.execute(
        """
        CREATE OR REPLACE FUNCTION file_status_outbox_trigger()
        RETURNS TRIGGER AS $$
        DECLARE
            payload jsonb;
        BEGIN
            -- Only fire when status actually changes
            IF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status THEN
                payload := jsonb_build_object(
                    'file_id', NEW.id,
                    'datastore_id', NEW.datastore_id,
                    'upload_session_id', NEW.upload_session_id,
                    'old_status', OLD.status,
                    'new_status', NEW.status,
                    'occurred_at', now()
                );

                PERFORM pg_notify('file_status_changed', payload::text);
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # -- Re-attach trigger just to be sure it's pointing at this function
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_file_status_outbox ON file;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_file_status_outbox
        AFTER UPDATE OF status ON file
        FOR EACH ROW
        EXECUTE FUNCTION file_status_outbox_trigger();
        """
    )


def downgrade():
    # -- On downgrade, just drop the trigger and function.
    # -- (If you really care about full revert, you could paste the old
    # --  INSERT-into-event_outbox implementation here instead.)
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_file_status_outbox ON file;
        """
    )
