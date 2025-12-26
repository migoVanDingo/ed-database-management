"""backfill project_metrics

Revision ID: c9d34733a311
Revises: f1aea658659e
Create Date: 2025-12-24 10:18:27.617341

"""
# Idempotent backfill to avoid errors when tables are missing.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9d34733a311"
down_revision: Union[str, Sequence[str], None] = "f1aea658659e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()

    table_exists = conn.execute(
        sa.text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'projects'
            """
        )
    ).first()
    if not table_exists:
        return

    project_ids = conn.execute(sa.text("SELECT id FROM projects")).fetchall()

    for (project_id,) in project_ids:
        conn.execute(
            sa.text(
                """
                INSERT INTO project_metrics (
                    project_id,
                    dataset_count,
                    file_count,
                    total_bytes,
                    collaborator_count,
                    likes,
                    shares
                )
                VALUES (:id, 0, 0, 0, 0, 0, 0)
                ON CONFLICT (project_id) DO NOTHING
                """
            ),
            {"id": str(project_id)},
        )


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM project_metrics"))
