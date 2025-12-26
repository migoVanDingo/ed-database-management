"""Add user table trigger

Revision ID: 39f67eb944ff
Revises:
Create Date: 2025-08-03 10:48:14.017600

"""
# Idempotent trigger/function creation to avoid DuplicateObject errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "39f67eb944ff"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_user_change() RETURNS trigger AS $$
        DECLARE
            payload JSON;
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                payload := json_build_object(
                    'operation', TG_OP,
                    'table', TG_TABLE_NAME,
                    'data', NULL,
                    'old_data', row_to_json(OLD)
                );
            ELSIF (TG_OP = 'UPDATE') THEN
                payload := json_build_object(
                    'operation', TG_OP,
                    'table', TG_TABLE_NAME,
                    'data', row_to_json(NEW),
                    'old_data', row_to_json(OLD)
                );
            ELSE
                payload := json_build_object(
                    'operation', TG_OP,
                    'table', TG_TABLE_NAME,
                    'data', row_to_json(NEW),
                    'old_data', NULL
                );
            END IF;

            PERFORM pg_notify('user_changes', payload::text);
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS user_notify_trigger ON "user";
        CREATE TRIGGER user_notify_trigger
        AFTER INSERT OR UPDATE OR DELETE ON "user"
        FOR EACH ROW
        EXECUTE FUNCTION notify_user_change();
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION notify_user_verified() RETURNS trigger AS $$
        DECLARE
            payload JSON;
        BEGIN
            IF (NEW.is_verified = TRUE AND (OLD.is_verified IS DISTINCT FROM TRUE)) THEN
                payload := json_build_object(
                    'operation', TG_OP,
                    'event_name', 'USER_VERIFIED',
                    'table', TG_TABLE_NAME,
                    'data', row_to_json(NEW),
                    'old_data', row_to_json(OLD)
                );

                PERFORM pg_notify('user_changes', payload::text);
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS user_verified_notify_trigger ON "user";
        CREATE TRIGGER user_verified_notify_trigger
        AFTER UPDATE OF is_verified ON "user"
        FOR EACH ROW
        WHEN (OLD.is_verified IS DISTINCT FROM NEW.is_verified AND NEW.is_verified = TRUE)
        EXECUTE FUNCTION notify_user_verified();
        """
    )


def downgrade():
    op.execute(
        'DROP TRIGGER IF EXISTS user_verified_notify_trigger ON "user";'
    )
    op.execute("DROP FUNCTION IF EXISTS notify_user_verified();")
    op.execute('DROP TRIGGER IF EXISTS user_notify_trigger ON "user";')
    op.execute("DROP FUNCTION IF EXISTS notify_user_change();")
