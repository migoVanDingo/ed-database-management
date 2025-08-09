"""Add user table trigger

Revision ID: 39f67eb944ff
Revises:
Create Date: 2025-08-03 10:48:14.017600

"""

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

        CREATE TRIGGER user_notify_trigger
        AFTER INSERT OR UPDATE OR DELETE ON "user"
        FOR EACH ROW
        EXECUTE FUNCTION notify_user_change();
    """
    )


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS user_notify_trigger ON "user";')
    op.execute("DROP FUNCTION IF EXISTS notify_user_change();")
