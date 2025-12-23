"""Add dataset active_version and annotation dataset link

Revision ID: 6b0728a1d712
Revises: 79a3964fbdc1
Create Date: 2025-12-23 10:59:00.091070

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6b0728a1d712"
down_revision: Union[str, Sequence[str], None] = "79a3964fbdc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ─────────────────────────────────────────
    # dataset: add active_version_id
    # ─────────────────────────────────────────
    op.add_column(
        "dataset",
        sa.Column("active_version_id", sa.String(), nullable=True),
    )
    op.create_foreign_key(
        "fk_dataset_active_version",
        "dataset",
        "dataset_version",
        ["active_version_id"],
        ["id"],
    )

    # ─────────────────────────────────────────
    # annotation: add dataset_id
    # ─────────────────────────────────────────
    op.add_column(
        "annotation",
        sa.Column("dataset_id", sa.String(), nullable=True),
    )
    op.create_foreign_key(
        "fk_annotation_dataset",
        "annotation",
        "dataset",
        ["dataset_id"],
        ["id"],
    )


def downgrade():
    # Reverse changes

    # annotation
    op.drop_constraint("fk_annotation_dataset", "annotation", type_="foreignkey")
    op.drop_column("annotation", "dataset_id")

    # dataset
    op.drop_constraint("fk_dataset_active_version", "dataset", type_="foreignkey")
    op.drop_column("dataset", "active_version_id")
