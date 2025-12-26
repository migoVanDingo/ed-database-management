"""add basemodel columns to dataset_item

Revision ID: cf7468594358
Revises: b2225ec62883
Create Date: 2025-12-26 09:44:28.237142

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cf7468594358"
down_revision: Union[str, Sequence[str], None] = "b2225ec62883"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add columns as nullable first to avoid issues if table already has rows
    op.add_column(
        "dataset_item", sa.Column("created_at", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "dataset_item", sa.Column("updated_at", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "dataset_item", sa.Column("deleted_at", sa.BigInteger(), nullable=True)
    )
    op.add_column("dataset_item", sa.Column("is_active", sa.Boolean(), nullable=True))

    # Backfill for existing rows (use epoch seconds)
    op.execute(
        "UPDATE dataset_item SET created_at = EXTRACT(EPOCH FROM NOW())::bigint WHERE created_at IS NULL;"
    )
    op.execute(
        "UPDATE dataset_item SET updated_at = EXTRACT(EPOCH FROM NOW())::bigint WHERE updated_at IS NULL;"
    )
    op.execute("UPDATE dataset_item SET is_active = TRUE WHERE is_active IS NULL;")

    # Enforce NOT NULL where your BaseModel expects it
    op.alter_column("dataset_item", "created_at", nullable=False)
    op.alter_column("dataset_item", "updated_at", nullable=False)
    op.alter_column("dataset_item", "is_active", nullable=False)


def downgrade():
    op.drop_column("dataset_item", "is_active")
    op.drop_column("dataset_item", "deleted_at")
    op.drop_column("dataset_item", "updated_at")
    op.drop_column("dataset_item", "created_at")
