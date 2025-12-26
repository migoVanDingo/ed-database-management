"""add event_outbox table and file status trigger

Revision ID: 0970968a4821
Revises: 12cde9649f8c
Create Date: 2025-12-14 08:03:35.063535

"""
# Idempotent trigger/function creation to avoid DuplicateObject errors.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0970968a4821"
down_revision: Union[str, Sequence[str], None] = "12cde9649f8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ─────────────────────────────────────────
    # 1) event_outbox table
    # ─────────────────────────────────────────
    # If you already have an outbox table, skip this block and just keep the trigger parts.
    op.create_table(
        "event_outbox",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("datastore_id", sa.String(length=64), nullable=True),
        sa.Column("upload_session_id", sa.String(length=64), nullable=True),
        sa.Column("old_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_event_outbox_processed_at",
        "event_outbox",
        ["processed_at"],
    )
    op.create_index(
        "ix_event_outbox_entity_type_entity_id",
        "event_outbox",
        ["entity_type", "entity_id"],
    )

    # ─────────────────────────────────────────
    # 2) Trigger function on file table
    # ─────────────────────────────────────────
    # NOTE: if your column names differ (e.g. size_bytes instead of size),
    # update the JSONB build accordingly.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION file_status_outbox_trigger()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Only fire when status actually changes
            IF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status THEN
                INSERT INTO event_outbox (
                    entity_type,
                    entity_id,
                    datastore_id,
                    upload_session_id,
                    old_status,
                    new_status,
                    payload,
                    occurred_at
                )
                VALUES (
                    'file',
                    NEW.id,
                    NEW.datastore_id,
                    NEW.upload_session_id,
                    OLD.status,
                    NEW.status,
                    jsonb_build_object(
                        'bucket', NEW.bucket,
                        'object_key', NEW.object_key,
                        -- change "size" to "size_bytes" or whatever your column is
                        'size_bytes', NEW.size,
                        'content_type', NEW.content_type
                    ),
                    now()
                );
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # ─────────────────────────────────────────
    # 3) Attach trigger to file table
    # ─────────────────────────────────────────
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
    # Remove trigger + function first
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_file_status_outbox ON file;
        DROP FUNCTION IF EXISTS file_status_outbox_trigger();
        """
    )

    # Drop indexes + table (if you didn't already have it)
    op.drop_index("ix_event_outbox_entity_type_entity_id", table_name="event_outbox")
    op.drop_index("ix_event_outbox_processed_at", table_name="event_outbox")
    op.drop_table("event_outbox")
