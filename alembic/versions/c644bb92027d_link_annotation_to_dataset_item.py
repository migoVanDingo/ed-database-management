"""Link annotation to dataset_item

Revision ID: c644bb92027d
Revises: 62559db29ad8
Create Date: 2025-12-23 11:52:00.766386

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c644bb92027d"
down_revision: Union[str, Sequence[str], None] = "62559db29ad8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add dataset_item_id column to annotation
    op.add_column(
        "annotation",
        sa.Column("dataset_item_id", sa.String(), nullable=True),
    )

    op.create_foreign_key(
        "fk_annotation_dataset_item",
        "annotation",
        "dataset_item",
        ["dataset_item_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_annotation_dataset_item",
        "annotation",
        type_="foreignkey",
    )
    op.drop_column("annotation", "dataset_item_id")
