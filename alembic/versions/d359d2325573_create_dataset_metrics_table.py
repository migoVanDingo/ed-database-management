"""create dataset_metrics table

Revision ID: d359d2325573
Revises: 82929dcabd99
Create Date: 2025-12-24 10:16:34.978193

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d359d2325573"
down_revision: Union[str, Sequence[str], None] = "82929dcabd99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "dataset_metrics",
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("file_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "project_usage_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("version_count", sa.Integer(), nullable=False, server_default="0"),
        # 👇 new
        sa.Column(
            "collaborator_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade():
    op.drop_table("dataset_metrics")
