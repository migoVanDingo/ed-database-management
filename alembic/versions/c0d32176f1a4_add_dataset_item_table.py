"""Add dataset_item table

Revision ID: c0d32176f1a4
Revises: 5eeaf36b2fc3
Create Date: 2025-12-23 11:47:20.651037

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c0d32176f1a4"
down_revision: Union[str, Sequence[str], None] = "5eeaf36b2fc3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Safety: if something (like metadata.create_all) created this table early,
    # drop it so we can recreate it in a controlled way.
    op.execute("DROP TABLE IF EXISTS dataset_item CASCADE;")

    op.create_table(
        "dataset_item",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("dataset_id", sa.String(), nullable=False),
        sa.Column("dataset_version_id", sa.String(), nullable=True),
        sa.Column("file_id", sa.String(), nullable=False),
        sa.Column("external_item_key", sa.String(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="raw",
        ),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_version.id"]),
        sa.ForeignKeyConstraint(["file_id"], ["file.id"]),
    )

    op.create_index(
        "ix_dataset_item_dataset_id",
        "dataset_item",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_dataset_item_dataset_version_id",
        "dataset_item",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_dataset_item_file_id",
        "dataset_item",
        ["file_id"],
        unique=False,
    )
    op.create_index(
        "ix_dataset_item_dataset_external_key",
        "dataset_item",
        ["dataset_id", "external_item_key"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_dataset_item_dataset_external_key",
        table_name="dataset_item",
    )
    op.drop_index(
        "ix_dataset_item_file_id",
        table_name="dataset_item",
    )
    op.drop_index(
        "ix_dataset_item_dataset_version_id",
        table_name="dataset_item",
    )
    op.drop_index(
        "ix_dataset_item_dataset_id",
        table_name="dataset_item",
    )
    op.drop_table("dataset_item")
