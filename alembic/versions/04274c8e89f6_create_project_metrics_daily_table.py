"""create project_metrics_daily table

Revision ID: 04274c8e89f6
Revises: 2c19121d24ba
Create Date: 2025-12-24 10:20:47.862446

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "04274c8e89f6"
down_revision: Union[str, Sequence[str], None] = "2c19121d24ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "project_metrics_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("dataset_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("file_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.BigInteger(), nullable=False, server_default="0"),
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
    )

    op.create_unique_constraint(
        "uq_project_metrics_daily_project_day",
        "project_metrics_daily",
        ["project_id", "day"],
    )

    op.create_index(
        "ix_project_metrics_daily_project_day",
        "project_metrics_daily",
        ["project_id", "day"],
    )


def downgrade():
    op.drop_index(
        "ix_project_metrics_daily_project_day", table_name="project_metrics_daily"
    )
    op.drop_constraint(
        "uq_project_metrics_daily_project_day", "project_metrics_daily", type_="unique"
    )
    op.drop_table("project_metrics_daily")
