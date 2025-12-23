"""Add dataset_split_assignment table

Revision ID: 516e6e9acdc5
Revises: c0d32176f1a4
Create Date: 2025-12-23 11:49:38.047579

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "516e6e9acdc5"
down_revision: Union[str, Sequence[str], None] = "c0d32176f1a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Safety: if something created this table early (e.g. metadata.create_all),
    # drop it so we can recreate it under Alembic's control.
    op.execute("DROP TABLE IF EXISTS dataset_split_assignment CASCADE;")

    op.create_table(
        "dataset_split_assignment",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("dataset_version_id", sa.String(), nullable=False),
        sa.Column("dataset_item_id", sa.String(), nullable=False),
        sa.Column("split", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.id"],
        ),
        sa.ForeignKeyConstraint(
            ["dataset_item_id"],
            ["dataset_item.id"],
        ),
    )

    op.create_index(
        "ix_dataset_split_assignment_dataset_version_id",
        "dataset_split_assignment",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_dataset_split_assignment_dataset_item_id",
        "dataset_split_assignment",
        ["dataset_item_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_dataset_split_assignment_version_item",
        "dataset_split_assignment",
        ["dataset_version_id", "dataset_item_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_dataset_split_assignment_version_item",
        "dataset_split_assignment",
        type_="unique",
    )
    op.drop_index(
        "ix_dataset_split_assignment_dataset_item_id",
        table_name="dataset_split_assignment",
    )
    op.drop_index(
        "ix_dataset_split_assignment_dataset_version_id",
        table_name="dataset_split_assignment",
    )
    op.drop_table("dataset_split_assignment")
