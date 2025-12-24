"""create project_metrics table

Revision ID: f1aea658659e
Revises: d8d86a9b8020
Create Date: 2025-12-24 10:18:00.039785

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f1aea658659e"
down_revision: Union[str, Sequence[str], None] = "d8d86a9b8020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "project_metrics",
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        # Core counts
        sa.Column("dataset_count", sa.Integer(), nullable=False, server_default="0"),
        # Optional rollups (keep now; you can decide later whether to actively maintain these)
        sa.Column("file_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        # 👇 collaborator stats
        sa.Column(
            "collaborator_count", sa.Integer(), nullable=False, server_default="0"
        ),
        # Social
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        # Timestamps
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
    op.drop_table("project_metrics")
