"""backfill dataset_metrics

Revision ID: d8d86a9b8020
Revises: d359d2325573
Create Date: 2025-12-24 10:17:10.398064

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d8d86a9b8020"
down_revision: Union[str, Sequence[str], None] = "d359d2325573"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "backfill_dataset_metrics"
down_revision = "create_dataset_metrics_table"  # set to your actual revision id
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    dataset_ids = conn.execute(sa.text("SELECT id FROM datasets")).fetchall()

    for (dataset_id,) in dataset_ids:
        conn.execute(
            sa.text(
                """
                INSERT INTO dataset_metrics (
                    dataset_id,
                    file_count,
                    total_bytes,
                    project_usage_count,
                    version_count,
                    collaborator_count,
                    likes,
                    shares
                )
                VALUES (:id, 0, 0, 0, 0, 0, 0, 0)
                ON CONFLICT (dataset_id) DO NOTHING
                """
            ),
            {"id": str(dataset_id)},
        )


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM dataset_metrics"))
