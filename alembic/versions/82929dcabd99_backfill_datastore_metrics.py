"""backfill datastore_metrics

Revision ID: 82929dcabd99
Revises: d9712c3a7ba5
Create Date: 2025-12-24 10:12:48.108153

"""
# Idempotent backfill to avoid errors when tables are missing.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "82929dcabd99"
down_revision: Union[str, Sequence[str], None] = "d9712c3a7ba5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Use a connection to execute raw SQL
    conn = op.get_bind()

    table_exists = conn.execute(
        sa.text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'datastores'
            """
        )
    ).first()
    if not table_exists:
        return

    # Fetch all datastore IDs
    datastore_ids = conn.execute(sa.text("SELECT id FROM datastores")).fetchall()

    for (datastore_id,) in datastore_ids:
        # Insert a metrics row only if it doesn't already exist
        conn.execute(
            sa.text(
                """
                INSERT INTO datastore_metrics (datastore_id, file_count, total_bytes, dataset_count, project_count, likes, shares)
                VALUES (:id, 0, 0, 0, 0, 0, 0)
                ON CONFLICT (datastore_id) DO NOTHING
                """
            ),
            {"id": str(datastore_id)},
        )


def downgrade():
    # Delete all metrics rows — safe because they can be regenerated
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM datastore_metrics"))
