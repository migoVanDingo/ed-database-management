"""create datastore_metrics table

Revision ID: d9712c3a7ba5
Revises: c644bb92027d
Create Date: 2025-12-24 10:10:13.981760

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = "d9712c3a7ba5"
down_revision: Union[str, Sequence[str], None] = "c644bb92027d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "datastore_metrics",
        sa.Column(
            "datastore_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datastores.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("file_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("dataset_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("project_count", sa.Integer(), nullable=False, server_default="0"),
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
    op.drop_table("datastore_metrics")
