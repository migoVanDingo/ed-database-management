"""add user verified trigger

Revision ID: 6a0ec1b19c59
Revises: 39f67eb944ff
Create Date: 2025-11-07 21:02:46.113338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a0ec1b19c59'
down_revision: Union[str, Sequence[str], None] = '39f67eb944ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
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

        CREATE TRIGGER user_verified_notify_trigger
        AFTER UPDATE OF is_verified ON "user"
        FOR EACH ROW
        WHEN (OLD.is_verified IS DISTINCT FROM NEW.is_verified AND NEW.is_verified = TRUE)
        EXECUTE FUNCTION notify_user_verified();
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TRIGGER IF EXISTS user_verified_notify_trigger ON "user";
        DROP FUNCTION IF EXISTS notify_user_verified();
        """
    )
