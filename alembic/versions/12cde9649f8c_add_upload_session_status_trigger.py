"""add upload_session status trigger

Revision ID: 12cde9649f8c
Revises: 67f7c0b6a3f8
Create Date: 2025-12-09 19:08:10.051416

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "12cde9649f8c"
down_revision: Union[str, Sequence[str], None] = "67f7c0b6a3f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Trigger function: notify when upload_session.status becomes 'ready'
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_upload_session_status_change()
        RETURNS trigger AS $$
        BEGIN
          -- Only act on UPDATE where status actually changed and is now 'ready'
          IF TG_OP = 'UPDATE'
             AND NEW.status IS DISTINCT FROM OLD.status
             AND NEW.status = 'ready' THEN

            PERFORM pg_notify(
              'upload_session_status_changed',
              json_build_object(
                'table', 'upload_session',
                'id', NEW.id,
                'datastore_id', NEW.datastore_id,
                'status', NEW.status,
                'error', NEW.error,
                'tags', NEW.tags,
                'created_at', NEW.created_at,
                'updated_at', NEW.updated_at,
                'event_name', 'UPLOAD_SESSION_STATUS_CHANGED',
                'operation', TG_OP
                )::text
            );
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 2) Trigger: call the function after any UPDATE of status on upload_session
    op.execute(
        """
        DROP TRIGGER IF EXISTS upload_session_status_trigger ON upload_session;
        CREATE TRIGGER upload_session_status_trigger
        AFTER UPDATE OF status ON upload_session
        FOR EACH ROW
        EXECUTE FUNCTION notify_upload_session_status_change();
        """
    )


def downgrade() -> None:
    # Remove trigger and function
    op.execute(
        """
        DROP TRIGGER IF EXISTS upload_session_status_trigger ON upload_session;
        DROP FUNCTION IF EXISTS notify_upload_session_status_change();
        """
    )
